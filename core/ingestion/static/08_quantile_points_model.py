#!/usr/bin/env python3
"""
STAGE 8 — Quantile Regression Points Modeling (P10 Floor, P50 Expected, P90 Ceiling).

Le formule di training/predizione vivono nel pacchetto privato fanta_lab_engine.
Questo script è un thin wrapper: carica il dataset, applica le predizioni
(engine se disponibile, altrimenti valori demo), salva il risultato.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import config
from core.ingestion.static.quantile_points_wrapper import apply_quantile_predictions

import pandas as pd


def main():
    print("=" * 60)
    print("  STAGE 8 — QUANTILE REGRESSION (FLOOR / EXPECTED / CEILING)")
    print("=" * 60)

    if not os.path.exists(config.DATASET_FINALE_CSV):
        raise FileNotFoundError(f"Missing {config.DATASET_FINALE_CSV}.")

    df_active = pd.read_csv(config.DATASET_FINALE_CSV)
    df_predicted = apply_quantile_predictions(df_active)

    df_predicted.to_csv(config.DATASET_FINALE_CSV, index=False, encoding="utf-8-sig")
    print(f"\n  Updated dataset with quantile projections: {config.DATASET_FINALE_CSV}")

    print("\n  TOP ATTACKERS QUANTILE PROJECTIONS (P10 / P50 / P90):")
    top_a = df_predicted[df_predicted["role"] == "A"].sort_values("predicted_pts_p50", ascending=False).head(8)
    for _, r in top_a.iterrows():
        print(f"    {r['player']:<20} Sq:{str(r['team']):<4} "
              f"Floor(P10):{r['predicted_pts_p10']:>5.1f} | Expected(P50):{r['predicted_pts_p50']:>5.1f} | "
              f"Ceiling(P90):{r['predicted_pts_p90']:>5.1f} | Spread: {r['pts_volatility_spread']:>4.1f} pts")

    print("\n  STAGE 8 COMPLETED.\n")


if __name__ == "__main__":
    main()
