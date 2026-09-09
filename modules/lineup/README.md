# modules.lineup

## 1. Divulgativo
Questo modulo sceglie la miglior formazione settimanale possibile usando i numeri live della giornata. Non guarda solo chi è forte “in generale”, ma prova a capire chi conviene schierare adesso, escludendo indisponibili e combinando i giocatori dentro un modulo regolamentare. Il risultato è una proposta concreta: titolari, panchina ordinata e stima dei punti attesi.

## 2. Tecnico
`modules/lineup/lineup_solver.py` costruisce un MILP con variabili binarie `x_i ∈ {0,1}` e massimizza la somma delle `xpts_week` dei titolari.

Objective reale del solver:

$$\max \sum_i x_i \cdot xPts_{week,i}$$

Nel codice è implementato come minimizzazione di `-1.0 * df["xpts_week"]` dentro `scipy.optimize.milp`.

Formazioni ammesse (`FORMATIONS`):
- 3-4-3
- 3-5-2
- 4-3-3
- 4-4-2
- 4-5-1
- 5-3-2
- 5-4-1

Pipeline logica:
1. richiede un overlay reale (`feed_unavailable` se manca);
2. converte la rosa in DataFrame;
3. aggiunge `xpts_week` con `compute_weekly_xpts()`;
4. calcola `status` via `get_player_status()`;
5. esclude `INFORTUNATO` e `SQUALIFICATO`;
6. prova ogni modulo e sceglie quello con `total_xpts` più alto.

Il bonus modificatore difensivo atteso è calcolato da `_bonus_modificatore(df, selected_indices)`: se i difensori titolari sono meno di 4, bonus `0.0`; altrimenti prende i 3 difensori con `xpts_week` più alte, aggiunge il portiere e fa la media su 4:

$$Bonus_{mod} = rac{xPts_{GK} + xPts_{D1} + xPts_{D2} + xPts_{D3}}{4}$$

La “Panchina Intelligente” è la lista dei non selezionati ordinata per `xpts_week` in ordine decrescente (`na_position="last"`), quindi prima i cambi più utili e in fondo chi non ha proiezione live.

## 3. Screenshot
> 📸 *Screenshot da aggiungere dopo il redesign UI (glow up).*

## 4. Dipendenze
- Dipende da `modules/common/data_provider.py` per overlay, xPts e status.
- Richiede un feed valido da `core/ingestion/dynamic/build_feed.py` via client dinamico.
- È usato direttamente da `modules/trades/trade_analyzer.py` e indirettamente da `web/app.py`.
