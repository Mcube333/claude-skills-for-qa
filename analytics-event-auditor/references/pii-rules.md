# PII rules

Flag as **Critical** any direct identifier in event attributes or user properties sent to a third-party analytics tool, unless the team has explicitly approved it (e.g. email as the identity key in a CRM tool), and even then note it.

| Kind | Detected by key name | Detected by value |
|---|---|---|
| email | `email`, `e_mail`, `user_email` | `x@y.tld` |
| phone | `phone`, `mobile`, `msisdn`, `contact_no`, `whatsapp` | Indian mobile (`[6-9]` + 9 digits, optional +91/0), E.164 `+` 10–15 digits |
| name | `name`, `first_name`, `full_name`, `customer_name`, `user_name` (not `product_name`, `screen_name`, `city_name`, etc.) | none (names can't be detected reliably by value) |
| address | `address`, `street`, `landmark`, `house_no` | none |
| dob | `dob`, `birth*` | none |
| gov_id | `aadhaar`, `pan`, `ssn`, `passport` | PAN `ABCDE1234F`, 12-digit Aadhaar-like |
| payment | `card_no`, `cvv`, `account_no`, `upi_id`, `vpa` | 13–19 digit Luhn-valid numbers |
| secret | `password`, `otp`, `token`, `api_key`, `auth` | JWT `eyJ…` |
| precise_location | `lat`, `lng`, `latitude`, `longitude` | none |
| ip_address | none | IPv4 |

Severity guidance: email/phone/name/address/gov_id/payment/secret → Critical. precise_location/ip_address → High unless approved. Pincode/city alone → not PII here (coarse location), mention only if combined with other identifiers.

Masking (always, in reports and chat): keep the first 2 and last 2 characters, mask the rest (`98******10`); emails keep the first letter of the local part and domain (`r***@g***`). Never paste raw PII values from captures into tickets, chat, or files.

False positives: an order id that happens to be 10 digits starting with 6–9 matches the phone pattern. When `by = value` only and the key clearly isn't personal (e.g. `order_id`), say it's likely a false positive rather than dropping it silently.
