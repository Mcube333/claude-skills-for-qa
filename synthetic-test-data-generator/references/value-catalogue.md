# Boundary and negative values by field type

| Field type | Boundary | Negative / invalid |
|---|---|---|
| Name | 1 char, max length, hyphen/apostrophe (O'Neil, Anne-Marie), accented (José), non-Latin (मोहम्मद) | empty, only spaces, digits, emoji, 10k chars, `<script>` |
| Email | max length 254, plus-addressing `a+b@example.com`, subdomain | missing @, two @, trailing dot, spaces |
| Phone | min/max digits for locale, with/without country code, spaces/dashes | letters, too short/long, wrong country code |
| Postcode/PIN | first/last valid in range | wrong length, letters where digits expected |
| Amount | 0, 0.01, max allowed, many decimals (rounding) | negative, non-numeric, overflow |
| Quantity | 1, max per order | 0, negative, decimal |
| Date | today, leap day, month end, 23:59 / 00:00 across timezones | past where future required, 31 Feb, far future |
| Text field | max length exactly, max+1 | empty when required, SQL/HTML injection strings (validation tests only) |
| Password | min length, all character classes | below min, common password, only spaces |
| ID / reference | min/max length, leading zeros | unknown ID, another user's record ID (authorisation test) |

Reserved values:
- Email domains: example.com, example.org, example.net (RFC 2606)
- Card numbers: only the payment gateway's documented test cards
- Phone: numbers documented as fictional for the locale (US 555-01xx), or obviously fake (all zeros after country code)
