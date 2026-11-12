# Recommendation, ranking, search and classification models

These outputs are judged in aggregate, not per response. One bad recommendation is not a bug; a drop in relevance across a labelled set is. So testing has two layers: **property checks per response** (still apply the four buckets) and **metrics on a labelled dataset**.

## 1. Per-response properties (hard rules, every response)
- **Shape**: right number of items (e.g. exactly 10 or ≤ N), no duplicates, valid IDs, scores in range and sorted when the UI expects sorted.
- **Must include**: pinned/sponsored/business-rule items appear where required; the exact-match item ranks first for an exact search query.
- **Must NOT include**: out-of-stock or unserviceable items (postal code/region), items already in cart/purchased when that's the rule, items of the wrong category, disabled/blacklisted SKUs, adult or unsafe items.
- **Around it**: latency, fallback when model is down (popular/default list, never an empty widget), cold-start user (no history) still gets a sensible list, analytics impression/click events fire with position.

## 2. Labelled dataset
- Build a golden set: inputs (user profile/query/item) with **labels** (relevant / not relevant, graded 0–3, or correct class).
- Sources: past clicks/orders/conversions, human labelling, support-ticket categories already tagged.
- Size: at least a few hundred for classification; 50–200 queries for search/ranking to start. Keep a **frozen** version for regression and a refreshed one for drift.
- Include slices: new vs returning users, cities, categories, platforms, long-tail queries, code-mixed-language/typo queries.

## 3. Metrics
**Classification** (intent, category, fraud, sentiment):
- Precision = of items flagged X, how many are truly X (cost of false alarms).
- Recall = of truly X items, how many we flagged (cost of misses).
- F1 = balance of both. Confusion matrix to see which classes get confused.
- Choose by business cost: fraud/PII detection → prioritise recall; auto-actions (auto-refund) → prioritise precision.

**Ranking / recommendation / search**:
- Precision@K / Recall@K: relevant items within top K.
- MRR: how high the first relevant result sits.
- NDCG@K: graded relevance with position weighting (standard for search).
- Hit rate@K: did the item the user later bought appear in top K.
- Coverage & diversity: share of catalogue ever recommended; not 10 near-identical items.
- Online (A/B, via analytics/BI dashboards): CTR, add-to-cart rate, conversion, revenue per session. Offline metrics must agree directionally with online ones.

## 4. Thresholds and regression
- Set a baseline from the current production model; a new model/version must be ≥ baseline − tolerance (e.g. NDCG@10 drop ≤ 1%) **overall and on every key slice**. A global gain that hides a slice drop is a fail.
- Re-run on: new model version, retraining, feature/data pipeline change, catalogue change.
- Log model version, dataset version, and metric values per run.

## 5. Test-case ideas
- Same user, two calls → stable ordering (or documented randomness).
- Item goes out of stock → disappears from recs within the agreed time.
- User with zero history → fallback list, no error.
- Query with typo / code-mixed → still finds the intended category.
- Boundary scores for classifiers (just above/below threshold).
- Bias/fairness slices: does any city/segment get systematically worse results?

## Output: Metrics plan
| Metric | Why | Dataset/slice | Threshold | Current baseline |
