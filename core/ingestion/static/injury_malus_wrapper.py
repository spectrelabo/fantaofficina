"""Thin wrapper attorno a fanta_lab_engine.injury_malus, con fallback demo (malus neutro)."""

try:
    from fanta_lab_engine import injury_malus as _engine_injury_malus
except ImportError:
    _engine_injury_malus = None


def compute_malus_for_player(giorni: int, grave: bool) -> float:
    """Calcola il malus infortunio per un giocatore, usando l'engine se disponibile."""
    if _engine_injury_malus is not None:
        try:
            return _engine_injury_malus(giorni, grave)
        except AttributeError:
            print("  [WARNING] fanta_lab_engine versione incompatibile, fallback a dati demo")

    print("  [INFO] fanta_lab_engine non disponibile: uso valori demo da examples/dataset_sample.csv")
    return 0.0
