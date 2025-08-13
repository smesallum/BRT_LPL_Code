import os, csv, numpy as np, pandas as pd, matplotlib.pyplot as plt
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
            for g,d in enumerate(out['diversity_ts']): w.writerow([g,d])
        rec.append(out['recovery_time_gens']); innov.append(out['innovation_total'])
        ts_data[sc]=out['diversity_ts']
    med_rec=float(np.nanmedian(rec)); ci_low=float(np.nanpercentile(rec,2.5)); ci_high=float(np.nanpercentile(rec,97.5))
    med_innov=float(np.nanmedian(innov))
    summary.append({'scenario':sc,'recovery_time_median_gens':med_rec,'CI95_low':ci_low,'CI95_high':ci_high,'innovation_total_median':med_innov})
df=pd.DataFrame(summary)
baseline=df.loc[df['scenario']==Scenarios.CLASSICAL,'innovation_total_median'].values[0]
df['novel_traits_index_relative']=df['innovation_total_median']/max(baseline,1e-9)
df.to_csv('results/summary_table.csv', index=False)
import matplotlib.pyplot as plt
plt.figure(); x=list(range(len(ts_data[Scenarios.BRT])))
plt.plot(x, ts_data[Scenarios.BRT], label='BRT'); plt.plot(x, ts_data[Scenarios.CLASSICAL], label='Classical')
plt.xlabel('Generations'); plt.ylabel('Diversity (alive lineages)'); plt.legend(); plt.tight_layout()
plt.savefig('results/figure2a_like.png', dpi=200)
print(df.to_string(index=False))
