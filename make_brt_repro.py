import os, csv, textwrap
from datetime import datetime

def write(path, text):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

# metadata & docs
write("LICENSE", "MIT License (c) 2025 Sameh Muslim\n")
write("CITATION.cff",
      "cff-version: 1.2.0\n"
      "title: BRT Simulation Reproducibility\n"
      f"date-released: {datetime.utcnow().date()}\n"
      "license: MIT\n"
      "authors:\n"
      "  - family-names: Muslim\n"
      "    given-names: Sameh\n")
write("requirements.txt", "numpy\npandas\nmatplotlib\n")
write("README.md", textwrap.dedent(
    "BRT Simulation Reproducibility\n\n"
    "Quick start\n"
    "  python -m venv .venv\n"
    "  .venv\\Scripts\\activate\n"
    "  pip install -r requirements.txt\n"
    "  python scripts\\run_experiments.py\n"
))

# parameter table
import pandas as pd
os.makedirs("data", exist_ok=True)
pd.DataFrame([
    {"parameter":"N_lineages","value":500,"notes":"Initial number of lineages"},
    {"parameter":"mu","value":1e-8,"notes":"Conceptual base mutation rate"},
    {"parameter":"H_min","value":0.05,"notes":"HGT min (per lineage per period)"},
    {"parameter":"H_max","value":0.30,"notes":"HGT max (per lineage per period)"},
    {"parameter":"cryptic_min","value":20,"notes":"Cryptic pool min"},
    {"parameter":"cryptic_max","value":50,"notes":"Cryptic pool max"},
    {"parameter":"compatibility_tau","value":0.5,"notes":"Compatibility filter (0-1)"}
]).to_csv("data/Supplementary_Table_S1.csv", index=False)

# package code
write("brt_sim/__init__.py", "from .model import run_simulation, Scenarios\n")
write("brt_sim/model.py", textwrap.dedent(
"""import random, numpy as np

class Scenarios:
    CLASSICAL='classical'; CRYPTIC_ONLY='cryptic_only'; HGT_ONLY='hgt_only'; BRT='brt_full'

def run_simulation(seed=42, n_lineages=500, generations=1200, extinction_period=300, extinction_fraction=0.6,
                   hgt_rate=0.1, cryptic_size=30, compatibility_tau=0.5, scenario='classical'):
    rng = random.Random(seed); np_rng = np.random.default_rng(seed)

    def make_lineage():
        return {'alive':True,
                'traits':set(np_rng.choice(1000, size=5, replace=False)),
                'cryptic':set(np_rng.choice(5000, size=cryptic_size, replace=False))}

    lineages=[make_lineage() for _ in range(n_lineages)]
    gene_pool=set(np_rng.choice(100000, size=5000, replace=False))

    diversity_ts=[]; innov_ts=[]
    pre_ext=n_lineages; rec_time=None; in_window=False; crossed=False

    def diversity(): return sum(1 for L in lineages if L['alive'])

    for g in range(generations):
        # extinction pulse
        if g>0 and g%extinction_period==0:
            alive=[L for L in lineages if L['alive']]
            for L in alive[:int(len(alive)*extinction_fraction)]: L['alive']=False
            in_window=True; crossed=False

        # recolonization
        dead_slots=sum(1 for L in lineages if not L['alive'])
        alive=[L for L in lineages if L['alive']]
        for _ in range(dead_slots):
            if not alive: break
            p=rng.choice(alive)
            c={'alive':True,'traits':set(p['traits']),'cryptic':set(p['cryptic'])}
            # cryptic activation
            if scenario in (Scenarios.CRYPTIC_ONLY, Scenarios.BRT) and rng.random()<0.02 and c['cryptic']:
                c['traits'].add(rng.choice(tuple(c['cryptic'])))
            # lateral acquisition
            if scenario in (Scenarios.HGT_ONLY, Scenarios.BRT) and rng.random()<hgt_rate:
                for _ in range(rng.randint(1,3)):
                    tr=rng.choice(tuple(gene_pool))
                    if rng.random()<compatibility_tau: c['traits'].add(tr)
            lineages.append(c)

        # within-generation updates
        for L in lineages:
            if not L['alive']: continue
            if scenario in (Scenarios.CRYPTIC_ONLY, Scenarios.BRT) and rng.random()<0.01 and L['cryptic']:
                L['traits'].add(rng.choice(tuple(L['cryptic'])))
            if scenario in (Scenarios.HGT_ONLY, Scenarios.BRT) and rng.random()<hgt_rate*0.05:
                tr=rng.choice(tuple(gene_pool))
                if rng.random()<compatibility_tau: L['traits'].add(tr)

        d=diversity(); diversity_ts.append(d)
        innov_ts.append(sum(max(0,len(L['traits'])-5) for L in lineages if L['alive']))

        if in_window and not crossed and d>=int(0.9*pre_ext):
            rec_time=(g%extinction_period); crossed=True

        if g>0 and (g+1)%extinction_period==0:
            in_window=False; pre_ext=d

    return {'diversity_ts':diversity_ts,
            'innovation_total':innov_ts[-1] if innov_ts else 0,
            'recovery_time_gens':rec_time or float('nan')}
"""))

# runner
write("scripts/run_experiments.py", textwrap.dedent(
"""import os, csv, numpy as np, pandas as pd, matplotlib.pyplot as plt
from brt_sim import run_simulation, Scenarios

os.makedirs('results', exist_ok=True); os.makedirs('results/raw', exist_ok=True)

reps=3
scenarios=[Scenarios.CLASSICAL, Scenarios.CRYPTIC_ONLY, Scenarios.HGT_ONLY, Scenarios.BRT]
summary=[]; ts_data={}

for sc in scenarios:
    rec=[]; innov=[]
    for r in range(reps):
        out=run_simulation(seed=100+r, scenario=sc)
        with open(f'results/raw/{sc}_rep{r}_diversity.csv','w',newline='') as fh:
            w=csv.writer(fh); w.writerow(['generation','diversity_alive_lineages'])
            for g,d in enumerate(out['diversity_ts']):
                w.writerow([g,d])
        rec.append(out['recovery_time_gens']); innov.append(out['innovation_total'])
        ts_data[sc]=out['diversity_ts']

    med_rec=float(np.nanmedian(rec))
    ci_low=float(np.nanpercentile(rec,2.5))
    ci_high=float(np.nanpercentile(rec,97.5))
    med_innov=float(np.nanmedian(innov))
    summary.append({'scenario':sc,
                    'recovery_time_median_gens':med_rec,
                    'CI95_low':ci_low,'CI95_high':ci_high,
                    'innovation_total_median':med_innov})

df=pd.DataFrame(summary)
baseline=df.loc[df['scenario']==Scenarios.CLASSICAL,'innovation_total_median'].values[0]
df['novel_traits_index_relative']=df['innovation_total_median']/max(baseline,1e-9)
df.to_csv('results/summary_table.csv', index=False)

plt.figure()
x=list(range(len(ts_data[Scenarios.BRT])))
plt.plot(x, ts_data[Scenarios.BRT], label='BRT')
plt.plot(x, ts_data[Scenarios.CLASSICAL], label='Classical')
plt.xlabel('Generations'); plt.ylabel('Diversity (alive lineages)')
plt.legend(); plt.tight_layout()
plt.savefig('results/figure2a_like.png', dpi=200)
print(df.to_string(index=False))
"""))

print("OK: files created")
