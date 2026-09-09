import os
import sys
import types

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_wrapper_falls_back_to_demo_when_engine_missing(monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "fanta_lab_engine", None)

    import importlib
    import core.ingestion.static.vorp_pricing_wrapper as wrapper_mod
    importlib.reload(wrapper_mod)

    df_in = pd.DataFrame({
        "player": ["Player A"],
        "role": ["A"],
        "team": ["INT"],
        "predicted_pts_p50": [150.0],
    })

    df_out = wrapper_mod.apply_vorp_pricing(df_in)

    assert "vorp_points" in df_out.columns
    assert "prezzo_fair_1000" in df_out.columns
    assert "prezzo_fair_500" in df_out.columns
    assert "surplus_value_cr" in df_out.columns
    captured = capsys.readouterr()
    assert "fanta_lab_engine non disponibile" in captured.out


def test_wrapper_uses_engine_when_available(monkeypatch):
    fake_engine = types.ModuleType("fanta_lab_engine")

    def fake_compute_vorp(df):
        df = df.copy()
        df["vorp_points"] = 42.0
        df["prezzo_fair_1000"] = 100
        df["prezzo_fair_500"] = 50
        df["surplus_value_cr"] = 10
        return df

    fake_engine.compute_vorp = fake_compute_vorp
    monkeypatch.setitem(sys.modules, "fanta_lab_engine", fake_engine)

    import importlib
    import core.ingestion.static.vorp_pricing_wrapper as wrapper_mod
    importlib.reload(wrapper_mod)

    df_in = pd.DataFrame({"player": ["Player A"], "role": ["A"], "predicted_pts_p50": [150.0]})
    df_out = wrapper_mod.apply_vorp_pricing(df_in)

    assert (df_out["vorp_points"] == 42.0).all()
