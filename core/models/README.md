# core.models

Questo modulo è documentazione pura: il codice vive in `core/ingestion/static/08_quantile_points_model.py` e `09_vorp_auction_pricing.py`.

## 1. Divulgativo
Qui si spiega come il progetto smette di ragionare con un numero solo e inizia a ragionare con una distribuzione. `P10`, `P50` e `P90` raccontano tre versioni realistiche della stessa stagione: il pavimento prudente, la stima centrale e il tetto massimo. In parole semplici, `P50` è quello che il modello si aspetta più spesso, `P10` è il caso storto ma plausibile, `P90` è la stagione in cui tutto gira bene.

## 2. Tecnico
`08_quantile_points_model.py` costruisce un training set lagged senza target leakage: le stagioni `t-1 ... t-3` diventano feature per prevedere i punti fantacalcistici totali della stagione `t`, con target `pg_t * mfv_t`. I tre modelli usano `GradientBoostingRegressor(loss="quantile")` con quantili `0.10`, `0.50`, `0.90`.

Formula divulgata nel progetto per la stima centrale:

$$P_{50} = 38 \times \left(\text{Starts\%} \times FM_{starter} + (1-\text{Starts\%}) \times FM_{sub}\right) \times (1 - \text{Injury Factor})$$

con

$$FM_{starter} = \text{Base Rating} + 3 \cdot xG_{90} + 1 \cdot xA_{90} - 0.2 \cdot \text{Malus}_{90}$$

Nel codice di produzione, le feature attive includono `mv`, `mfv`, `gol_rate`, `ass_rate`, `amm_rate`, `avail_rate` e one-hot di ruolo; dopo la prediction il sistema forza la monotonicità: `P10 <= P50 <= P90`.

Il layer economico in `09_vorp_auction_pricing.py` trasforma i punti in valore d’asta. La formula base è:

$$VORP_i = \max(0, xPts_{player} - xPts_{replacement\ level})$$

Nel repository `xPts_player` corrisponde a `predicted_pts_p50`, quindi la colonna finale è `vorp_points`. Il replacement level è calcolato per ruolo ordinando i giocatori per `predicted_pts_p50` e prendendo il baseline coerente con gli slot di lega.

La fair price curve usa il budget spendibile per ruolo e una power-law scarcity curve. Nella documentazione del progetto:

$$Fair\ Price_i = 1 + \left(\frac{VORP_i^{\alpha}}{\sum_j VORP_j^{\alpha}}\right) \times Spendable\ Pool_{role}$$

con `alpha` non lineare calibrato per ruolo. In pratica il codice delega il mapping finale a `target_pricing.py`, poi pubblica `prezzo_fair_1000`, `prezzo_fair_500`, `target_price_1000/500` e `surplus_value_cr`.

## 3. Screenshot
> 📸 *Screenshot da aggiungere dopo il redesign UI (glow up).*

## 4. Dipendenze
- Documenta `core/ingestion/static/08_quantile_points_model.py`.
- Documenta `core/ingestion/static/09_vorp_auction_pricing.py` e `core/ingestion/static/target_pricing.py`.
- Le colonne risultanti vengono consumate da `modules/lineup/`, `modules/valuation/`, `modules/trades/` e `web/app.py`.
