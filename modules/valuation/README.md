# modules.valuation

## 1. Divulgativo
Questo modulo legge le rose dopo l’asta e prova a dire chi è messo meglio sul lungo periodo. Non si limita alla spesa o al nome più famoso: stima i punti stagionali attesi della squadra, quantifica quanto capitale è esposto su profili fisicamente fragili e assegna badge per colpi, errori e costruzione della rosa. È il lato “power rankings” del progetto.

## 2. Tecnico
`modules/valuation/audit_engine.py` è un report engine read-only, senza dipendenza dal feed live. La metrica principale nasce da `_team_expected_points(team, pool_df, tracking_history)`, che somma per ogni giocatore una versione ripesata del `predicted_pts_p50`.

Se esistono almeno 3 record recenti in `season_tracking`, `_reweighted_value()` usa:

$$ExpectedSeasonPoints = 0.5 \cdot P50_{originale} + 0.5 \cdot RecentForm_{EWMA}$$

Altrimenti mantiene `predicted_pts_p50` puro.

L’Indice di Capitale a Rischio deriva da `_team_risk_capital(team, pool_df)`: somma i crediti pagati per tutti i giocatori con `giorni_infortunio_3y > 60` (`FRAGILITY_THRESHOLD_DAYS = 60`). Il report pubblica sia `risk_capital_cr` sia:

$$RiskCapitalPct = rac{RiskCapitalCr}{BudgetTeam} 	imes 100$$

Draft badges reali dal codice:
- `Miglior Colpo VORP: {player} (+X.Y cr)` — miglior `surplus_value_cr` positivo nella rosa.
- `Peggior Overpay: {player} (X.Y cr)` — peggior `surplus_value_cr` negativo nella rosa.
- `Most Balanced Squad` — assegnato alla squadra con deviazione standard minima della spesa per reparto P/D/C/A (`_department_std`).
- `Glass Cannon` — assegnato alle squadre che stanno sia nella top-3 per `expected_points` sia nella top-3 per `risk_capital_cr`.

L’output finale è ordinato in modo decrescente per `expected_points`.

## 3. Screenshot
> 📸 *Screenshot da aggiungere dopo il redesign UI (glow up).*

## 4. Dipendenze
- Dipende da `modules/valuation/season_tracking.py` per `get_recent_form()`.
- Consuma `player_pool_df` con colonne come `predicted_pts_p50`, `giorni_infortunio_3y`, `surplus_value_cr`.
- Viene usato da `web/app.py` per audit e power rankings post-draft.
