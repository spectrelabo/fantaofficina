import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_malus_calculation_falls_back_when_engine_missing(monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "fanta_lab_engine", None)

    import importlib
    import core.ingestion.static.injury_malus_wrapper as wrapper_mod
    importlib.reload(wrapper_mod)

    malus = wrapper_mod.compute_malus_for_player(giorni=90, grave=True)

    assert malus == 0.0
    captured = capsys.readouterr()
    assert "fanta_lab_engine non disponibile" in captured.out


def test_malus_calculation_uses_engine_when_available(monkeypatch):
    fake_engine = types.ModuleType("fanta_lab_engine")
    fake_engine.injury_malus = lambda giorni, grave: 0.777
    monkeypatch.setitem(sys.modules, "fanta_lab_engine", fake_engine)

    import importlib
    import core.ingestion.static.injury_malus_wrapper as wrapper_mod
    importlib.reload(wrapper_mod)

    malus = wrapper_mod.compute_malus_for_player(giorni=90, grave=True)

    assert malus == 0.777
