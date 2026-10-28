"""GraphQL documents (Admin API 2026-07).

Deliberately no customer PII is requested: customers are fetched by id only, and orders
don't ask for email, names or addresses.

Required access scopes: read_products, read_inventory (variant unit cost), read_orders,
read_all_orders (backfill beyond 60 days; needs Shopify approval), read_customers.
"""

MONEY = "shopMoney { amount }"

SHOP = """
query Shop { shop { name myshopifyDomain currencyCode ianaTimezone } }
"""

PRODUCT_FIELDS = """
fragment ProductFields on Product {
  id title handle productType status updatedAt
  variants(first: 100) {
    nodes {
      id sku title price
      inventoryItem { unitCost { amount } }
    }
  }
}
"""

PRODUCTS = (
    PRODUCT_FIELDS
    + """
query Products($first: Int!, $after: String, $query: String) {
  products(first: $first, after: $after, query: $query, sortKey: UPDATED_AT) {
    nodes { ...ProductFields }
    pageInfo { hasNextPage endCursor }
  }
}
"""
)

PRODUCT = (
    PRODUCT_FIELDS
    + """
query Product($id: ID!) { product(id: $id) { ...ProductFields } }
"""
)

VISIT = """
  landingPage referrerUrl source
  utmParameters { source medium campaign content term }
"""

ORDER_FIELDS = f"""
fragment OrderFields on Order {{
  id name createdAt processedAt updatedAt cancelledAt test sourceName currencyCode
  displayFinancialStatus displayFulfillmentStatus
  customer {{ id }}
  subtotalPriceSet {{ {MONEY} }}
  totalDiscountsSet {{ {MONEY} }}
  totalShippingPriceSet {{ {MONEY} }}
  totalTaxSet {{ {MONEY} }}
  totalPriceSet {{ {MONEY} }}
  totalRefundedSet {{ {MONEY} }}
  customAttributes {{ key value }}
  customerJourneySummary {{
    firstVisit {{ {VISIT} }}
    lastVisit {{ {VISIT} }}
  }}
  lineItems(first: 100) {{
    nodes {{
      id name sku quantity
      originalUnitPriceSet {{ {MONEY} }}
      totalDiscountSet {{ {MONEY} }}
      product {{ id }}
      variant {{ id inventoryItem {{ unitCost {{ amount }} }} }}
    }}
  }}
  refunds(first: 50) {{
    id createdAt note
    totalRefundedSet {{ {MONEY} }}
    refundLineItems(first: 100) {{ nodes {{ totalTaxSet {{ {MONEY} }} }} }}
  }}
  transactions(first: 50) {{
    kind status gateway
    amountSet {{ {MONEY} }}
    fees {{ amount {{ amount }} }}
  }}
}}
"""

ORDERS = (
    ORDER_FIELDS
    + """
query Orders($first: Int!, $after: String, $query: String) {
  orders(first: $first, after: $after, query: $query, sortKey: UPDATED_AT) {
    nodes { ...OrderFields }
    pageInfo { hasNextPage endCursor }
  }
}
"""
)

ORDER = (
    ORDER_FIELDS
    + """
query Order($id: ID!) { order(id: $id) { ...OrderFields } }
"""
)

# Only used transiently by the conversions sender: email/phone are hashed immediately and
# never stored. Needs "protected customer data" access for email + phone in the Dev Dashboard;
# without it Shopify returns an access error and events go out without hashed PII.
ORDER_PII = """
query OrderPii($id: ID!) {
  order(id: $id) { email phone billingAddress { countryCodeV2 } }
}
"""

CUSTOMERS = """
query Customers($first: Int!, $after: String, $query: String) {
  customers(first: $first, after: $after, query: $query) {
    nodes { id createdAt }
    pageInfo { hasNextPage endCursor }
  }
}
"""

WEBHOOKS = """
query Webhooks { webhookSubscriptions(first: 100) { nodes { id topic uri } } }
"""

WEBHOOK_CREATE = """
mutation WebhookCreate($topic: WebhookSubscriptionTopic!, $uri: String!) {
  webhookSubscriptionCreate(topic: $topic, webhookSubscription: {uri: $uri, format: JSON}) {
    webhookSubscription { id topic uri }
    userErrors { field message }
  }
}
"""
