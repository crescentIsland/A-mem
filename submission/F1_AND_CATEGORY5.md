# F1 and Category-Five Scoring in This Experiment

This explanation follows the local implementation in `utils.py`, `load_dataset.py` and `test_advanced_robust.py`. It does not change the metrics or measured outputs.

## The F1 formula to put on slide five

Let A be the set of unique prediction tokens, B the set of unique reference tokens, and C their intersection:

$$
A=\operatorname{set}(\operatorname{tokens}(\hat y)),\qquad
B=\operatorname{set}(\operatorname{tokens}(y)),\qquad C=A\cap B.
$$

$$
P=\frac{|C|}{|A|},\qquad R=\frac{|C|}{|B|},\qquad
F_1=\frac{2PR}{P+R}=\frac{2|C|}{|A|+|B|}.
$$

- **Precision:** what fraction of the predicted unique words appear in the reference?
- **Recall:** what fraction of the reference's unique words are covered by the prediction?
- **F1:** the harmonic mean of precision and recall.
- An empty token set or zero overlap receives F1=0. Duplicate words count once.

The repository lowercases text, replaces periods, commas, exclamation marks and question marks with spaces, and splits on whitespace. This F1 function does not remove stopwords or perform stemming. Other metrics may tokenize differently.

### Small worked example

Reference: `4 years`. Prediction: `4`.

Then A={4}, B={4, years}, and C={4}. Precision=1, recall=1/2, and F1=2/3, approximately 0.667. Predicting `4 years` gives F1=1. Predicting `since then` gives F1=0 for this reference.

The reported run F1 averages the 199 per-question scores; the final table shows the mean and sample SD of three run-level values. F1 is not the percentage of correctly answered questions.

## What category five tests

Category five contains adversarial questions that cannot be answered from the conversation. The expected behavior is to say that the answer was not mentioned, rather than inventing information or borrowing it from the wrong person.

For example, the conversation provides Caroline's adoption-agency reason, but the question asks why **Melanie** chose the agency. The reference is `Not mentioned in the conversation`.

### What is actually scored

1. The prompt presents that unanswerable option and a misleading candidate answer in seed-controlled order.
2. `QA.reference(False)` returns `Not mentioned in the conversation` for category five.
3. The standard quality metrics, including lexical F1, compare the prediction against that reference. Semantically similar abstention wording can receive different lexical scores.
4. A separate `adversarial_correct` heuristic checks for `not mentioned` or `no information available`, and rejects predictions also containing the literal misleading answer. This is a rule-based auxiliary flag, not a general semantic judge.
5. The legacy option would score against the misleading answer. This experiment leaves `legacy_c5_reference=False` in every condition.

Therefore, a category-five F1 of 75.92% is not a claim that exactly 75.92% of those questions were correctly rejected. Keep lexical F1, Exact Match and the auxiliary abstention flag distinct.

## Actual stored memory

Open `MEMORY_NOTE_EXAMPLE.md` for one real final-state note, `MEMORY_NOTES.md` for all 419 notes, or `memory-notes.json` for structured fields. They come from the verified cache shared by all runs. The raw dialogue remains in `data/locomo10.json` at the repository root. Generated context and tags should be checked against original content; they are model outputs, not independent ground truth.
