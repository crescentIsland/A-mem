"""Create a report figure from the saved three-round measurements."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

data = json.loads((ROOT/'submission/measurements.json').read_text(encoding='utf-8'))
fig, axes = plt.subplots(1,3,figsize=(11,4.2))
panels = [('Overall F1','quality','f1',100,60,'F1 (%)'),
          ('Answerable-question F1','quality','non_adversarial_f1',100,60,'F1 (%)'),
          ('QA token usage','costs','qa_tokens_per_question',1,16000,'Tokens / question')]
for ax,(title,group,metric,scale,maximum,label) in zip(axes,panels):
    stats = [data['aggregate'][k][group][metric] for k in ('10','5')]
    means = [s['mean']*scale for s in stats]
    errors = [s['sample_sd']*scale for s in stats]
    ax.bar(['k=10','k=5'],means,yerr=errors,capsize=5,color=['#31688e','#e58a38'],width=0.55)
    for index,(value,error) in enumerate(zip(means,errors)):
        text = f'{value:,.0f} ± {error:.0f}' if metric.endswith('question') else f'{value:.2f} ± {error:.2f}'
        ax.text(index,value+error+maximum*0.035,text,ha='center',fontsize=9)
    ax.set(title=title,ylabel=label,ylim=(0,maximum))
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',alpha=0.15)
    ax.set_axisbelow(True)
fig.suptitle('A-MEM: retrieval budget, answer quality and token usage',fontsize=14)
fig.text(0.5,0.025,'Mean ± sample SD across 3 runs per setting; same 199 questions and fixed memory. No equivalence claim.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,0.07,1,0.91))
fig.savefig(ROOT/'submission/quality_cost.png',dpi=220)
fig.savefig(ROOT/'submission/quality_cost.svg')
print('Saved submission/quality_cost.png and quality_cost.svg from measured data.')
