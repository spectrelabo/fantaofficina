# modules.trades

## 1. Divulgativo
Questo modulo prova a capire se uno scambio migliora davvero le due squadre coinvolte. Non si ferma al “questo è più forte di quello”, ma pesa anche i bisogni di reparto e, quando il feed live è disponibile, misura l’impatto immediato sulla formazione titolare. In più scandaglia combinazioni multiple per trovare scambi win-win che a occhio spesso non emergono.

## 2. Tecnico
`modules/trades/trade_analyzer.py` combina una valutazione statica di valore e, opzionalmente, una valutazione live sulla lineup.

Valore base del singolo giocatore:

$$Value_{player} = predicted\_pts\_p50 + vorp\_points$$

Il modulo applica un role multiplier: `1.2` se il reparto è sotto il target (`ROLE_TARGET = {P:3, D:8, C:8, A:6}`), `0.8` se è in surplus. La delta statica di squadra è quindi una differenza tra valore entrante e uscente pesato per fabbisogno di ruolo.

Se l’overlay live è disponibile, `evaluate_trade()` costruisce rose pre/post trade e richiama `solve_lineup()` per entrambe le squadre. La formula effettiva è:

$$\Delta Utilità = E[Punti\ Titolari\ Post\ Trade] - E[Punti\ Titolari\ Pre\ Trade]$$

Nel payload JSON appaiono `team_a_delta_xpts` e `team_b_delta_xpts`.

Il Win-Win Detector Combinatorio è `find_winwin_trades(...)`: prova tutte le combinazioni `1..max_per_side` di giocatori in uscita e in entrata usando `itertools.combinations`, calcola `team_a_delta` e `team_b_delta`, e conserva solo quelle con miglioramento stretto per entrambi:

$$team\_a\_delta > 0 \quad \land \quad team\_b\_delta > 0$$

Le proposte vengono ordinate per `combined_delta` decrescente.

## 3. Screenshot
> 📸 *Screenshot da aggiungere dopo il redesign UI (glow up).*

## 4. Dipendenze
- Dipende da `modules/lineup/lineup_solver.py` per la valutazione live pre/post scambio.
- Consuma dataset con `predicted_pts_p50` e `vorp_points`.
- È orchestrato da `web/app.py` nelle schermate dedicate alla trade machine.
