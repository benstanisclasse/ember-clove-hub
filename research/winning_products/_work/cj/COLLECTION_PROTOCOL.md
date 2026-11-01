# Phase F CJ collection protocol (for collector agents)

This implements sections F2-F5 of `registry/PHASE_F_PLAN.md`. Candidates are listed in
`research/winning_products/_work/phase_f_candidates.csv`; use the columns cand, cat_name, name, asp and saved_cj_pid.

## Safety: read-only, hard rules

Use **only** these CJ connector tools:
- `search_products`
- `get_product_detail`
- `get_product_variants`
- `get_product_inventory`
- `calculate_freight`
- `get_rate_limit_status`

Never call any other CJ tool. That includes every add_to_cart, cart, order, pay, payment link, sourcing, dispute,
product connection, save_product_to_shop, publish, listing, webhook, settings, `show_*` and `open_*` tool, and image
search. Nothing may be ordered, saved, listed, connected or changed.

## Rate limit

Make CJ calls **one at a time**: never more than one call in a single message. Freight (logistics) must stay at
roughly 1 request per second or slower.

## Data integrity: most important

- Copy every number, id and string **exactly** as the tool returned it.
- Never estimate, round, fill in or "fix" a value. If a field is missing, write null.
- If a call errors, record the error text in `errors` and move on. One retry is allowed.

## Per candidate

### 1. Search

- Write 1-2 **generic** English keyword phrases (2-5 words). Remove brand names. Describe function and form, e.g.
  "bone conduction headphones", "baggy cargo jeans men".
- Run `search_products(keyword=..., pageSize=20)`.
- If `saved_cj_pid` is set, evaluate that pid first; still run at least one search.

### 2. Consider candidates

- Open up to 3 plausible results with `get_product_detail(pid=...)`.
- Compare against the Kalodata title on:
  - function
  - form
  - material
  - dimensions/specs
  - capacity/size
  - pack quantity
  - colours and sizes
  - packaging
- Don't just take the first result.

### 3. Score the best match

| Score | Meaning |
|---|---|
| 2 | Close substitute: same function and form, same key specs and pack size; differs only in secondary details |
| 1 | Same function but materially different (form factor, material, capacity, pack size, quality tier), **or** the Kalodata item is a branded, licensed or patented design that CJ only imitates (a brand's own design, a character, a vehicle licence, a signature mechanism) |
| 0 | Nothing acceptable on CJ |

Score 3 is not allowed in this phase: photos are not compared.

### 4. If the score is 2, collect variants, inventory and freight

**Variants:** `get_product_variants(pid=...)`.

**Inventory:** `get_product_inventory(pid=...)`.

**Freight:** `calculate_freight` with `endCountryCode="US"` and `products=[{vid, quantity: 1}]`.
- **vid:** the heaviest variant by `variantWeight`. Also run the lightest variant if it weighs < 70% of the heaviest.
- **Origins:**
  - `startCountryCode="CN"`, always.
  - `startCountryCode="US"` as well, if the inventory shows any US stock.
- **Zips:** run each origin with each of 10001, 60601 and 90001.
- That makes 3-12 freight calls per candidate.

**If the score is 0 or 1:** skip step 4, but still save the file.

## Output

Write one file per candidate: `research/winning_products/_work/cj/<cand>.json`. Write it as soon as that candidate is
done, then go on to the next.

```json
{
  "cand": "F01",
  "kalo_pid": "...",
  "kalo_name": "...",
  "collected_at": "2026-11-01T..Z",
  "searches": [
    {
      "keyword": "...",
      "n_results": 20,
      "results": [
        {"pid": "...", "name": "...", "sellPrice": "...", "listedNum": 0, "warehouseInventoryNum": 0, "isWarehouse/country fields if present": "..."}
      ]
    }
  ],
  "considered": [
    {"cj_pid": "...", "cj_name": "...", "score": 1, "reason": "why it was or wasn't chosen"}
  ],
  "match": {
    "cj_pid": "... or null",
    "cj_name": "...",
    "cj_sku": "...",
    "score": 2,
    "branded_cap": false,
    "note": "1-2 sentences: what matches and what differs"
  },
  "detail": {
    "productNameEn": "...", "productSku": "...", "categoryName": "...", "material": "...", "packing": "...",
    "productWeight": "...", "listedNum": 0, "sellPrice": "...", "suggestSellPrice": "...",
    "description_excerpt": "first ~300 characters, verbatim"
  },
  "variants": [
    {
      "vid": "...", "variantSku": "...", "variantKey": "...", "variantNameEn": "...", "variantWeight": 0,
      "variantLength": 0, "variantWidth": 0, "variantHeight": 0, "variantSellPrice": 0, "variantSugSellPrice": 0
    }
  ],
  "inventory": [
    {"vid": "...", "countryCode": "CN", "totalInventory": 0, "cjInventory": 0, "factoryInventory": 0, "verifiedWarehouse": 1}
  ],
  "freight": [
    {
      "vid": "...", "which": "heaviest", "origin": "CN", "zip": "10001",
      "methods": [
        {
          "logisticName": "...", "logisticAging": "4-9", "logisticPrice": 0, "totalPostageFee": 0, "taxesFee": 0,
          "clearanceOperationFee": 0, "remoteFee": null, "error": null, "errorEn": null
        }
      ]
    }
  ],
  "errors": []
}
```

Notes on the fields:
- **searches.results:** keep up to 20 per search.
- **inventory:** this is `variantInventories`, flattened to one row per vid × country. Leave out the `stock` sub-lists.
- **freight.methods:** keep **every** method returned, with exactly these fields.
- **Field names:** use the names the tool returns. If the tool's names differ from those shown above, keep the tool's names.
