"""Atomic, validated QA checkpoints; no model calls or metric changes."""
import json
import math
from pathlib import Path

QUESTION_FIELDS = ('sample_id', 'question_index', 'question', 'reference', 'category', 'adversarial_answer')


def load_checkpoint(path, metadata, expected_questions):
    path = Path(path)
    if not path.exists():
        return {}, {}
    payload = json.loads(path.read_text(encoding='utf-8'))
    if payload.get('metadata') != metadata:
        raise ValueError('Checkpoint settings differ from this evaluation')
    rows = payload.get('individual_results')
    if not isinstance(rows, list) or len(rows) > len(expected_questions):
        raise ValueError('Invalid checkpoint result count')
    answers = {}
    for row, expected in zip(rows, expected_questions):
        if any(row.get(field) != expected[field] for field in QUESTION_FIELDS):
            raise ValueError('Checkpoint questions are not a matching sequential prefix')
        if not isinstance(row.get('prediction'), str):
            raise ValueError('Invalid saved prediction')
        metrics = row.get('metrics', {})
        if not all(field in metrics for field in ('f1', 'bleu1', 'exact_match')):
            raise ValueError('Checkpoint is missing quality metrics')
        if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in metrics.values()):
            raise ValueError('Checkpoint contains invalid metric values')
        if any(not 0 <= metrics[field] <= 1 for field in ('f1', 'bleu1', 'exact_match')):
            raise ValueError('Checkpoint primary metrics are out of range')
        answers[(row['sample_id'], row['question_index'])] = row
    return answers, payload.get('recovery', {})


def save_checkpoint(path, metadata, rows, recovery):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    payload = {'metadata': metadata, 'individual_results': rows, 'recovery': recovery}
    temporary.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
    temporary.replace(path)
