import os
import sys
import types

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_wrapper_falls_back_to_demo_when_engine_missing(monkeypatch, tmp_path, capsys):
    # Simula l'assenza del pacchetto fanta_lab_engine
    monkeypatch.setitem(sys.modules, "fanta_lab_engine", None)

    import importlib
    import core.ingestion.static.quantile_points_wrapper as wrapper_mod  # nome interno, vedi Step 3
    importlib.reload(wrapper_mod)

    df_in = pd.DataFrame({
        "player": ["Player A"],
        "role": ["A"],
        "team": ["INT"],
        "FVM_1000": [50.0],
        "Prezzo_Consigliato_Cr": [30.0],
    })

    df_out = wrapper_mod.apply_quantile_predictions(df_in)

    assert "predicted_pts_p50" in df_out.columns
    captured = capsys.readouterr()
    assert "fanta_lab_engine non disponibile" in captured.out


def test_wrapper_uses_engine_when_available(monkeypatch):
    fake_engine = types.ModuleType("fanta_lab_engine")

    def fake_predict_points(df):
        df = df.copy()
        df["predicted_pts_p50"] = 999.0
        return df

    fake_engine.predict_points = fake_predict_points
    monkeypatch.setitem(sys.modules, "fanta_lab_engine", fake_engine)

    import importlib
    import core.ingestion.static.quantile_points_wrapper as wrapper_mod
    importlib.reload(wrapper_mod)

    df_in = pd.DataFrame({"player": ["Player A"], "role": ["A"]})
    df_out = wrapper_mod.apply_quantile_predictions(df_in)

    assert (df_out["predicted_pts_p50"] == 999.0).all()
