#!/usr/bin/env python3
"""
STAGE 9 — Positional Market Hierarchy & Power-Law Fair Auction Valuation Engine.

Le formule VORP/fair-pricing vivono nel pacchetto privato fanta_lab_engine.
Questo script è un thin wrapper: carica il dataset, applica il pricing
(engine se disponibile, altrimenti valori demo), salva i tre CSV di output.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import config
from core.ingestion.static.vorp_pricing_wrapper import apply_vorp_pricing

import pandas as pd


def main():
    print("=" * 60)
    print("  STAGE 9 — POSITIONAL MARKET FAIR AUCTION PRICING ENGINE")
    print("=" * 60)

    if not os.path.exists(config.DATASET_FINALE_CSV):
        raise FileNotFoundError(f"Missing {config.DATASET_FINALE_CSV}.")

    df = pd.read_csv(config.DATASET_FINALE_CSV)

    if "predicted_pts_p50" not in df.columns:
        print("  Running Stage 8 quantile modeling first...")
        import importlib
        mod08 = importlib.import_module("core.ingestion.static.08_quantile_points_model")
        mod08.main()
        df = pd.read_csv(config.DATASET_FINALE_CSV)

    df_priced = apply_vorp_pricing(df)

    df_priced.to_csv(config.DATASET_FINALE_CSV, index=False, encoding="utf-8-sig")

    path_500 = os.path.join(config.DATA_DIR, "dataset_finale_500.csv")
    df_500 = df_priced.copy()
    df_500["prezzo_fair"] = df_500["prezzo_fair_500"]
    df_500.to_csv(path_500, index=False, encoding="utf-8-sig")

    path_1000 = os.path.join(config.DATA_DIR, "dataset_finale_1000.csv")
    df_1000 = df_priced.copy()
    df_1000["prezzo_fair"] = df_1000["prezzo_fair_1000"]
    df_1000.to_csv(path_1000, index=False, encoding="utf-8-sig")

    print(f"\n  Updated Master Dataset: {config.DATASET_FINALE_CSV}")
    print(f"  Exported 500cr Dataset: {path_500}")
    print(f"  Exported 1000cr Dataset: {path_1000}")

    print("\n  STAGE 9 COMPLETED.\n")


if __name__ == "__main__":
    main()
