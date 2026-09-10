# Spectre - FantaMoneyball — Quantitative Fantasy Football & League Analytics Framework

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/License-PolyForm--Noncommercial--1.0.0-blue.svg)](LICENSE)
[![ML: Quantile Regression](https://img.shields.io/badge/ML-Quantile%20Regression%20(demo)-yellow.svg)](docs/MODEL_INTERPRETABILITY.md)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-yellow.svg?logo=buy-me-a-coffee)](https://buymeacoffee.com/blueskies360)

A modular, data-driven pipeline for data extraction, probabilistic points projection, and
sabermetric-style valuation (VORP) for fantasy football auctions (Fantacalcio Serie A).

📖 **Model Interpretability Guide**: [docs/MODEL_INTERPRETABILITY.md](docs/MODEL_INTERPRETABILITY.md)

## Demo positioning

**This is a public demonstration build.** Data ingestion (historical stats and injury
scraping) is real, but the points projection and pricing formulas are intentionally
simplified for teaching purposes. The full product — real machine learning models
(quantile regression), refined VORP pricing, post-draft audit engine, trade analyzer,
lineup optimizer, and AI copilot — is a private commercial product, not distributed here.

Se questo progetto ti è stato utile, o semplicemente ti piace l'idea, una donazione aiuta a
mantenerlo open source: [Buy Me A Coffee](https://buymeacoffee.com/blueskies360).

## The problem this framework addresses

Every pre-season, fantasy managers sit at the draft table trusting gut feeling over data.
The typical result: overpaying for media-hyped names, ignoring injury-prone assets, and
leaving budget on the table for players who never earn their price back. `Spectre -
FantaMoneyball` replaces intuition with a reproducible, data-driven pipeline: ingest
historical performance, project expected points, and translate that into a fair auction
price — so decisions are grounded in numbers, not hype.

## Features available in this branch

- Real historical & injury data scraping (fantacalcio.it, football-data.co.uk, Transfermarkt)
- Simplified points projection and VORP-style auction pricing (demo heuristics, not the
  production ML models)
- Excel workbook generation for the produced outputs
- Local web interface for exploring the base auction workflow
- Zero-config interactive terminal demo (`demo.py`) using bundled sample data

## Interactive demo (zero-config)

You don't need to scrape any data to see the pipeline in action:

```bash
python demo.py
```

It runs directly on `examples/dataset_sample.csv` and shows the projection/pricing workflow
end to end.

## Repository structure

- `core/ingestion/static/` — ingestion (real scraping for historical stats and injuries),
  pricing, and export pipeline scripts
- `core/config.py` and related config files — runtime configuration
- `run_pipeline.py` — executes the full pipeline flow
- `web/app.py` — starts the local web interface
- `demo.py` — zero-config interactive terminal demo
- `examples/dataset_sample.csv` — bundled sample dataset for the demo
- `tests/` — regression coverage for the public modules

## Installation

```bash
pip install -r requirements.txt
```

## Run locally

```bash
python run_pipeline.py
python web/app.py
```

## Documentation

- `docs/MODEL_INTERPRETABILITY.md` — plain-language overview of the demo logic
- `docs/pipeline_architecture.md` — pipeline stages and data flow
- `docs/data_sources.md` — data sources used by the ingestion scripts

## License

This repository is distributed under the license currently included in [`LICENSE`](LICENSE)
(PolyForm Noncommercial 1.0.0).
