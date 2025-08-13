import random
import numpy as np

class Scenarios:
    CLASSICAL = "classical"
    CRYPTIC_ONLY = "cryptic_only"
    HGT_ONLY = "hgt_only"
    BRT = "brt_full"

def run_simulation(
    seed=42,
    n_lineages=500,
    generations=800,
    extinction_period=200,
    extinction_fraction=0.6,
    hgt_rate=0.08,
    cryptic_size=20,
    compatibility_tau=0.5,
    scenario="classical",
    trait_space=2000,
    pool_size=10000,
    recolonization_rate=0.2  # fill at most 20% of empty slots per generation
):
    """
    Memory-safe, fixed carrying capacity. After extinction, diversity recovers
    gradually because only a fraction of empty slots are refilled each generation.
    """
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    def make_lineage(alive=True):
        return {
            "alive": alive,
            "traits": set(np_rng.choice(trait_space, size=5, replace=False)),
            "cryptic": set(np_rng.choice(trait_space*5, size=cryptic_size, replace=False)),
        }

    # fixed gene pool for cheap sampling
    gene_pool = np_rng.choice(pool_size, size=min(pool_size, 5000), replace=False)

    # start at full capacity (fixed-size list)
    lineages = [make_lineage(alive=True) for _ in range(n_lineages)]

    diversity_ts, innov_ts = [], []
    pre_ext = n_lineages
    rec_time = None
    in_window = False
    crossed = False

    def diversity(lst):
        return sum(1 for L in lst if L["alive"])

    for g in range(generations):
        # 1) extinction pulse
        if g > 0 and g % extinction_period == 0:
            for L in lineages:
                if L["alive"] and rng.random() < extinction_fraction:
                    L["alive"] = False
            in_window = True
            crossed = False
            pre_ext = n_lineages

        # 2) recolonization: keep length fixed; fill a fraction of dead slots
        alive = [L for L in lineages if L["alive"]]
        dead  = [L for L in lineages if not L["alive"]]
        new_lineages = alive[:] + dead[:]  # same length as before

        # births allowed this generation
        empty_slots = len(dead)
        births = min(empty_slots, int(round(recolonization_rate * empty_slots)))
        parents = alive if alive else [make_lineage(alive=True)]

        i = 0
        while births > 0 and i < len(new_lineages):
            if not new_lineages[i]["alive"]:
                p = rng.choice(parents)
                c = {
                    "alive": True,
                    "traits": set(p["traits"]),
                    "cryptic": set(p["cryptic"]),
                }
                if scenario in (Scenarios.CRYPTIC_ONLY, Scenarios.BRT) and c["cryptic"] and rng.random() < 0.02:
                    c["traits"].add(rng.choice(tuple(c["cryptic"])))
                if scenario in (Scenarios.HGT_ONLY, Scenarios.BRT) and rng.random() < hgt_rate:
                    for _ in range(rng.randint(1, 2)):
                        tr = int(np_rng.choice(gene_pool))
                        if rng.random() < compatibility_tau:
                            c["traits"].add(tr)
                new_lineages[i] = c
                births -= 1
            i += 1

        # 3) within-generation updates
        for L in new_lineages:
            if not L["alive"]:
                continue
            if scenario in (Scenarios.CRYPTIC_ONLY, Scenarios.BRT) and L["cryptic"] and rng.random() < 0.01:
                L["traits"].add(rng.choice(tuple(L["cryptic"])))
            if scenario in (Scenarios.HGT_ONLY, Scenarios.BRT) and rng.random() < hgt_rate * 0.05:
                tr = int(np_rng.choice(gene_pool))
                if rng.random() < compatibility_tau:
                    L["traits"].add(tr)

        # 4) finalize
        lineages = new_lineages
        d = diversity(lineages)
        diversity_ts.append(d)
        innov_ts.append(sum(max(0, len(L["traits"]) - 5) for L in lineages if L["alive"]))

        if in_window and not crossed and d >= int(0.9 * pre_ext):
            rec_time = (g % extinction_period)
            crossed = True
        if g > 0 and (g + 1) % extinction_period == 0:
            in_window = False

    return {
        "diversity_ts": diversity_ts,
        "innovation_total": innov_ts[-1] if innov_ts else 0,
        "recovery_time_gens": rec_time if rec_time is not None else float("nan"),
    }
