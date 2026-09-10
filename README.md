# Spectre - FantaMoneyball — Quantitative Fantasy Football & League Analytics Framework

[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/License-PolyForm--Noncommercial--1.0.0-blue.svg)](LICENSE)

Public demo version of a quantitative fantasy football and league analytics framework.

## Demo positioning

This is a demonstrative public build focused on showing the end-to-end workflow with bundled sample data and simplified heuristics.

**Questa è una versione dimostrativa con dati ed euristiche semplificate a scopo didattico. La versione completa (dati reali, modelli di machine learning, moduli di analisi avanzata) è un prodotto commerciale privato — non distribuita pubblicamente.**

## Features available in this branch

- Base auction pricing workflow for fantasy football analysis
- Real historical & injury data scraping (fantacalcio.it, football-data.co.uk, Transfermarkt); pricing/valuation formulas remain simplified for demo purposes
- Excel workbook generation for the produced outputs
- Local web interface for exploring the demo build

## Repository structure

- `core/ingestion/static/` — ingestion (real scraping for historical stats and injuries), pricing, and export pipeline scripts
- `core/config.py` and related config files — runtime configuration
- `run_pipeline.py` — executes the pipeline flow
- `web/app.py` — starts the local web interface
- `tests/` — regression coverage for the remaining public modules

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

## License

This repository is distributed under the license currently included in `LICENSE`.
