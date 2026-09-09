"""Thin wrapper attorno a fanta_lab_engine.compute_vorp, con fallback demo."""

import pandas as pd

try:
    from fanta_lab_engine import compute_vorp as _engine_compute_vorp
except ImportError:
    _engine_compute_vorp = None


def apply_vorp_pricing(df: pd.DataFrame) -> pd.DataFrame:
    """Applica VORP e fair pricing, usando l'engine se disponibile, demo altrimenti."""
    if _engine_compute_vorp is not None:
        try:
            return _engine_compute_vorp(df)
        except AttributeError:
            print("  [WARNING] fanta_lab_engine versione incompatibile, fallback a dati demo")

    print("  [INFO] fanta_lab_engine non disponibile: uso valori demo da examples/dataset_sample.csv")
    df = df.copy()
    df["vorp_points"] = 0.0
    df["prezzo_fair_1000"] = df.get("Prezzo_Consigliato_Cr", pd.Series(1.0, index=df.index))
    df["prezzo_fair_500"] = df["prezzo_fair_1000"] / 2
    df["surplus_value_cr"] = 0
    return df
