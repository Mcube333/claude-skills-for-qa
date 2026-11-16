# Hypothesis library

Common causes by issue class, with the fastest check for each. Adapt names to the system at hand.

## Money / payment ("paid but not reflecting", wrong amount, double charge)
| Hypothesis | Fastest check |
|---|---|
| Payment authorised but never captured | Gateway dashboard/API status for the payment ID: authorised vs captured |
| Captured, but webhook not received or failed | Webhook delivery log at gateway + app webhook logs for that payment ID |
| Webhook received, but mapped to wrong order/invoice/user | Compare reference/notes field in gateway payload with the internal record |
| Payment recorded, but downstream state (subscription, renewal, order) not updated | Payment record exists? Then check the state-update job/event for that ID |
| Duplicate payment from retry or double tap | Two payment IDs with same order reference within seconds |
| Amount mismatch from rounding, tax, currency or stale price | Recompute expected amount from line items at the time of payment |
| Refund initiated but not completed | Refund status at gateway vs internal refund record |

## State / status mismatch
| Hypothesis | Fastest check |
|---|---|
| Async job failed or is stuck | Job/queue logs and retry count for the record |
| Race condition between two updates | Timestamps of both updates; which one won |
| Client shows cached or stale data | Fetch from API directly vs what the app shows |
| Manual admin change overrode the system | Audit log / updated_by for the record |

## Missing or duplicate data
| Hypothesis | Fastest check |
|---|---|
| Write failed silently (validation, constraint) | Error logs at the time of the action |
| Soft-deleted or filtered out | Query without the status/deleted filter |
| Duplicate from retry without idempotency key | Records with same business key created close together |

## Integration / third party
| Hypothesis | Fastest check |
|---|---|
| Third-party outage or timeout | Their status page and our outbound call logs at that time |
| Contract change in their API | Compare recent response fields to the expected contract |
| Credentials/config differ between environments | Config for the environment where it fails |

## Access / auth
| Hypothesis | Fastest check |
|---|---|
| Expired or revoked session/token | Token issue/expiry time vs failure time |
| Role/permission or feature flag missing for this user | User's roles/flags vs a working user |

## Only some users affected
Look for what the affected users share: platform, app version, region/city, plan type, account age,
experiment variant, payment method, or a data value (null field, special character).
