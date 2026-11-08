"""Replay saved experiment evidence for a presentation; no API or model imports."""
import argparse
import hashlib
import json
import statistics
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT/'submission'


def load_evidence():
    summary = json.loads((PACKAGE/'measurements.json').read_text(encoding='utf-8'))
    assert summary['complete'] and summary['completed_runs'] == 6
    runs = {}
    first = None
    for spec in summary['runs']:
        path = PACKAGE/spec['data_file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == spec['data_sha256'], f'Changed data: {path.name}'
        data = json.loads(path.read_text(encoding='utf-8'))
        assert len(data['individual_results']) == data['total_questions'] == 199
        assert data['dataset_sha256'] == summary['dataset_sha256']
        assert abs(statistics.mean(q['metrics']['f1'] for q in data['individual_results'])-spec['quality']['f1']) < 1e-9
        if first is None:
            first = data['individual_results']
        for a, b in zip(first, data['individual_results']):
            assert all(a[key] == b[key] for key in ('question','category','reference'))
        runs[(spec['round'],spec['k'])] = data['individual_results']
    assert len(runs) == 6
    return summary, runs


def show_summary(summary):
    print('\n[1] Three measured rounds: the same 419 memory notes and 199 questions; three runs per setting.')
    for k in ('10','5'):
        data = summary['aggregate'][k]
        f1 = data['quality']['f1']
        tokens = data['costs']['qa_tokens_per_question']
        print(f"k={k}: F1={f1['mean']*100:.2f}% +/- {f1['sample_sd']*100:.2f} percentage points; tokens/question={tokens['mean']:.1f} +/- {tokens['sample_sd']:.1f}")
    difference = summary['paired']['quality_k5_minus_k10']['f1']['mean']*100
    saving = summary['paired']['token_reduction_fraction']['mean']*100
    print(f'k=5 minus k=10: F1 difference {difference:+.2f} percentage points; token reduction {saving:.2f}%.')
    print('F1 measures lexical overlap; it is not the percentage of questions answered correctly.')


def show_case(runs, index, label, explanation):
    first = runs[(1,10)][index]
    print(f'\n[{label}] Question: {first["question"]}')
    print('Reference:',first['reference'])
    for number in (1,2,3):
        print(f'Round {number}:')
        for k in (10,5):
            row = runs[(number,k)][index]
            print(f'  k={k}: {row["prediction"]}    F1={row["metrics"]["f1"]:.3f}')
    print('Interpretation: '+explanation)


def say(text):
    print(textwrap.fill(text, width=76))


def presentation_case(runs, number):
    index = 10 if number == 1 else 155
    first = runs[(1,10)][index]
    print('\n' + '='*76)
    print(f'SAVED EXPERIMENT RESULTS | CASE {number} OF 2')
    print('='*76)
    say('Question: ' + first['question'])
    say('Reference answer: ' + str(first['reference']))
    print()
    if number == 1:
        print(f"{'Round':<7}{'k=10 answer':<19}k=5 answer")
        print('-'*60)
        for round_number in (1,2,3):
            a = runs[(round_number,10)][index]['prediction']
            b = runs[(round_number,5)][index]['prediction']
            print(f'{round_number:<7}{a:<19}{b}')
    else:
        print('EXAMPLE ANSWERS (ROUND 1)')
        for k in (10,5):
            say(f"k={k}: {runs[(1,k)][index]['prediction']}")
        print('\nCONSISTENCY ACROSS ALL THREE ROUNDS')
        print(f"{'Setting':<12}{'Correct abstention':<25}Mean F1 for this question")
        print('-'*66)
        for k in (10,5):
            rows = [runs[(r,k)][index] for r in (1,2,3)]
            correct = sum(row['metrics']['adversarial_correct'] for row in rows)
            score = statistics.mean(row['metrics']['f1'] for row in rows)
            print(f"{f'k={k}':<12}{f'{correct}/3 rounds':<25}{score:.3f}")
    if number == 1:
        print('\nTHIS QUESTION ONLY')
        for k in (10,5):
            rows = [runs[(r,k)][index] for r in (1,2,3)]
            exact = sum(row['metrics']['exact_match'] for row in rows)
            print(f"k={k}: exact reference matches in {exact}/3 rounds; mean F1={statistics.mean(row['metrics']['f1'] for row in rows):.3f}")
        print('\nTAKEAWAY')
        say('k=10 consistently gives the correct duration. k=5 misses this key detail. This is one example, not the overall experiment score.')
    else:
        print('\nTAKEAWAY')
        say('The agency information concerns Caroline, but the question asks about Melanie. k=10 applies another person\'s reason; k=5 correctly says the answer is not mentioned.')
        say('More context did not guarantee correct person attribution in this example.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--section',choices=['all','summary','coverage','refusal','metric'],default='all')
    parser.add_argument('--pause',action='store_true',help='Press Enter between sections during a recording.')
    parser.add_argument('--verify',action='store_true',help='Validate packaged measurements and exit.')
    parser.add_argument('--presentation',action='store_true',help='Show only the two recording cases, with concise tables and one pause.')
    parser.add_argument('--no-pause',action='store_true',help='Show presentation cases without waiting for Enter.')
    args = parser.parse_args()
    summary,runs = load_evidence()
    if args.presentation and not args.verify:
        print('A-MEM | Verified saved results | No live model call')
        presentation_case(runs,1)
        if not args.no_pause:
            input('\nExplain this case, then press Enter for case 2...')
        presentation_case(runs,2)
        print('\nDEMO COMPLETE: return to slide 8 for limitations and conclusions.')
        return
    print('A-MEM measured-result replay: saved experimental evidence, not live model inference. No API requests.')
    print('Verified: six data-file SHA256 hashes, paired questions, and aggregate F1 scores.')
    if args.verify:
        return
    sections = {
        'summary':lambda:show_summary(summary),
        'coverage':lambda:show_case(runs,10,'2 Missing a key detail','k=10 answered 4 years in all three rounds; k=5 did not give the correct duration. The inspected round-three contexts also differed in direct evidence coverage.'),
        'refusal':lambda:show_case(runs,155,'3 Person attribution and abstention','The question asks about Melanie, but the agency information concerns Caroline. k=10 misattributed it in all three rounds; k=5 correctly abstained.'),
        'metric':lambda:show_case(runs,83,'4 Metric limitation','Taking care of our minds is semantically related to self-care, but receives lexical F1=0. A lexical score is not a direct measure of factual correctness.'),
    }
    keys = list(sections) if args.section == 'all' else [args.section]
    for i,key in enumerate(keys):
        if i and args.pause:
            input('\nPress Enter for the next section...')
        sections[key]()


if __name__ == '__main__':
    main()
