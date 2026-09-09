# web

## 1. Divulgativo
Questo modulo è la faccia visibile del progetto: il server Flask che mette insieme asta live, listone e strumenti di supporto. È pensato per funzionare sia in modalità community sia in modalità personale, adattando configurazione, persistenza e esperienza d'uso al contesto. In pratica, tutto quello che l'utente tocca passa da qui.

## 2. Tecnico
`web/app.py` inizializza una Flask app monolitica ma organizzata per aree: config/env loading, tactical presets, dataset loading, shared state, pricing dinamico, REST API e template frontend.

Path split introdotto esplicitamente nel file:
- `BASE_DIR = os.path.dirname(os.path.abspath(__file__))` → cartella `web/`, usata per static serving.
- `PROJECT_ROOT = os.path.dirname(BASE_DIR)` → root del repository, usata per `data/`, `core/`, `.env` e config.

Dual-track behavior:
- `APP_ENV` defaulta a `community`.
- `IS_PERSONAL` diventa vero se `APP_ENV == "personal"` oppure se esiste `core/config.personal.py` e non si è in `community`.
- In modalità personal può caricare budget, slots, teams, password admin e persona del bot da file/env; in community usa defaults open-source.

Read-only filesystem constraint: `_get_writable_path()` prova a scrivere nella root di progetto, ma se gira su Vercel o il path non è scrivibile devia su una copia writable runtime. La parte utente sensibile alla persistenza cross-device è gestita con stato in memoria/Redis e, lato client, con `localStorage` per watchlist, profili e preferenze non distruttive.

Static asset layout:
- `web/static/css/` — fogli stile come `tutorial.css`.
- `web/static/js/` — script frontend come `tutorial.js`.
- route Flask: `/static/<path:path>` serve file da `os.path.join(BASE_DIR, "static")`.

Tra gli endpoint principali ci sono `/api/players`, `/api/state`, `/api/assign`, `/api/undo`, oltre agli endpoint per auth e settings. La web app importa i moduli di dominio da `modules/`.

## 3. Screenshot
> 📸 *Screenshot da aggiungere.*

## 4. Dipendenze
- Dipende da `core/config.py`, `modules/common/`.
- Consuma dataset in `data/`, cache infortuni, configurazioni di lega e asset statici sotto `web/static/`.
- È il layer applicativo finale che orchestra tutto il resto del repository.
