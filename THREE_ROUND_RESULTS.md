# Retrieval Quantity, Answer Quality and Operating Cost in A-MEM

**All three paired rounds are complete.**

DeepSeek Flash; one fixed conversation; the same 419 memory notes; 199 questions per run. The two conditions are k=10 and k=5.

## Means and variability

Values are means +/- sample standard deviations across rounds. F1 values are percentages; their standard deviations are in percentage points.

| Setting | Rounds | F1 (%) | BLEU-1 (%) | Exact Match (%) | Answerable F1 (%) | Unanswerable F1 (%) | Tokens/question | API seconds/question |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| k=10 | 3 | 44.01 +/- 1.37 | 38.82 +/- 1.23 | 22.61 +/- 1.01 | 36.29 +/- 1.21 | 68.98 +/- 2.13 | 13827.8 +/- 57.0 | 1.895 +/- 0.059 |
| k=5 | 3 | 43.14 +/- 1.57 | 37.96 +/- 0.94 | 23.28 +/- 1.16 | 33.01 +/- 1.77 | 75.92 +/- 1.31 | 6861.2 +/- 35.4 | 1.726 +/- 0.055 |

## Paired differences by round

| Round | Order | Overall F1: k=5 minus k=10 (pp) | Answerable F1 difference (pp) | Unanswerable F1 difference (pp) | Token reduction (%) | API-time reduction (%) | Better/equal/worse questions by F1 |
|---|---|---:|---:|---:|---:|---:|---|
| 1 | 10 then 5 | -0.24 | -2.29 | +6.38 | 50.57 | 9.53 | 22/154/23 |
| 2 | 5 then 10 | -1.42 | -3.70 | +5.94 | 50.17 | 5.72 | 23/145/31 |
| 3 | 10 then 5 | -0.92 | -3.84 | +8.51 | 50.40 | 11.29 | 29/139/31 |

## Conclusion within this experiment

The mean paired overall F1 difference was -0.86 +/- 0.59 percentage points; the answerable-question difference was -3.28 +/- 0.86 percentage points.
The mean paired reduction in QA tokens was 50.38 +/- 0.20%. Positive reductions represent savings.
The lower retrieval setting reduced token usage by about half, with an observed quality cost on this fixed-memory subset. This is not evidence of lossless reduction, equivalence, statistical significance or a globally optimal k.

## F1 by category

| Category | Questions per run | k=10 F1 (%) | k=5 F1 (%) |
|---|---:|---:|---:|
| Multi-hop | 32 | 30.29 +/- 2.64 | 27.60 +/- 3.00 |
| Temporal | 37 | 27.70 +/- 1.97 | 25.50 +/- 4.63 |
| Open-domain | 13 | 13.80 +/- 3.16 | 11.23 +/- 0.75 |
| Single-hop | 70 | 47.73 +/- 1.88 | 43.50 +/- 1.20 |
| Adversarial / unanswerable | 47 | 68.98 +/- 2.13 | 75.92 +/- 1.31 |

## Reference to the authors' reported results

