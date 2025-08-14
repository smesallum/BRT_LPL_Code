# BRT Simulation Reproducibility
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16862739.svg)](https://doi.org/10.5281/zenodo.16862739)
## Quick start (Windows PowerShell)
1. python -m venv .venv
2. .\.venv\Scripts\Activate.ps1
3. pip install -r requirements.txt
4. python scripts\run_experiments.py --generations 900 --extinction_period 300 --extinction_fraction 0.5 --recolonization_rate 0.4 --n_lineages 400 --reps 3 --no_figure

Outputs written to:
- results/summary_table.csv
- results/raw/*
- results/figure2a_like.png (omit if --no_figure used)
- results/RUN_LOG.txt
- results/RUN_TIMESTAMP.txt

## Data & Code Availability
All simulation code is in this repository. Raw per-replicate time series and summary tables are produced by scripts/run_experiments.py into the results/ folder. The exact command used for the revision is recorded in results/RUN_LOG.txt with a timestamp in results/RUN_TIMESTAMP.txt.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16862739.svg)](https://doi.org/10.5281/zenodo.16862739)

