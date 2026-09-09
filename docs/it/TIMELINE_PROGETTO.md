# Timeline del progetto

Questa pagina racconta la storia di `fanta-lab`: da dove è partito, cosa è diventato attraverso sette pilastri di lavoro, e verso quale idea di prodotto si sta muovendo. Non è un changelog tecnico — per quello ci sono i README dei singoli moduli — ma una narrazione pensata per chiunque voglia capire *perché* il progetto è fatto così.

## 1. Da dove veniamo

`fanta-lab` è nato come uno script pensato per un solo momento della stagione: l'asta pre-campionato. L'obiettivo era semplice e circoscritto — dato un listone di calciatori, produrre un prezzo "giusto" a cui comprarli, da consultare la sera del draft e poi accantonare fino all'anno successivo.

Il cuore statistico di quella prima versione era una regressione quantile (Gradient Boosting Regressor) allenata sui dati storici dei giocatori, capace di stimare non un singolo numero ma tre percentili dei punti attesi a fine stagione: P10 (scenario pessimista), P50 (scenario mediano) e P90 (scenario ottimista). Da questa distribuzione di punti attesi si derivava il VORP (Value Over Replacement Player), che confrontava ogni giocatore con un ipotetico sostituto di livello base nel suo ruolo per arrivare a un fair price coerente con il budget d'asta.

Era, in sostanza, una fotografia: un unico calcolo, fatto una volta, per decidere come spendere il budget in un'unica serata. Tutto quello che è successo dopo — i sette pilastri descritti qui sotto — è la storia di come quella fotografia sia diventata un film: un sistema che continua a osservare, aggiornare e ricalibrare le proprie stime lungo l'intero arco delle 38 giornate di campionato.

## 2. Cosa mostra questa versione demo

**Pilastro 1 — Dual-track community/personal.** Il primo passo di maturazione architetturale: separare una configurazione "community", pensata per essere condivisa e riprodotta da chiunque cloni il repository, da una configurazione "personal", con dati e parametri specifici di chi usa il progetto per la propria lega. La cascata di configurazione guidata dalla variabile d'ambiente `APP_ENV` ha reso possibile questa distinzione senza duplicare codice.

**Pilastro 2 — Bugfix critici.** Una serie di correzioni che hanno reso il sistema affidabile in produzione: un fallback su `player_id` per garantire la riproducibilità del training anche quando l'identificativo primario non è disponibile; maggiore resilienza dello scraping delle fonti dati, con meccanismi di fallback quando le pagine cambiano struttura o non rispondono; una ricalibrazione dei percentili della Scala Slot per tenere conto delle differenze tra ruoli; e un blueprint di percentuali dinamiche, riscalate sul budget effettivo della lega invece di un valore fisso.

**Pilastro 3 — Baseline demo pubblica.** Questo repository pubblico è una versione semplificata e didattica del progetto: mostra la pipeline d'asta end-to-end (caricamento dati, pricing, export Excel) usando un dataset di esempio incluso nel repo, senza scraping live. Il prodotto commerciale completo — pipeline dati storici reali, un modello di regressione quantile allenato, moduli analitici in-season e un assistente AI — è un prodotto privato, non distribuito qui.

Il filo conduttore del progetto, dal punto di vista statistico, è il passaggio da una stima puntuale calcolata una sola volta a un sistema che ragiona in termini di intere distribuzioni di possibili esiti piuttosto che singoli valori attesi: una regressione quantile stima non un singolo numero ma tre percentili dei punti attesi (scenario pessimista, mediano, ottimista), e il VORP (Value Over Replacement Player) confronta ogni giocatore con un sostituto di livello base nel suo ruolo per arrivare a un fair price d'asta.

## 3. Dove vogliamo arrivare

La direzione verso cui il progetto si muove non è un elenco di funzionalità da spuntare, ma un'idea di fondo: rendere l'incertezza statistica sempre più centrale e sempre più accessibile — ragionando sempre di più in termini di distribuzioni intere piuttosto che di singoli punti attesi, e traducendo questa sofisticazione in decisioni comprensibili per chi gioca a fantacalcio per divertirsi, non per fare data science.
