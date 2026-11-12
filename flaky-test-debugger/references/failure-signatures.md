# Failure signatures

Error text → likely category → what to check → typical fix. Messages are abbreviated; match on the distinctive part.

## 1. Synchronization / timing

| Signature | Framework | Check | Fix |
|---|---|---|---|
| `TimeoutError: locator.click: Timeout 30000ms exceeded` + call log `waiting for locator(...)` with no match | Playwright | Element never appeared: wrong page/state, or earlier step didn't finish | Assert the preceding state (URL, loader hidden, response) before acting |
| Call log shows `element is not stable` / `element is not visible` / `element is not enabled` repeatedly | Playwright | Animation, disabled button awaiting validation/API | Wait for the enabling condition (`assertThat(btn).isEnabled()`, response) |
| `expect(locator).toHaveText` / `hasText` failed with an older value | Playwright | Value read before async update | Use web-first assertion on the final value; don't read `textContent()` then compare |
| Assertion on `count()`/`allTextContents()` returns fewer items | Playwright | Read immediately, list still loading | `assertThat(items).hasCount(n)` or wait for the list response first |
| `NoSuchElementException` right after click/navigation | Selenium/Appium | Implicit wait 0 or too short and no explicit wait | Explicit `WebDriverWait` for the target condition |
| `StaleElementReferenceException` | Selenium/Appium | Element reference held across a re-render | Re-locate inside the wait; PageFactory proxies or `By` per use; ignore stale in waits |
| `TimeoutException: Expected condition failed: waiting for visibility of...` intermittently near loaders | Selenium/Appium | Waiting on element while spinner overlays | Wait for spinner invisibility first |
| Test passes with a debugger/breakpoint, fails at full speed | any | Classic missing wait | Find the step that needs a condition |
| `Thread.sleep(…)` present near the failing line | any | Sleep too short on slow runs, wasteful on fast ones | Replace with the condition it was standing in for |

## 2. Locator fragility / strictness

| Signature | Framework | Fix |
|---|---|---|
| `strict mode violation: locator(...) resolved to 2 elements` | Playwright | Scope to a container, use role+name, or `getByTestId`; avoid `.first()` unless order is guaranteed |
| Works on some runs: index-based XPath `(//div)[3]`, `nth(2)` | any | Content-dependent ordering (recommendations, sort ties). Locate by text/test id |
| Generated ids/classes (`css-1x2y3z`, `:r5:`, `android:id/...12`) | any | Use test ids or accessibility ids; ask devs to add them |
| Text locator fails on some runs | any | Text varies (A/B copy, locale, truncation, dynamic counts). Use test id or regex |

## 3. Overlay, animation, click interception

| Signature | Framework | Fix |
|---|---|---|
| `<div class="modal-backdrop"> intercepts pointer events` / `subtree intercepts pointer events` | Playwright | Wait for overlay to be hidden; dismiss toast/banner explicitly; don't use `force` |
| `ElementClickInterceptedException: ... Other element would receive the click` | Selenium | Same; also check sticky headers covering the element after scroll |
| Cookie/consent banner, app rating prompt, push-permission dialog in screenshot | any | Deterministically dismiss in setup or pre-set consent via cookie/storage state/capability |
| Mobile: keyboard covers button | Appium | Hide keyboard or scroll element into view before tap |
| Bottom sheet / carousel mid-animation | Appium/web | Wait for final position/state (attribute or settled element), or disable animations (Android dev settings `animator_duration_scale=0`, CSS `prefers-reduced-motion`/`reducedMotion: 'reduce'` context option) |

## 4. Test data and state coupling

| Signature | Check | Fix |
|---|---|---|
| Passes alone, fails in suite (or vice versa) | Order dependence: run isolated vs full suite | Each test creates its own data; no shared mutable fixtures |
| `409 Conflict`, `duplicate key`, "already exists" | Hard-coded unique values (email, ISBN, phone) | Generate unique data per run (UUID/timestamp) |
| Cart/wishlist/count assertions off by N | Shared account accumulating state from other tests/runs | Dedicated accounts per thread, or clean state in setup via API |
| Fails first run of the day / after deploy | Cache warm-up, seed data reset, expired token | Health check / warm-up step; token refresh |
| Leftover cookies/localStorage/app data | Context or app reused (`noReset=true`) | New browser context per test; `noReset=false` or explicit cleanup |

