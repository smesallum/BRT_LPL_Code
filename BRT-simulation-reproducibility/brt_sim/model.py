import random, numpy as np
class Scenarios:
    CLASSICAL='classical'; CRYPTIC_ONLY='cryptic_only'; HGT_ONLY='hgt_only'; BRT='brt_full'
def run_simulation(seed=42, n_lineages=500, generations=1200, extinction_period=300, extinction_fraction=0.6,
                   hgt_rate=0.1, cryptic_size=30, compatibility_tau=0.5, scenario='classical'):
    rng = random.Random(seed); np_rng = np.random.default_rng(seed)
    def make_lineage():
        return {'alive':True,'traits':set(np_rng.choice(1000, size=5, replace=False)),
                'cryptic':set(np_rng.choice(5000, size=cryptic_size, replace=False))}
    lineages=[make_lineage() for _ in range(n_lineages)]
    gene_pool=set(np_rng.choice(100000, size=5000, replace=False))
    diversity_ts=[]; innov_ts=[]
    pre_ext=n_lineages; rec_time=None; in_window=False; crossed=False
    def diversity(): return sum(1 for L in lineages if L['alive'])
    for g in range(generations):
        if g>0 and g%extinction_period==0:
            alive=[L for L in lineages if L['alive']]
            for L in alive[:int(len(alive)*extinction_fraction)]: L['alive']=False
            in_window=True; crossed=False
        dead_slots=sum(1 for L in lineages if not L['alive'])
        alive=[L for L in lineages if L['alive']]
        for _ in range(dead_slots):
            if not alive: break
            p=rng.choice(alive)
            c={'alive':True,'traits':set(p['traits']),'cryptic':set(p['cryptic'])}
            if scenario in (Scenarios.CRYPTIC_ONLY, Scenarios.BRT) and rng.random()<0.02 and c['cryptic']:
                c['traits'].add(rng.choice(tuple(c['cryptic'])))
            if scenario in (Scenarios.HGT_ONLY, Scenarios.BRT) and rng.random()<hgt_rate:
                for _ in range(rng.randint(1,3)):
                    tr=rng.choice(tuple(gene_pool))
                    if rng.random()<compatibility_tau: c['traits'].add(tr)
            lineages.append(c)
        for L in lineages:
            if not L['alive']: continue
            if scenario in (Scenarios.CRYPTIC_ONLY, Scenarios.BRT) and rng.random()<0.01 and L['cryptic']:
                L['traits'].add(rng.choice(tuple(L['cryptic'])))
            if scenario in (Scenarios.HGT_ONLY, Scenarios.BRT) and rng.random()<hgt_rate*0.05:
                tr=rng.choice(tuple(gene_pool))
                if rng.random()<compatibility_tau: L['traits'].add(tr)
        d=diversity(); diversity_ts.append(d)
        innov_ts.append(sum(max(0,len(L['traits'])-5) for L in lineages if L['alive']))
        if in_window and not crossed and d>=int(0.9*pre_ext): rec_time=(g%extinction_period); crossed=True
        if g>0 and (g+1)%extinction_period==0:
            in_window=False; pre_ext=d
    return {'diversity_ts':diversity_ts,'innovation_total':innov_ts[-1] if innov_ts else 0,'recovery_time_gens':rec_time or float('nan')}
