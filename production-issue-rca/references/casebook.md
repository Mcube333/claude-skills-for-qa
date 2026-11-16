# Casebook

Add one entry per solved pattern. Keep it generic enough to reuse; no customer data.

## Template

### <Pattern name>
- **Signals:** what the ticket and first checks look like
- **Checks:** the queries/logs/screens that confirmed it
- **Root cause:** one line
- **Resolution:** what was done for the customer
- **Prevention:** fix + regression test

## Example

### Payment captured, renewal not extended
- **Signals:** customer has a payment receipt; account still shows renewal overdue and late fee.
- **Checks:** gateway shows captured; webhook delivered; payment row exists but linked to an older invoice.
- **Root cause:** webhook handler matched the payment to the oldest open invoice instead of the one in the payment reference.
- **Resolution:** support raised a correction request to relink the payment and reverse the late fee.
- **Prevention:** match on the reference ID only; regression test: two open invoices, pay the newer one, assert the newer one is closed.
