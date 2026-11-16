# Change classification rules

| Change | Response (server -> client) | Request (client -> server) |
|---|---|---|
| Field removed | Breaking | Safe if server ignores it; breaking if server now rejects unknown fields |
| Field added | Safe (optional) | Breaking if required; safe if optional |
| Field renamed | Breaking | Breaking |
| Type changed (number <-> string, object <-> array) | Breaking | Breaking |
| Optional -> required | Safe for clients | Breaking |
| Required -> optional / nullable | Risky/Breaking (clients may crash on null) | Safe |
| Enum value added | Risky (old clients may not handle) | Safe |
| Enum value removed | Safe for clients reading, breaking if clients send it | Breaking |
| Format changed (date, decimals, currency string) | Risky | Risky |
| Status code changed | Breaking | n/a |
| Endpoint removed / path changed | Breaking | Breaking |
| Auth / header requirement added | Breaking | Breaking |
| Pagination / default sort changed | Risky | Risky |
