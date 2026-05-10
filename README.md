# DS LAB I

An agentic machine learning automation tool. You give it a dataset, and it handles the rest — from analysis to a live prediction API.

---

## What It Does

This tool runs a full machine learning pipeline with minimal input from you:

1. **Consults you** (or works fully on its own) to understand your project goals
2. **Analyzes the dataset** with exploratory data analysis (EDA)
3. **Plans and runs preprocessing** — cleaning, encoding, scaling
4. **Splits the data** into training and test sets
5. **Trains a model** using an AI-generated training plan
6. **Tunes the model** for better performance
7. **Selects the best features** automatically
8. **Deploys the model** to a remote VM and exposes it as a public REST API (optional)
9. **Writes a report** summarizing the entire process (optional)

It supports **binary classification**, **multi-class classification**, and **regression**, **anomaly detection**, **time series** and **clustering** tasks.

---

## How to Run

```bash
python main.py
```

You will be asked to provide the path to your dataset. After that, you can either answer a few questions about your project or let the tool decide everything automatically.

---

## Deployment

If deployment is enabled in the configuration, the tool will:

- Connect to a remote VM over SSH
- Upload the trained model and API files
- Install dependencies in a virtual environment
- Start a FastAPI server on port 5000
- Expose it publicly via [ngrok](https://ngrok.com)

The public endpoint is saved automatically to `configuration/configuration.json`.

### Prediction API

Once deployed, the API has two endpoints:

| Method | Path       | Description              |
|--------|------------|--------------------------|
| GET    | `/`        | Check if the API is live |
| POST   | `/predict` | Get predictions          |

**Example request body for `/predict`:**

```json
[
  { "feature_1": 1.5, "feature_2": "value", "..." : "..." }
]
```

**Example response:**

```json
{ "prediction": [0] }
```

---

## Environment Variables

Create a `.env` file in the `vm/` folder with the following keys:

```
VM_IP=your_vm_ip
VM_PASSWORD=your_vm_password
NGROK_AUTH_TOKEN=your_ngrok_token
OPENAI_API_KEY=your_openai_key
```

---

## Project Structure

```
DS LAB I/
├── main.py               # Entry point
├── agents/               # AI agents for each pipeline step
├── tools/                # Helper tools (EDA, training, deployment, etc.)
├── prompts/              # Prompt templates for the agents
├── llms/                 # LLM integration
├── vm/                   # Files that run on the remote VM
├── configuration/        # Key project configurations
├── sandbox/              # Workspace for agents and tools
└── models/               # Trained model artifacts
```

### LLM modules (`llms/`)

| File | Role |
|------|------|
| `generation.py` | Planning, reasoning, and structured extraction via the OpenAI Chat API |
| `codex.py` | Code generation and repair |

Both read system prompts from `prompts/` and use API keys from your environment (see **Environment Variables**).

### Agents (`agents/`)

| File | Role |
|------|------|
| `consultant.py` | Q&A consultation, off-topic handling, target detection entry |
| `configfiller.py` | Fills missing fields in the project configuration from the EDA report |
| `planner.py` | Builds preprocessing and training plans |
| `processoragent.py` | Generates and runs preprocessing code (with fix loops) |
| `trainagent.py` | Generates and runs training code (with fix loops) |
| `evaluationagent.py` | Scores the model and tuning loops |
| `reporter.py` | Builds the markdown documentation for a run |

### Tools (`tools/`)

These scripts do **not** call the LLM; they run fixed steps the pipeline depends on.

| File | Role |
|------|------|
| `eda.py` | Exploratory data analysis report |
| `datasplitter.py` | Train / validation / test split |
| `coderunner.py` | Runs generated scripts as subprocesses |
| `datareader.py` | Loads CSV/TSV and basic checks |
| `metrics.py` | Maps metric names to scikit-learn scores |
| `transfer.py` | SFTP upload to the deployment VM |
| `deployer.py` | Remote setup, FastAPI, ngrok |
| `featuredecider.py` | Decides input columns for the prediction API |

### Prompts (`prompts/`)

Markdown files used as system or task prompts. Examples:

| File | Used for |
|------|----------|
| `consultant.md` | Consultation dialogue |
| `consultantassistant.md` | Extracting consultation answers into JSON |
| `targetdetector.md` | Target column detection |
| `configfiller.md` | Filling configuration from EDA |
| `processingplanprompt.md` | Preprocessing plan |
| `trainplanprompt.md` | Training plan |
| `codexcodeprompt.md` | Code generation |
| `codexfixprompt.md` | Code repair |
| `processorreasoningprompt.md` | Preprocessing fix-loop reasoning |
| `trainreasoningprompt.md` | Training fix-loop reasoning |
| `evaluationprompt.md` | Hyperparameter tuning suggestions |
| `featurecolumns.md` | Inference input columns |
| `reportprompt.md` | Final run documentation |

### Other configuration (`configuration/`)

| File | Role |
|------|------|
| `constants.json` | Split ratios, tuning limits, paths |
| `metrics.json` | Allowed metric names per task type |
| `modeloptions.md` | Model shortlist for the planner |
| `edaconfig.py` | EDA settings |

During a run, the active settings for the project are written under `configuration/` (for example `configuration.json` for the run).

---

## Testing the project

1. Install dependencies (see **Requirements**).
2. Set `OPENAI_API_KEY` (and optional VM variables if you test deployment).
3. Run `python main.py`, pass a path to a small CSV, and try both paths: with questions and without.
4. Check outputs under `sandbox/` (processed data, scripts, logs, optional `documentation.md`) and `configuration/` for the updated JSON.

For prompt or agent changes, edit the matching file in `prompts/` or `agents/`, then repeat a short run to confirm the pipeline still completes.

---

## Requirements

- Python 3.10.18
- An OpenAI API key
- A remote Linux VM accessible over SSH (for deployment)
- A ngrok account and auth token (for public API exposure)

Install dependencies:

```bash
pip install -e .
```