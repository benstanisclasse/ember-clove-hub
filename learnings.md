# Ember & Clove — learnings playbook

Running conclusions drawn from the Hub's records. Update after every cycle.
Evidence levels: **controlled** (one-change duplicate test) · **repeated** (seen in 2+ cycles) · **tentative** (one cycle) · **contradicted**.

## What works
_(none yet)_

## What doesn't
_(none yet)_

## Open questions to test next
_(none yet)_

## Cycle notes

### 2026-10-24 — Pricing blocks paid ads (economics.py, verified from Shopify)
All 13 products are priced only ~10–11% above Shopify unit cost. After payment fees (2.9% + $0.30) and a 5% refund allowance, profit per sale is $0–1.29 **before any shipping cost**, so break-even CPA is effectively $0–1. No paid campaign can be profitable at current prices. Evidence level: **verified** (arithmetic on store data). Prices needed for a $20 break-even CPA are in `data/products.csv` (`price_for_desired_cpa`).

### 2026-10-24 — Sourcing decision: dropship apparel only
Owner chose dropship-only, apparel-only. Supplier research (reports/supplier_research_2026-10-24.md): Printful cuts landed cost vs current suppliers by ~$4 (tee), ~$7 (crewneck) and ~$23 (hoodie). With Printful, profit per sale reaches the ~$20 ad budget at tee $32.99, crewneck $44.99, hoodie $49.99+. Hoodies have the most room ($26–31 at $54.99–59.99). Wellness products dropped: current supplier retail prices undercut any viable markup. Evidence: **verified** for Printful list prices; Printify/Gooten figures are estimates.
