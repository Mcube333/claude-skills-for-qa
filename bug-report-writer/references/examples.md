# Examples

## Weak report (what to avoid)

> Title: Cart page bug
> Steps: Add items and go to cart. Prices are wrong.
> Expected: Correct prices.

Problems: no area, no trigger, no data, "wrong" not shown, expectation has no source, no environment.

## Strong report

```
Title: [Cart - Cost breakup] Refundable deposit row missing when cart has items with different tenures

Environment: Staging | iOS 18.1 | iPhone 14 | App 5.12.0 (build 812) | Logged-in returning user
Preconditions: Cart contains Product A on 12-month tenure and Product B on 3-month tenure

Steps to reproduce:
1. Open the app and go to "Cart".
2. Scroll to "Cost breakup".
3. Compare rows with the Android app for the same cart.

Expected result: "Refundable deposit" row shown with the summed deposit, as on Android 5.12.0 and in PRD section 4.2.
Actual result: No "Refundable deposit" row. "Total payable now" is lower by the deposit amount.

Reproducibility: Always (5 of 5)
Severity: Major - user sees a lower amount than will be charged
Priority: P1 - pricing shown before payment; blocks release
Evidence: ios_cost_breakup.png, android_cost_breakup.png
Labels/Components: iOS, cart, pricing, regression
Notes: Possible cause: deposit field missing from the iOS cost breakup mapping (Android shows it from the same API response).
```

## Grouped ticket

```
Title: [Cart - Cost breakup] 4 formatting mismatches vs design on iOS

...
Sub-issues:
- [ ] Amounts missing thousand separators ("Rs. 12999" instead of "Rs. 12,999")
- [ ] "Handling fee" tooltip text differs from Figma frame "Cost breakup v3"
- [ ] Discount row shown in black instead of green
- [ ] Extra divider under the total row
```
