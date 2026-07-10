"""linkedin-token.py — get a fresh LinkedIn access token via OAuth (browser flow).

Usage:
  python scripts/linkedin-token.py

Prompts for the LinkedIn app Client ID + Client Secret, opens the browser,
the profile owner logs in and authorizes, and the script prints:

  LINKEDIN_ACCESS_TOKEN=...
  LINKEDIN_PERSON_URN=urn:li:person:...

The app must have http://localhost:8912/callback registered as a redirect URL
(App → Auth tab → OAuth 2.0 settings → Authorized redirect URLs).
"""

from __future__ import annotations
import argparse
import http.server
import subprocess
import threading
import urllib.parse
import webbrowser

import requests

REPO = "luislunar/Linked-Content-Generator"
PORT = 8912
REDIRECT_URI = f"http://localhost:{PORT}/callback"
SCOPE = "openid profile w_member_social"

result: dict = {}


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        result.update({k: v[0] for k, v in qs.items()})
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        if "code" in result:
            msg = "Listo. Ya puedes cerrar esta pestaña y volver a la terminal."
        else:
            msg = f"Error de LinkedIn: {result.get('error_description', result.get('error', 'desconocido'))}"
        self.wfile.write(f"<h2>{msg}</h2>".encode())

    def log_message(self, *args):
        pass


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--secret-suffix", default="",
                    help='p.ej. "_WILLIAM" guarda en LINKEDIN_ACCESS_TOKEN_WILLIAM')
    args = ap.parse_args()

    client_id = input("Client ID de la app de LinkedIn: ").strip()
    client_secret = input("Client Secret: ").strip()

    server = http.server.HTTPServer(("localhost", PORT), Handler)
    threading.Thread(target=server.handle_request, daemon=True).start()

    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization?"
        + urllib.parse.urlencode(
            {
                "response_type": "code",
                "client_id": client_id,
                "redirect_uri": REDIRECT_URI,
                "scope": SCOPE,
            }
        )
    )
    print("\nAbriendo el navegador... inicia sesión con la cuenta de LinkedIn del perfil que va a publicar.")
    print(f"Si no se abre solo, copia esta URL:\n{auth_url}\n")
    webbrowser.open(auth_url)

    while "code" not in result and "error" not in result:
        pass
    server.server_close()

    if "error" in result:
        print(f"\nERROR: {result.get('error_description', result['error'])}")
        return

    r = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "authorization_code",
            "code": result["code"],
            "redirect_uri": REDIRECT_URI,
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=30,
    )
    if r.status_code >= 400:
        print(f"\nERROR al canjear el token ({r.status_code}): {r.text}")
        return
    token = r.json()["access_token"]
    expires_days = r.json().get("expires_in", 0) // 86400

    person_urn = ""
    person_name = ""
    u = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    if u.status_code < 400:
        person_urn = f"urn:li:person:{u.json()['sub']}"
        person_name = u.json().get("name", "")

    print(f"\nToken verificado ✓  Perfil: {person_name or '(nombre no disponible)'}")
    print(f"El token caduca en {expires_days} días.")

    token_secret = f"LINKEDIN_ACCESS_TOKEN{args.secret_suffix}"
    urn_secret = f"LINKEDIN_PERSON_URN{args.secret_suffix}"
    print(f"\nGuardando {token_secret} en GitHub ({REPO})...")
    subprocess.run(["gh", "secret", "set", token_secret, "-R", REPO],
                   input=token, text=True, check=True)
    if person_urn:
        print(f"Guardando {urn_secret}...")
        subprocess.run(["gh", "secret", "set", urn_secret, "-R", REPO],
                       input=person_urn, text=True, check=True)
    print("\nTodo guardado ✓  No hace falta copiar nada.")


if __name__ == "__main__":
    main()
