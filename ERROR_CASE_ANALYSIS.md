# Interpreting the Error Cases

This analysis uses saved answers from three rounds and an inspection of round-three retrieval contexts. It makes no new model calls. The inspected context evidence is packaged in `submission/evidence/context-case-audit.json` (copied unchanged from the local audit).

## 1. Coverage of direct evidence

For how long Caroline has known her current friends, the reference is `4 years`. k=10 gives that answer in every round; k=5 gives `Since then`, `Since 12 July, 2023`, and `since then`. The inspected k=10 context includes “known these friends for 4 years”; k=5 lacks that direct statement.

For the neighborhood-walk question, the reference is `a rainbow sidewalk`. k=10 names it in all rounds, whereas k=5 always returns `pretty cool stuff`. The inspected k=10 context includes rainbow/sidewalk information; k=5 lacks those direct expressions.

These observations are consistent with lower retrieval coverage missing useful details. Absence of a keyword does not prove absence of all semantic clues. Query generation and answer sampling are stochastic, so individual differences are not isolated causal proof.

## 2. Person attribution and unanswerable questions

“Why did Melanie choose the adoption agency?” is unanswerable from the conversation. In all rounds, k=10 supplies a reason concerning LGBTQ+ inclusivity and support, while k=5 correctly abstains. Both inspected contexts contain Caroline's agency information. The error is consistent with applying Caroline's information to Melanie.

This does not prove that lower k always helps or that it removed every distractor. It does show that additional context did not ensure correct person attribution.

## 3. Lexical F1 can penalize related wording

The charity-race reference is `self-care is important`. k=10 returns `self-care is really important`, scoring approximately 0.857. k=5 returns `taking care of our minds`, scoring zero, consistently across rounds. The wording is semantically related, and both expressions appear in the inspected contexts.

This difference has a clear lexical-overlap component. Zero F1 cannot automatically mean zero understanding or a completely unrelated answer. The experiment preserves the authors' metric implementation rather than changing it after seeing results.

## 4. Higher F1 can still mean an incomplete answer

For “What does Melanie do to destress?”, the reference is `Running, pottery`. k=5 returns only `running` in all rounds. Its F1 is higher than k=10's answer containing extra activities, but it still omits pottery. This is an improved lexical score with an incomplete answer, not a fully correct answer.

## Interpretation

Lower k approximately halves QA tokens in this experiment and is associated with missing useful details in some cases. Some unanswerable questions receive better abstention responses. F1 is sensitive to wording and is not human factual-accuracy judgment. Overall and category scores, variability and examples should be reported together. These observations do not establish lossless reduction, statistical significance or equivalence.
