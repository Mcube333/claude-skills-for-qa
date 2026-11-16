# Go / no-go rules (defaults; adapt to the team's exit criteria)

## No-go if any of these
- An open Critical or P1 product bug in scope
- Payment, pricing, checkout, login or data-integrity flows not executed
- Pass rate of must-test (P1) cases below 100% without an accepted exception
- Smoke suite failing on the release build
- Privacy issue open (PII leak, wrong data shown to another user)

## Go with known issues if
- Only Major/P2 or lower bugs open, each with an owner and a named person who accepted it
- Coverage gaps are low-risk and written down
- Workarounds exist for the open issues and support is informed

## Go if
- No open product bugs above Minor/P3 in scope
- All planned must-test cases executed and passed
- Automation green, or failures explained as test/environment issues and covered manually
