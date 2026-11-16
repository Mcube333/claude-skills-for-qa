# Experiment mechanics checks

| Check | How to test | Expected |
|---|---|---|
| Bucketing works | Several fresh users/devices | Each lands in one variant; split roughly matches allocation over many users |
| Stickiness - session | Reload, background/foreground, navigate away and back | Same variant |
| Stickiness - login | Guest bucketed, then logs in (and the reverse) | Defined behaviour (keep or re-bucket) matches PRD; no flicker |
| Stickiness - cross device | Same account on two devices | Same variant if bucketing is by user ID |
| Isolation | Inspect UI, API responses, analytics in each variant | No elements or calls from another variant |
| Targeting | Ineligible user (region, platform, version, segment) | Sees control/default, no exposure event |
| Exposure timing | Watch network/analytics | Exposure fires when the variant is shown, once |
| Fallback | Block the flag service or force timeout | App shows default/control without crash or blank UI |
| Kill switch | Turn experiment off | All users get default; no stale variant from cache |
| Cache / CDN | Change allocation | New users follow new allocation; old users per stickiness rules |
| Old app versions | Version without the experiment code | Stable, sees default |
| Concurrent experiments | User in two experiments touching same screen | Defined precedence, no broken layout |
| Test traffic exclusion | Run automation | Not counted in experiment metrics |
