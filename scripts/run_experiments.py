import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import argparse, csv
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from brt_sim import run_simulation, Scenarios

def main():
    p = argparse.ArgumentParser(description="Run BRT simulations and save results.")
    p.add_argument("--generations", type=int, default=800)
    p.add_argument("--reps", type=int, default=3)
    p.add_argument("--n_lineages", type=int, default=400)
    p.add_argument("--extinction_period", type=int, default=200)
    p.add_argument("--extinction_fraction", type=float, default=0.6)
    p.add_argument("--hgt_rate", type=float, default=0.08)
    p.add_argument("--cryptic_size", type=int, default=20)
    p.add_argument("--compatibility_tau", type=float, default=0.5)
    p.add_argument("--recolonization_rate", type=float, default=0.2)
    p.add_argument("--no_figure", action="store_true")
    args = p.parse_args()

    os.makedirs("results", exist_ok=True)
    os.makedirs("results/raw", exist_ok=True)

    scenarios = [Scenarios.CLASSICAL, Scenarios.CRYPTIC_ONLY, Scenarios.HGT_ONLY, Scenarios.BRT]
    summary, ts_data = [], {}

    for sc in scenarios:
        rec, innov = [], []
        for r in range(args.reps):
            out = run_simulation(
                seed=100 + r,
                scenario=sc,
                generations=args.generations,
                n_lineages=args.n_lineages,
                extinction_period=args.extinction_period,
                extinction_fraction=args.extinction_fraction,
                hgt_rate=args.hgt_rate,
                cryptic_size=args.cryptic_size,
                compatibility_tau=args.compatibility_tau,
                recolonization_rate=args.recolonization_rate,
            )
            with open(f"results/raw/{sc}_rep{r}_diversity.csv","w",newline="") as fh:
                w=csv.writer(fh); w.writerow(["generation","diversity_alive_lineages"])
                for g,d in enumerate(out["diversity_ts"]): w.writerow([g,d])
            rec.append(out["recovery_time_gens"]); innov.append(out["innovation_total"])
            ts_data[sc]=out["diversity_ts"]

        summary.append({
            "scenario": sc,
            "recovery_time_median_gens": float(np.nanmedian(rec)),
            "CI95_low": float(np.nanpercentile(rec,2.5)),
            "CI95_high": float(np.nanpercentile(rec,97.5)),
            "innovation_total_median": float(np.nanmedian(innov))
        })

    df = pd.DataFrame(summary)
    baseline = df.loc[df["scenario"]==Scenarios.CLASSICAL,"innovation_total_median"].values[0]
    df["novel_traits_index_relative"] = np.where(baseline>0, df["innovation_total_median"]/baseline, np.nan)
    df.to_csv("results/summary_table.csv", index=False)
    print(df.to_string(index=False))

    if not args.no_figure and Scenarios.BRT in ts_data and Scenarios.CLASSICAL in ts_data:
        plt.figure()
        x=list(range(len(ts_data[Scenarios.BRT])))
        plt.plot(x, ts_data[Scenarios.BRT], label="BRT")
        plt.plot(x, ts_data[Scenarios.CLASSICAL], label="Classical")
        plt.xlabel("Generations"); plt.ylabel("Diversity (alive lineages)")
        plt.legend(); plt.tight_layout()
        plt.savefig("results/figure2a_like.png", dpi=200)

if __name__ == "__main__":
    main()
