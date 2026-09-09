"""Thin wrapper attorno a fanta_lab_engine.predict_points, con fallback demo."""

import pandas as pd

try:
    from fanta_lab_engine import predict_points as _engine_predict_points
except ImportError:
    _engine_predict_points = None


def apply_quantile_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """Applica le predizioni quantile, usando l'engine se disponibile, demo altrimenti."""
    if _engine_predict_points is not None:
        try:
            return _engine_predict_points(df)
        except AttributeError:
            print("  [WARNING] fanta_lab_engine versione incompatibile, fallback a dati demo")

    print("  [INFO] fanta_lab_engine non disponibile: uso valori demo da examples/dataset_sample.csv")
    df = df.copy()
    df["predicted_pts_p10"] = 0.0
    df["predicted_pts_p50"] = 0.0
    df["predicted_pts_p90"] = 0.0
    df["pts_volatility_spread"] = 0.0
    return df
