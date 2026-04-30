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