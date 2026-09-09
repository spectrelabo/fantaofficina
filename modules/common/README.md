# modules.common

## 1. Divulgativo
Questo è il ponte tra i dati live e i moduli analitici. Serve a evitare che lineup solver, audit e trade machine parlino direttamente con gli scraper o con il feed grezzo: qui trovano funzioni già pronte per capire se il feed è reale, leggere l’overlay della giornata e agganciare ogni giocatore alla sua proiezione settimanale.

## 2. Tecnico
`modules/common/data_provider.py` è un shared data-access layer. Importa `get_default_client()` da `core.ingestion.dynamic.client` e `normalize_name()` da `core.ingestion.dynamic.utils`, poi espone queste funzioni pubbliche:

```python
def is_overlay_real(feed):
def get_dynamic_overlay(client=None):
def compute_weekly_xpts(df, overlay):
def get_player_status(overlay, team, name, role):
```

Comportamento reale:
- `is_overlay_real(feed)` considera valido solo un feed con `matchday > 0` e almeno un player nel payload.
- `get_dynamic_overlay(client=None)` prova `client.get_feed()` e non rilancia eccezioni: in caso di errore restituisce `None`.
- `compute_weekly_xpts(df, overlay)` crea una copia del DataFrame, aggiunge colonna `xpts_week` e ritorna `(df_with_column, overlay_available)`.
- `get_player_status(overlay, team, name, role)` restituisce lo status del giocatore dal feed, default `"OK"`.

Il file contiene anche helper interni `_team_slug()` e `_player_key()` per mantenere la stessa chiave `team_player_role` usata da `core.ingestion.dynamic.build_feed`.

## 3. Screenshot
> 📸 *Screenshot da aggiungere dopo il redesign UI (glow up).*

## 4. Dipendenze
- Dipende da `core.ingestion.dynamic.client` e `core.ingestion.dynamic.utils`.
- È usato direttamente da `modules/lineup/lineup_solver.py`.
- Fornisce il contratto dati live che il resto dei moduli può riusare senza conoscere la struttura interna del feed.