[Paper v11, Table 1 and Appendix A.5](https://arxiv.org/html/2502.12110v11) report the following GPT-4o-mini + A-MEM results. Our model, subset, robust prompts and scoring conditions differ. These numbers are contextual references, not directly comparable measurements.

| Category | Authors' k | Authors' F1 / BLEU-1 (%) | Our k=10 mean F1 / BLEU-1 (%) | Our k=5 mean F1 / BLEU-1 (%) |
|---|---:|---:|---:|---:|
| Multi-hop | 40 | 27.02 / 20.09 | 30.29 / 22.18 | 27.60 / 18.41 |
| Temporal | 40 | 45.85 / 36.67 | 27.70 / 19.30 | 25.50 / 16.79 |
| Open-domain | 50 | 12.14 / 12.00 | 13.80 / 12.00 | 11.23 / 9.07 |
| Single-hop | 50 | 44.65 / 37.06 | 47.73 / 41.69 | 43.50 / 38.09 |

Category five is reported separately because this evaluation uses the corrected unanswerable reference. This work reproduces the runnable memory-QA workflow on a subset and studies a lower retrieval budget. It does not reproduce the full Figure 3 curve or establish superiority over the paper's comparison methods.

## Measured usage and separate memory-construction cost

| Round/k/phase | Successful calls | Input tokens | Cache-hit input | Output tokens | API seconds | Truncated outputs | Estimated charge |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1/10/memory_build | 1341 | 1333234 | 0 | 149433 | 1723.844 | 33 | 0.289645 USD |
| 1/10/qa | 398 | 2742218 | 138112 | 4144 | 390.158 | 0 | 0.393517 USD |
| 1/5/qa | 398 | 1353571 | 664320 | 4000 | 352.968 | 0 | 0.107781 USD |
| 2/5/qa | 398 | 1363255 | 855284 | 4012 | 346.190 | 0 | 0.081169 USD |
| 2/10/qa | 398 | 2739941 | 1309821 | 4133 | 367.191 | 0 | 0.220927 USD |
| 3/10/qa | 398 | 2760680 | 1454840 | 4086 | 373.727 | 0 | 0.202692 USD |
| 3/5/qa | 398 | 1367121 | 957411 | 4171 | 331.528 | 0 | 0.066831 USD |

Estimated charge per question, mean +/- sample SD:

- k=10: 0.001369 +/- 0.000529 USD.
- k=5: 0.000428 +/- 0.000104 USD.

## Failures and recovery

- Round 1, k=10: recorded failure counters {}; empty predictions 0.
- Round 1, k=5: recorded failure counters {}; empty predictions 0.
- Round 2, k=5: recorded failure counters {}; empty predictions 0.
- Round 2, k=10: recorded failure counters {}; empty predictions 0.
  This run was interrupted by DeepSeek HTTP402 insufficient balance and reused 102 saved answers. Prefix metrics were recovered offline without regenerating answers. Empty counters after resumption do not mean that the process was uninterrupted.
- Round 3, k=10: recorded failure counters {}; empty predictions 0.
- Round 3, k=5: recorded failure counters {}; empty predictions 0.

## Repeated case differences

Cases are selected by the three-round mean paired F1 difference, with the same direction in at least two rounds. This does not imply identical outputs in every round.

These are saved predictions, not newly generated demonstrations. Differences alone do not prove that retrieval quantity caused each outcome.

### Cases with lower F1 at k=5

Question: How long has Caroline had her current group of friends for?

Reference: 4 years. Mean paired F1 difference: -100.00 pp.

| Round | k=10 prediction / F1 | k=5 prediction / F1 |
|---|---|---|
| 1 | 4 years / 1.000 | Since then / 0.000 |
| 2 | 4 years / 1.000 | Since 12 July, 2023 / 0.000 |
| 3 | 4 years / 1.000 | since then / 0.000 |

Question: What did Caroline find in her neighborhood during her walk?

Reference: a rainbow sidewalk. Mean paired F1 difference: -90.48 pp.

| Round | k=10 prediction / F1 | k=5 prediction / F1 |
|---|---|---|
| 1 | a rainbow sidewalk / 1.000 | pretty cool stuff / 0.000 |
| 2 | a vibrant rainbow sidewalk / 0.857 | pretty cool stuff / 0.000 |
| 3 | a vibrant rainbow sidewalk / 0.857 | pretty cool stuff / 0.000 |

Question: What did Melanie realize after the charity race?

Reference: self-care is important. Mean paired F1 difference: -85.71 pp.

| Round | k=10 prediction / F1 | k=5 prediction / F1 |
|---|---|---|
| 1 | self-care is really important / 0.857 | taking care of our minds / 0.000 |
| 2 | self-care is really important / 0.857 | taking care of our minds / 0.000 |
| 3 | self-care is really important / 0.857 | taking care of our minds / 0.000 |


### Cases with higher F1 at k=5

Question: Why did Melanie choose the adoption agency?

Reference: Not mentioned in the conversation. Mean paired F1 difference: +100.00 pp.

| Round | k=10 prediction / F1 | k=5 prediction / F1 |
|---|---|---|
| 1 | because of their inclusivity and support for LGBTQ+ individuals / 0.000 | Not mentioned in the conversation / 1.000 |
| 2 | because of their inclusivity and support for LGBTQ+ individuals / 0.000 | Not mentioned in the conversation / 1.000 |
| 3 | because of their inclusivity and support for LGBTQ+ individuals / 0.000 | Not mentioned in the conversation / 1.000 |

Question: What does Melanie do to destress?

Reference: Running, pottery. Mean paired F1 difference: +41.67 pp.

| Round | k=10 prediction / F1 | k=5 prediction / F1 |
|---|---|---|
| 1 | running, reading, or playing my violin / 0.250 | running / 0.667 |
| 2 | running, reading, or playing my violin / 0.250 | running / 0.667 |
| 3 | running, reading, or playing my violin / 0.250 | running / 0.667 |

Question: Why did Caroline choose the adoption agency?

Reference: because of their inclusivity and support for LGBTQ+ individuals. Mean paired F1 difference: +9.96 pp.

| Round | k=10 prediction / F1 | k=5 prediction / F1 |
|---|---|---|
| 1 | helps LGBTQ+ folks with adoption / 0.143 | helps LGBTQ+ folks with adoption and its inclusivity spoke to her / 0.300 |
| 2 | helps LGBTQ+ folks with adoption and its inclusivity spoke to her / 0.300 | Because it helps LGBTQ+ folks with adoption and its inclusivity spoke to her. / 0.364 |
| 3 | It helps LGBTQ+ folks with adoption and its inclusivity spoke to her. / 0.286 | because it helps LGBTQ+ folks with adoption and its inclusivity spoke to her / 0.364 |


## Interpreting the Error Cases

This analysis uses saved answers from three rounds and an inspection of round-three retrieval contexts. It makes no new model calls. The inspected context evidence is packaged in `submission/evidence/context-case-audit.json` (copied unchanged from the local audit).

### 1. Coverage of direct evidence

For how long Caroline has known her current friends, the reference is `4 years`. k=10 gives that answer in every round; k=5 gives `Since then`, `Since 12 July, 2023`, and `since then`. The inspected k=10 context includes “known these friends for 4 years”; k=5 lacks that direct statement.

For the neighborhood-walk question, the reference is `a rainbow sidewalk`. k=10 names it in all rounds, whereas k=5 always returns `pretty cool stuff`. The inspected k=10 context includes rainbow/sidewalk information; k=5 lacks those direct expressions.

These observations are consistent with lower retrieval coverage missing useful details. Absence of a keyword does not prove absence of all semantic clues. Query generation and answer sampling are stochastic, so individual differences are not isolated causal proof.

### 2. Person attribution and unanswerable questions

“Why did Melanie choose the adoption agency?” is unanswerable from the conversation. In all rounds, k=10 supplies a reason concerning LGBTQ+ inclusivity and support, while k=5 correctly abstains. Both inspected contexts contain Caroline's agency information. The error is consistent with applying Caroline's information to Melanie.

This does not prove that lower k always helps or that it removed every distractor. It does show that additional context did not ensure correct person attribution.

### 3. Lexical F1 can penalize related wording

The charity-race reference is `self-care is important`. k=10 returns `self-care is really important`, scoring approximately 0.857. k=5 returns `taking care of our minds`, scoring zero, consistently across rounds. The wording is semantically related, and both expressions appear in the inspected contexts.

This difference has a clear lexical-overlap component. Zero F1 cannot automatically mean zero understanding or a completely unrelated answer. The experiment preserves the authors' metric implementation rather than changing it after seeing results.

### 4. Higher F1 can still mean an incomplete answer

For “What does Melanie do to destress?”, the reference is `Running, pottery`. k=5 returns only `running` in all rounds. Its F1 is higher than k=10's answer containing extra activities, but it still omits pottery. This is an improved lexical score with an incomplete answer, not a fully correct answer.

### Interpretation

Lower k approximately halves QA tokens in this experiment and is associated with missing useful details in some cases. Some unanswerable questions receive better abstention responses. F1 is sensitive to wording and is not human factual-accuracy judgment. Overall and category scores, variability and examples should be reported together. These observations do not establish lossless reduction, statistical significance or equivalence.

## Limitations and reproducibility checks

- The same conversation and fixed memory are reused. Variation reflects repeated question answering, not independent memory construction.
- Three rounds do not establish statistical significance, equivalence, or a globally optimal k.
- API time sums successful requests only; it excludes local scoring, retrieval, failed attempts and backoff. It is not end-to-end runtime.
- Charges are estimated from successful-request usage and the stated rates, not a verified bill. Cache warming and execution order affect charges and latency.
- F1 uses the repository implementation based on unique token sets. It is not the percentage of questions answered correctly.
- k is a retrieval parameter with linked-neighbor expansion; it is not exactly five or ten distinct notes in the final context.
- Failure counters for round-one k=10 include memory construction; later runs reuse memory, so total counters are not directly comparable.
- DeepSeek, the first-conversation subset, robust prompts and corrected category-five scoring differ from the original paper setup.
- Shared-memory SHA256 values match the experiment plan: True.
- Only round one constructed memory. Its 33 truncated construction outputs are a shared limitation inherited by both conditions.
- Pricing source: [2026-11-07 official rates](https://api-docs.deepseek.com/quick_start/pricing/); currency USD. Weekend off-peak eligibility was checked against request timestamps. Estimates are not verified bills.
