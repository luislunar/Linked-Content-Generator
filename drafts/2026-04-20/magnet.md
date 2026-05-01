# The GSA Pricing Calculator: What Federal Buyers Will Actually Pay

A back-of-envelope calculator to price your GSA Schedule offer so it wins bids *and* protects margin. Federal buyers have a predictable ceiling — most small businesses leave 18–30% on the table because they price like it's a commercial quote.

## How to use

1. Pull your last 10 commercial invoices for the product/service you'll put on Schedule.
2. Compute your **Most Favored Customer (MFC) price** — the lowest price any commercial customer has paid in the last 12 months.
3. Apply the formulas below. The output is the price you submit in your GSA proposal.

## The formulas

### Step 1 — Baseline GSA price
```
GSA_Price = MFC_Price × (1 - GSA_Discount)
```
Typical `GSA_Discount`: **4%–8%** below MFC. Going deeper signals weakness; going shallower gets rejected.

### Step 2 — Add the Industrial Funding Fee (IFF)
```
Submitted_Price = GSA_Price × 1.0075
```
The 0.75% IFF is GSA's cut. You collect it from the buyer and remit it quarterly.

### Step 3 — Sanity check against GSA Advantage
Search your product category on `gsaadvantage.gov`. Your `Submitted_Price` should land in the **40th–60th percentile** of comparable offerings. Too low → buyers assume quality issues. Too high → contracting officer rejects on "fair and reasonable."

## Worked example — IT services

| Input | Value |
|---|---|
| MFC commercial rate | $185/hr |
| GSA discount (6%) | -$11.10 |
| GSA price | $173.90 |
| IFF (0.75%) | +$1.30 |
| **Submitted price** | **$175.20/hr** |

GSA Advantage comparable range: $140–$210. This lands at the 58th percentile. ✅ Proceed.

## Red flags your pricing is wrong

- You priced identically to commercial → proposal rejected (no MFC discount shown)
- You discounted 20%+ → you'll lose money on every BPA call order
- You're the cheapest on GSA Advantage by 15%+ → buyers think you can't deliver
- You forgot IFF → you owe GSA money out of pocket every quarter

## What to do next

Run your top 3 SKUs through this calculator. If any land outside the 40th–60th percentile, comment **PRICE** and I'll send you the MFC documentation template GSA requires.
