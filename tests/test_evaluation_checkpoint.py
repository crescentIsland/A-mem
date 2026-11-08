import copy

import pytest

from evaluation_checkpoint import load_checkpoint, save_checkpoint


def fixtures():
    expected = [dict(sample_id=0, question_index=i, question=f'q{i}',
                     reference=f'gold{i}', category=1, adversarial_answer=None)
                for i in range(2)]
    row = dict(expected[0], prediction='prediction', metrics=dict(f1=0.5, bleu1=0.2, exact_match=0))
    return {'model': 'same', 'k': 10}, expected, row


def test_round_trip_keeps_prefix_and_recovery(tmp_path):
    metadata, expected, row = fixtures()
    path = tmp_path/'checkpoint.json'
    recovery = {'reason': 'HTTP402', 'completed_questions': 1}
    save_checkpoint(path, metadata, [row], recovery)
    saved, restored_recovery = load_checkpoint(path, metadata, expected)
    assert saved == {(0, 0): row}
    assert restored_recovery == recovery
    assert not path.with_suffix('.json.tmp').exists()


def test_absent_checkpoint_has_no_saved_answers(tmp_path):
    metadata, expected, _ = fixtures()
    assert load_checkpoint(tmp_path/'missing.json', metadata, expected) == ({}, {})


@pytest.mark.parametrize('bad', ['settings', 'reference', 'skip', 'duplicate', 'nan'])
def test_rejects_incompatible_or_corrupt_checkpoint(tmp_path, bad):
    metadata, expected, row = fixtures()
    rows = [copy.deepcopy(row)]
    saved_metadata = dict(metadata)
    if bad == 'settings':
        saved_metadata['k'] = 5
    elif bad == 'reference':
        rows[0]['reference'] = 'different gold'
    elif bad == 'skip':
        rows[0]['question_index'] = 1
    elif bad == 'duplicate':
        rows.append(copy.deepcopy(row))
    elif bad == 'nan':
        rows[0]['metrics']['f1'] = float('nan')
    path = tmp_path/'checkpoint.json'
    save_checkpoint(path, saved_metadata, rows, {})
    with pytest.raises(ValueError):
        load_checkpoint(path, metadata, expected)


def test_evaluator_reuses_saved_answer_without_model_or_metric_calls(tmp_path):
    """Exercise the actual evaluator with local fakes, without importing LLM/model clients."""
    import ast
    import hashlib
    import json
    import logging
    import os
    import pickle
    from collections import defaultdict
    from datetime import datetime
    from pathlib import Path
    from types import SimpleNamespace
    from typing import Optional

    source = Path(__file__).resolve().parents[1]/'test_advanced_robust.py'
    function = next(node for node in ast.parse(source.read_text(encoding='utf-8')).body
                    if isinstance(node, ast.FunctionDef) and node.name == 'evaluate_dataset')
    dataset = tmp_path/'dataset.json'
    dataset.write_text('[]', encoding='utf-8')
    digest = hashlib.sha256(dataset.read_bytes()).hexdigest()
    cache = tmp_path/f'cached_memories_robust_openai_test_{digest[:12]}'
    cache.mkdir()
    (cache/'memory_cache_sample_0.pkl').write_bytes(pickle.dumps({}))
    (cache/'retriever_cache_sample_0.pkl').write_bytes(b'local fake')
    metadata = dict(dataset_sha256=digest, model='test', retrieve_k=10, seed=42,
                    ratio=1.0, backend='openai', temperature_c5=0.5,
                    refresh_index=False, memory_scope='conversation', legacy_c5_reference=False)
    row = dict(sample_id=0, question_index=0, question='saved question', reference='gold',
               category=1, adversarial_answer=None, prediction='gold',
               metrics=dict(f1=1.0, bleu1=1.0, exact_match=1))
    save_checkpoint(tmp_path/'result_checkpoint.json', metadata, [row], {'reason': 'test'})

    def forbidden(*args, **kwargs):
        pytest.fail('A saved answer triggered a new model or metric call')

    retriever = SimpleNamespace(load=lambda *args: retriever)
    memory = SimpleNamespace(memories={}, retriever=retriever)
    agent = SimpleNamespace(memory_system=memory, answer_question=forbidden)
    qa = SimpleNamespace(question='saved question', category=1,
                         adversarial_answer=None, reference=lambda legacy: 'gold')
    sample = SimpleNamespace(qa=[qa])
    environment = dict(Optional=Optional, datetime=datetime, os=os, Path=Path,
                       hashlib=hashlib, defaultdict=defaultdict, pickle=pickle, json=json,
                       __file__=str(tmp_path/'evaluator.py'), FAILURES={},
                       load_checkpoint=load_checkpoint, save_checkpoint=save_checkpoint,
                       setup_logger=lambda path: logging.getLogger('checkpoint-test'),
                       load_locomo_dataset=lambda path: [sample],
                       RobustAdvancedMemAgent=lambda *args: agent, cache_is_current=lambda path: True,
                       score_prediction=forbidden,
                       aggregate_metrics=lambda metrics, categories: {'overall': {'f1': {'mean': metrics[0]['f1']}}})
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), environment)
    result = environment['evaluate_dataset'](str(dataset), 'test', str(tmp_path/'result.json'),
                                              ratio=1.0, backend='openai')
    assert result['resumed_questions'] == 1
    assert result['individual_results'] == [row]
    assert result['total_questions'] == 1
