<div align="center">

# ◉ Afterimage

### Give your IT incidents a memory.

**A local-first AI-powered IT incident knowledge system that helps you find similar past issues, learn from previous resolutions, and troubleshoot smarter.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Ollama](https://img.shields.io/badge/AI-Ollama-black?style=flat-square)](https://ollama.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[Explore the Code](https://github.com/sumedhx/afterimage) · [Report a Bug](https://github.com/sumedhx/afterimage/issues) · [Request a Feature](https://github.com/sumedhx/afterimage/issues)

</div>

---

## The Problem

IT support engineers encounter recurring issues every day.

A printer stops responding. An access point becomes unreachable. A workstation develops a login problem.

Often, someone has already encountered the same issue and found a solution. But that knowledge might be buried in old tickets, scattered across notes, or remembered only by the engineer who fixed it.

**Afterimage helps IT support engineers turn past incidents into reusable knowledge.**

Instead of starting troubleshooting from scratch, describe the current problem and retrieve similar historical incidents, their symptoms, recorded root causes, and resolutions.

## Screenshots

### 1. Dashboard

Get an overview of your incident knowledge base, review incident statuses, and quickly navigate to the main workflows.

<div align="center">
  <img src="docs/screenshots/dashboard.png" alt="Afterimage dashboard showing incident metrics, quick actions, and recent incidents" width="700">
</div>

### 2. Search Incident Knowledge

Describe a technical problem and retrieve relevant historical incidents. Each match displays its category, status, similarity score, symptoms, recorded root cause, and resolution.

<div align="center">
  <img src="docs/screenshots/search.png" alt="Afterimage semantic search showing historical incident matches and similarity scores" width="600">
</div>

### 3. AI-Assisted Troubleshooting

Use a local AI model to analyze retrieved incidents, identify similarities, summarize historical findings, and suggest troubleshooting checks.

<div align="center">
  <img src="docs/screenshots/ai-analysis.png" alt="Afterimage local AI analysis with historical findings and suggested troubleshooting steps" width="600">
</div>

### 4. Record a New Incident

Capture the incident title, category, description, symptoms, affected system, user context, recent changes, root cause, resolution, and status.

<div align="center">
  <img src="docs/screenshots/new-incident.png" alt="Afterimage form for recording an IT incident and its resolution" width="600">
</div>

---

## Features

### 🔎 Hybrid Incident Search

Find relevant incidents using a combination of semantic similarity and keyword matching.

- Search using natural-language descriptions.
- Find conceptually similar incidents even when the wording differs.
- Match important technical terms and symptoms.
- Review similarity scores for retrieved incidents.
- Retrieve troubleshooting information from previous cases.

### 🧠 Local AI Analysis

After retrieving relevant incidents, ask a local language model to analyze them.

Afterimage uses Ollama to run its AI model locally, avoiding the need for a hosted LLM API for local inference.

The analysis can include:

- Similarities between the current issue and historical incidents.
- Previously recorded root causes and resolutions.
- Suggested troubleshooting checks.
- Uncertainties and possible alternative explanations.

AI-generated suggestions should always be verified before applying changes to production systems.

### 📝 Incident Management

Record and maintain a structured history of IT incidents.

Each incident can include:

- Incident title and category.
- Issue description.
- Symptoms and error messages.
- Hostname or system name.
- Username.
- Context surrounding the issue.
- Recent changes.
- Root cause.
- Troubleshooting steps and resolution.
- Incident status.

Review, edit, and delete saved incidents through the application.

### 📚 Sample Knowledge Base

Explore the application using fictional sample incidents.

- Enable sample knowledge to explore example scenarios.
- Search sample incidents alongside your saved incidents.
- Disable sample knowledge to work with your saved records only.
- Keep sample records separate from your actual incident database.

This makes it possible to explore Afterimage before building your own knowledge base.

### 🔐 Local-First Architecture

Afterimage is designed to keep incident data and AI inference local.

- SQLite stores saved incident records locally.
- Ollama runs the language model on your machine.
- Local embeddings support semantic search.
- No hosted LLM API is required for the core local inference workflow.

**Privacy note:** Local processing does not automatically guarantee complete privacy. Your machine, installed dependencies, and any additional integrations still affect your security posture.

---

## How It Works

Afterimage follows a retrieval-first workflow.

```text
┌──────────────────────────────┐
│      Describe the Issue      │
│                              │
│ Symptoms, errors, context    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│        Hybrid Search         │
│                              │
│ Semantic similarity          │
│ +                            │
│ Keyword matching             │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│     Historical Incidents     │
│                              │
│ Symptoms, root causes,       │
│ resolutions and match scores │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Local AI Analysis      │
│                              │
│ Similarities, findings,      │
│ suggested troubleshooting    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Engineer Investigates   │
│                              │
│ Verify findings and resolve  │
│ the current incident         │
└──────────────────────────────┘
```

The goal is not to replace an IT engineer. It is to make existing knowledge easier to find and reuse.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and incident processing |
| Streamlit | Interactive web interface |
| SQLite | Local incident database |
| Ollama | Local AI model execution and embeddings |
| Qwen2.5 1.5B | Language model for AI-assisted analysis |
| `nomic-embed-text` | Text embeddings for semantic search |

### Models

Afterimage is configured to use these Ollama models:

| Model | Role |
|---|---|
| `qwen2.5:1.5b` | AI-assisted incident analysis |
| `nomic-embed-text` | Generate embeddings for semantic search |

These models must be available in your local Ollama installation.

---

## Getting Started

### Prerequisites

Install the following:

- Python 3.10 or newer.
- Git.
- [Ollama](https://ollama.com/download).

Your machine also needs sufficient memory and processing capacity to run the selected local models.

### 1. Clone the Repository

```bash
git clone https://github.com/sumedhx/afterimage.git
cd afterimage
```

### 2. Create a Virtual Environment

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install the Ollama Models

Make sure Ollama is installed and running.

Pull the language model:

```bash
ollama pull qwen2.5:1.5b
```

Pull the embedding model:

```bash
ollama pull nomic-embed-text
```

Confirm that both models are available:

```bash
ollama list
```

### 5. Run Afterimage

```bash
streamlit run app.py
```

Streamlit will display a local URL, typically:

```text
http://localhost:8501
```

Open that URL in your browser.

---

## Using Afterimage

### Step 1 — Explore the Dashboard

Review the incident overview and enable the sample knowledge base to explore example incidents.

### Step 2 — Search for an Issue

Open **Search Knowledge** and describe the problem you are investigating.

For example:

> The warehouse printer is online, but print jobs remain stuck in the queue.

Afterimage retrieves relevant historical incidents and displays their match scores and recorded troubleshooting information.

### Step 3 — Analyze the Results

Select **Analyze with local AI** to generate an analysis based on the retrieved incidents.

Review the similarities, historical findings, and suggested checks.

### Step 4 — Investigate and Verify

Use the suggestions as a starting point for your investigation. Confirm the actual root cause rather than assuming that the most similar incident has the same cause.

### Step 5 — Record the Resolution

Open **New Incident** and document the issue and the steps that resolved it.

Over time, your saved incidents become a reusable source of troubleshooting knowledge.

### Step 6 — Maintain Your Knowledge Base

Use **Incident History** to review, edit, or remove saved incidents.

---

## Project Structure

```text
afterimage/
├── app.py
├── requirements.txt
├── src/
│   ├── ai.py
│   ├── database.py
│   ├── sample_incidents.py
│   └── search.py
├── data/
│   └── afterimage.db
├── docs/
│   └── screenshots/
│       ├── dashboard.png
│       ├── search.png
│       ├── ai-analysis.png
│       └── new-incident.png
└── README.md
```

| File | Purpose |
|---|---|
| `app.py` | Streamlit application and interface |
| `src/ai.py` | AI-assisted incident analysis |
| `src/database.py` | SQLite database operations |
| `src/sample_incidents.py` | Fictional sample incidents |
| `src/search.py` | Hybrid incident search |
| `requirements.txt` | Python dependencies |
| `data/afterimage.db` | Local incident database |

The database is created locally by the application and should not be committed to Git.

---

## Privacy and Data Storage

Afterimage is designed for local use.

- Saved incidents are stored in a local SQLite database.
- The database file should not be committed to Git.
- Local Ollama models handle language-model inference and embedding generation.
- Sample incidents are separate from saved database records.

Before storing real incident data, consider whether it contains passwords, access tokens, personal information, internal IP addresses, network configurations, or other sensitive operational details.

**Never store credentials or secrets in incident descriptions.**

### Recommended `.gitignore`

Ensure your `.gitignore` includes:

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/

# Environment variables and secrets
.env
.env.*

# Local application data
data/*.db
data/*.sqlite
data/*.sqlite3

# Operating system
.DS_Store
Thumbs.db
```

If you intentionally distribute a sanitized sample database, handle it separately from your private incident data.

---

## Current Scope

Afterimage currently focuses on local incident knowledge and retrieval.

| Capability | Status |
|---|---|
| Incident creation | Available |
| Incident history | Available |
| Incident editing and deletion | Available |
| Semantic and keyword-based search | Available |
| Similarity scores | Available |
| Local AI analysis | Available |
| Fictional sample knowledge base | Available |
| Local SQLite storage | Available |
| Hosted public demo | Not currently available |

The application is intended to run locally. A public demo is not currently provided.

---

## Roadmap

Potential future improvements include:

- [ ] Import incidents from CSV and existing ticket exports.
- [ ] Export incident records for backup and migration.
- [ ] Improve search evaluation and relevance ranking.
- [ ] Add filters for category, status, and affected system.
- [ ] Track incident recurrence and resolution effectiveness.
- [ ] Add automated tests for search and database operations.
- [ ] Improve incident deduplication.
- [ ] Support configurable local embedding and language models.
- [ ] Add a more detailed incident timeline.

These are potential future enhancements, not claims about existing functionality.

---

## Contributing

Contributions, suggestions, and bug reports are welcome.

1. Fork the repository.
2. Create a feature branch:

   ```bash
   git checkout -b feature/your-feature
   ```

3. Make your changes.
4. Test the application locally.
5. Commit your changes:

   ```bash
   git add .
   git commit -m "feat: describe your change"
   ```

6. Push your branch and open a pull request.

For larger changes, open an issue first to discuss the proposed approach.

Please avoid committing local databases, credentials, or sensitive incident records.

---

## Why Afterimage?

In IT support, a resolved incident should be more than a closed ticket.

It should become knowledge that helps the next engineer solve a similar problem faster.

Afterimage is built around that idea: preserve the useful details of past incidents, make them searchable, and use local AI to help connect the dots.

Sometimes, the most useful intelligence isn't knowing everything.

**It's remembering what happened last time.**

---

## Author

**Sumedh Suralkar**

- GitHub: [@sumedhx](https://github.com/sumedhx)
- Project: [Afterimage](https://github.com/sumedhx/afterimage)
- Email: [sumedh.developer@gmail.com](mailto:sumedh.developer@gmail.com)

---

<div align="center">

**Built with Python, Streamlit, SQLite, and local AI.**

*Keep your knowledge local. Make every incident count.*

</div>
