# RAG Q&A System

Sistema di Question & Answer basato su **Retrieval-Augmented Generation** (RAG) che risponde a domande su una collezione di documenti con attribuzione delle fonti.

## Architettura

```
Documenti (TXT/MD/PDF)
        │
        ▼
  ┌─────────────┐
  │  Ingestion   │  loader → chunker → embeddings → vector store
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  Retrieval   │  query → ricerca semantica → chunk rilevanti
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  Generation  │  contesto + domanda → LLM → risposta con fonti
  └─────────────┘
```

La pipeline è suddivisa in tre moduli indipendenti:
- **Ingestion**: caricamento documenti, splitting in chunk, generazione embeddings, storage in ChromaDB
- **Retrieval**: ricerca semantica dei chunk più rilevanti rispetto alla domanda
- **Generation**: generazione della risposta tramite LLM con attribuzione delle fonti

### Scelte tecniche

| Componente | Tecnologia | Motivazione |
|---|---|---|
| Embeddings + LLM | OpenAI API (`text-embedding-3-small`, `gpt-4o-mini`) | Setup semplice, nessuna GPU necessaria |
| Vector Store | ChromaDB | Persistente, zero configurazione, ottima API Python |
| Chunking | Splitter ricorsivo custom | Dimostra comprensione della pipeline senza dipendere da framework |
| API | FastAPI | Async, auto-documentazione Swagger, type hints |
| CLI | Click | Interfaccia pulita e dichiarativa |
| PDF parsing | PyMuPDF | Veloce, nessuna dipendenza Java |

**Perché non LangChain?** Per un progetto di questa scala, implementare la pipeline direttamente permette maggiore controllo e dimostra comprensione profonda dei singoli componenti.

## Quick Start

### Prerequisiti
- Python 3.11+
- Chiave API OpenAI

### Setup

```bash
# Clona il repository
git clone <repo-url>
cd Task2

# Crea virtual environment e installa
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -e ".[dev]"

# Configura la chiave API
cp .env.example .env
# Modifica .env e inserisci la tua OPENAI_API_KEY
```

### Uso via CLI

```bash
# Indicizza i documenti di esempio
python -m rag.cli ingest

# Fai una domanda
python -m rag.cli ask "What are Python best practices for error handling?"

# Domanda con dettagli sui chunk recuperati
python -m rag.cli ask "What is the CAP theorem?" --verbose

# Lista documenti indicizzati
python -m rag.cli list

# Rimuovi un documento dall'indice
python -m rag.cli remove "filename.txt"
```

### Uso via Web UI

```bash
# Avvia il server
python -m rag.api.app

# Apri nel browser
# http://localhost:8080
```

La web UI permette di:
- **Caricare documenti** tramite drag & drop o file picker (TXT, MD, PDF)
- **Gestire i documenti** indicizzati (visualizzare lista, eliminare)
- **Fare domande** e ricevere risposte con fonti

### API REST

Con il server avviato, gli endpoint disponibili sono:

| Metodo | Endpoint | Descrizione |
|---|---|---|
| `POST` | `/api/ask` | Fai una domanda |
| `POST` | `/api/documents/upload` | Carica un documento |
| `GET` | `/api/documents` | Lista documenti indicizzati |
| `DELETE` | `/api/documents/{filename}` | Rimuovi un documento |
| `POST` | `/api/ingest` | Re-indicizza tutti i documenti |
| `GET` | `/api/health` | Health check |

Documentazione interattiva Swagger: `http://localhost:8080/docs`

Esempio con curl:
```bash
# Indicizza documenti
curl -X POST http://localhost:8080/api/ingest

# Fai una domanda
curl -X POST http://localhost:8080/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the CAP theorem?"}'
```

## Struttura del progetto

```
Task2/
├── src/rag/
│   ├── config.py               # Configurazione centralizzata (pydantic-settings)
│   ├── ingestion/
│   │   ├── loader.py           # Caricamento documenti (TXT, MD, PDF)
│   │   ├── chunker.py          # Splitting ricorsivo custom
│   │   └── pipeline.py         # Orchestrazione ingestion
│   ├── retrieval/
│   │   └── retriever.py        # Ricerca semantica su ChromaDB
│   ├── generation/
│   │   ├── prompt.py           # Template dei prompt
│   │   └── generator.py        # Chiamata LLM con attribuzione fonti
│   ├── api/
│   │   ├── app.py              # FastAPI application
│   │   ├── routes.py           # Endpoint REST
│   │   └── models.py           # Schema request/response
│   └── cli.py                  # Interfaccia CLI (Click)
├── static/
│   └── index.html              # Web UI (HTML/JS vanilla)
├── documents/                  # Documenti di esempio
├── tests/                      # Test suite
├── pyproject.toml              # Configurazione progetto e dipendenze
└── .env.example                # Template variabili d'ambiente
```

## Gestione risposte non supportate

Il sistema gestisce i casi in cui la risposta non è supportata dai documenti a tre livelli:

1. **Soglia di rilevanza**: se nessun chunk supera la soglia minima di similarità (configurabile), il sistema restituisce direttamente un messaggio di "nessun documento rilevante" senza chiamare il LLM
2. **Prompt engineering**: il prompt istruisce esplicitamente il modello a rifiutare quando il contesto non contiene informazioni sufficienti
3. **Parsing output**: il sistema analizza la risposta del LLM per identificare frasi di rifiuto e marca la risposta come `is_supported: false`

## Testing

```bash
pytest tests/ -v
```

## Configurazione

Tutte le impostazioni sono configurabili tramite variabili d'ambiente o file `.env`:

| Variabile | Default | Descrizione |
|---|---|---|
| `OPENAI_API_KEY` | — | Chiave API OpenAI (obbligatoria) |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Modello per embeddings |
| `LLM_MODEL` | `gpt-4o-mini` | Modello per generazione risposte |
| `CHUNK_SIZE` | `512` | Dimensione target dei chunk (caratteri) |
| `CHUNK_OVERLAP` | `64` | Sovrapposizione tra chunk |
| `TOP_K` | `5` | Numero di chunk da recuperare |
| `RELEVANCE_THRESHOLD` | `0.3` | Soglia minima di similarità |
| `TEMPERATURE` | `0.1` | Temperatura del modello LLM |
