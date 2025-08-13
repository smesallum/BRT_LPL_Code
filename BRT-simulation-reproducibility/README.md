# BRT Simulation Reproducibility
Minimal Python implementation to reproduce qualitative results.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/run_experiments.py
```
Outputs will be written to `results/`:
- `summary_table.csv` (medians + 95% CIs)
- `raw/*.csv` (per-replicate diversity time series)
- `figure2a_like.png` (BRT vs Classical diversity)
