#!/usr/bin/env python3
"""
FASE 1 — Raccolta dati storici giocatori e squadre Serie A (VERSIONE DEMO).

NOTA: versione dimostrativa pubblica — lo scraping reale multi-fonte
vive esclusivamente nel prodotto commerciale privato. Questo script
carica il dataset di esempio incluso nel repo, così la pipeline resta
eseguibile end-to-end senza fare alcuna richiesta di rete.

Output:
  - storico_giocatori_raw.csv
  - storico_giocatori_aggregato.csv
"""

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from core import config

DEMO_SOURCE = os.path.join(config.EXAMPLES_DIR, "dataset_sample.csv")


def main():
    print("[INFO] Versione demo pubblica: uso dati d'esempio da examples/dataset_sample.csv (nessuna richiesta di rete).")
    df = pd.read_csv(DEMO_SOURCE)
    os.makedirs(config.DATA_DIR, exist_ok=True)
    df.to_csv(config.STORICO_RAW_CSV, index=False, encoding="utf-8-sig")
    df.to_csv(config.STORICO_AGG_CSV, index=False, encoding="utf-8-sig")
    print(f"[INFO] Scritti {len(df)} record demo in {config.STORICO_RAW_CSV} e {config.STORICO_AGG_CSV}")


if __name__ == "__main__":
    main()
