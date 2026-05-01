# Setup guide

Click-by-click setup for the three external systems this repo talks to: **Notion**, **Blotato**, and **GitHub Actions secrets**. Budget ~30 minutes for everything.

---

## 1. Notion — integration token + 3 databases

### 1a. Create a Notion integration (1 minute)

1. Go to https://www.notion.so/profile/integrations
2. Click **"+ New integration"**
3. Name: `Linked-Content-Generator`. Associated workspace: Josh's workspace (or yours if that's where we'll house these DBs).
4. Type: **Internal**. Capabilities: leave **Read**, **Update**, **Insert content** checked. No comment permission needed.
5. Click **Save**.
6. On the next screen, copy the **Internal Integration Token** (starts with `secret_` or `ntn_`). This is `NOTION_TOKEN`.

### 1b. Create a parent page the integration can access (2 minutes)

1. In Notion, create a new page anywhere. Title it **"Linked Content Generator"**.
2. Click the **⋯** menu (top-right) → **Connections → Connect to** → pick `Linked-Content-Generator`.
3. Copy the page URL. You won't need it directly — the integration uses it as a parent for the databases we create.

### 1c. Let me create the 3 databases via API

When you give me `NOTION_TOKEN` and that parent page URL, I'll run a one-shot script that creates:

- **Posts DB** — one row per LinkedIn post, with engagement formula column
- **Magnets DB** — one row per lead magnet
- **Experiments DB** — one row per autoresearch experiment

I'll print the 3 database IDs. Those become:

```
NOTION_POSTS_DB_ID=<uuid>
NOTION_MAGNETS_DB_ID=<uuid>
NOTION_EXPERIMENTS_DB_ID=<uuid>
```

(We'll also enable **public page share** on magnet pages so LinkedIn viewers can open the link without a Notion account.)

---

## 2. Blotato — API key + LinkedIn account ID

### 2a. Sign up for Blotato (5 minutes)

1. Go to https://www.blotato.com and sign up (or log in if Josh already has an account).
2. Choose the plan that includes API access — this is usually the paid tier. (Free trials may or may not include API — check their pricing page.)
3. In the Blotato dashboard, click **"Connect accounts"** or **"Social accounts"** and connect **LinkedIn** — this is the OAuth handoff Blotato does on our behalf, so we never touch LinkedIn's API directly.
4. Once LinkedIn shows as "connected," take note of the account identifier. It's usually shown in the account card or a settings page. This is `BLOTATO_LINKEDIN_ACCOUNT_ID`.

### 2b. Get the API key (1 minute)

1. In Blotato dashboard → **Settings → API** (or **Integrations → Developer**, wording varies).
2. Generate a new API key. Copy it. This is `BLOTATO_API_KEY`.
3. Confirm the API base URL from their docs (should be something like `https://backend.blotato.com/v2`). If it differs from the default in our scripts, set `BLOTATO_API_BASE` as well.

### 2c. Verify with a test call

```bash
# local terminal, with .env filled in
source .env  # (shell-friendly env file)
curl -H "blotato-api-key: $BLOTATO_API_KEY" "$BLOTATO_API_BASE/accounts"
```

If you get a JSON list back with a LinkedIn account in it — you're good.

---

## 3. GitHub — make the repo + add secrets

### 3a. Push the repo

1. Create the repo on GitHub if it doesn't exist yet: https://github.com/new → name it `Linked-Content-Generator`, owner `luislunar`, **Public** (matches the font decision — we're using Montserrat, not Gotham).
2. When I confirm you're ready, I'll run:
   ```
   git add .
   git commit -m "feat: initial scaffold"
   git push -u origin main
   ```

### 3b. Add repo secrets

Repo → **Settings → Secrets and variables → Actions → New repository secret**. Add each of these:

| Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Claude API key from https://console.anthropic.com |
| `NOTION_TOKEN` | From step 1a |
| `NOTION_POSTS_DB_ID` | From step 1c |
| `NOTION_MAGNETS_DB_ID` | From step 1c |
| `NOTION_EXPERIMENTS_DB_ID` | From step 1c |
| `BLOTATO_API_KEY` | From step 2b |
| `BLOTATO_LINKEDIN_ACCOUNT_ID` | From step 2a |

### 3c. Enable Actions

Repo → **Actions** tab → if prompted, click **"I understand my workflows, go ahead and enable them"**.

---

## 4. Local dev — optional but recommended

Install tools so you can run the daily generator locally and iterate on prompts without burning Actions minutes.

```bash
# macOS
brew install ffmpeg node python@3.12
npm install -g @anthropic-ai/claude-code

# in the repo
python3 -m venv .venv
source .venv/bin/activate
pip install requests
cd scripts && npm init -y && npm i playwright && npx playwright install chromium
```

Then copy env:

```bash
cp .env.example .env
# fill in all the values from steps 1–3
set -a && source .env && set +a
```

Run locally:

```bash
./scripts/run-claude.sh daily
```

This produces `drafts/<today>/` with magnet.md, post.md, post.meta.json, hypothesis.md — and creates the Notion rows — without publishing.

---

## 5. Video pipeline test (no Notion/Blotato needed)

We've seeded a dummy draft at `drafts/2026-04-19/` so you can test the video + overlay pipeline on its own. See [`docs/test-video.md`](test-video.md).