## 5. Parallel / concurrency

| Signature | Check | Fix |
|---|---|---|
| Fails only with threads > 1; actions land in the wrong browser/device | `static WebDriver`/`Page`/`Playwright` fields, singletons | ThreadLocal per thread; `remove()` after quit |
| `Target page, context or browser has been closed` in another test | Shared context closed by a sibling test's teardown | Per-test context ownership |
| Appium: `Could not start a new session`, `systemPort ... busy`, `wdaLocalPort` conflicts | Same port for two devices | Unique `systemPort`/`wdaLocalPort`/`mjpegServerPort` per device |
| `ConcurrentModificationException`, NPE in shared list/map | Shared non-thread-safe collection in test class | Thread-safe collections or per-thread state |
| REST Assured: wrong base URI/auth in some tests | Tests mutating `RestAssured.baseURI`/static filters | Per-request `RequestSpecification` |
| Failure rate grows with thread count | | Compare thread-count=1 vs N to confirm |

## 6. Environment / infrastructure

| Signature | Notes |
|---|---|
| `net::ERR_CONNECTION_REFUSED`, `ECONNRESET`, `Connection reset`, `SocketTimeoutException` | Service down/restarting; check timestamps against deploys |
| Backend `502/503/504` in trace network list at failure time | Env instability (or product bug if reproducible under normal load) |
| `java.lang.OutOfMemoryError`, `Browser closed unexpectedly`, `Target crashed` | CI resources; too many workers for the runner |
| `Session not created`, `device offline`, `adb: device unauthorized`, `xcodebuild failed with code 65` | Device/emulator health; add a pre-run device check |
| Only on CI, only headless | Viewport differences (responsive layout hides element), fonts, missing GPU. Set viewport explicitly; compare headed vs headless |

## 7. External dependencies

| Signature | Fix |
|---|---|
| Different UI on different runs (copy, layout, flow) | **A/B experiment or feature flag** bucketing randomly. Pin the variant (cookie, header, user attribute, flag override) per test |
| Payment sandbox, maps, OTP/SMS provider, analytics timing out | Mock/stub at the network layer (`page.route`, WireMock), or isolate into a dedicated, non-blocking suite |
| Analytics/tracking assertions intermittently missing events | Events batched/flushed asynchronously. Wait for the specific outgoing request rather than a fixed delay; assert presence, not exact order, unless order is part of the spec |
| Recommendations/search results vary | Assert on properties (count ≥ 1, all match filter), not exact items |

## 8. Time, date, locale

| Signature | Fix |
|---|---|
| Fails around midnight, month end, DST change, or in a different CI region | Freeze/inject clock (`page.clock` in Playwright Node 1.45+, `context.setTimezoneId`, `Clock` injection in Java), set `timezoneId`/`locale` in context options |
| Date pickers selecting "tomorrow" fail at month boundaries | Compute dates relative to a fixed date, or select by full date |
| Currency/number formatting differs (`$1,299` vs `$1299`, `1.299,00`) | Set locale explicitly; parse numbers instead of comparing strings |

## 9. Real product bug (don't hide)

Indicators: app shows an error toast/page; a request returns 5xx under normal load; the same request is sent twice (double submit); state is wrong after a correct action (e.g. total not updated after quantity change); a race between two API calls producing different final values on different runs. Action: keep the test failing (or quarantine with a linked bug), write a short bug report: steps, expected, actual, frequency (from flake_stats), evidence (trace network lines, screenshot).

## REST Assured specifics

| Signature | Category |
|---|---|
| `java.net.SocketTimeoutException: Read timed out` | 6 (or 9 if one endpoint consistently slow) |
| Status flips 200/404 right after create | Eventual consistency / replication lag: poll for the resource with a bounded wait (Awaitility), don't sleep |
| Schema validation fails on some runs only | Optional/nullable field present only for some data. Fix schema (if API is correct) or file a contract bug |
| 401 midway through suite | Token expiry: refresh logic |

## TestNG/JUnit specifics

| Signature | Category |
|---|---|
| `@BeforeClass`/`@BeforeSuite` failure → many skipped tests | Fix the first failure; skips are cascade |
| `dependsOnMethods` chains | Order coupling (4); make tests independent |
| `parallel="methods"` with instance fields set in `@BeforeMethod` | Concurrency (5): TestNG shares one instance across threads, so instance fields race. Use ThreadLocal |
