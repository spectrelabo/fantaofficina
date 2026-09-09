#!/usr/bin/env python3
"""
FASE 3 — Scraping infortuni da Transfermarkt (VERSIONE DEMO).

NOTA: versione dimostrativa pubblica — lo scraping reale con cache,
retry e parsing profili vive esclusivamente nel prodotto commerciale
privato. Questo script carica il dataset di esempio incluso nel repo,
senza fare alcuna richiesta HTTP, e pubblica una cache infortuni demo
compatibile con gli stage a valle.
"""

import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from core import config

DEMO_SOURCE = os.path.join(config.EXAMPLES_DIR, "dataset_sample.csv")


def main():
    print("[INFO] Versione demo pubblica: uso dati d'esempio da examples/dataset_sample.csv (nessuna richiesta di rete).")
    df = pd.read_csv(DEMO_SOURCE)
    cache = {
        str(player).strip(): {
            "giorni_infortunio_3y": 0,
            "n_infortuni_3y": 0,
            "infortunio_grave": 0,
        }
        for player in df["player"].dropna().unique()
    }
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(config.INJURIES_CACHE_JSON, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Scritti {len(cache)} record demo (infortuni neutri) in {config.INJURIES_CACHE_JSON}")


if __name__ == "__main__":
    main()
