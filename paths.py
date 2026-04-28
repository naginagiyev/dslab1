from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
agentsDir = PROJECT_ROOT / "agents"
configDir = PROJECT_ROOT / "configuration"
dataDir = PROJECT_ROOT / "data"
llmsDir = PROJECT_ROOT / "llms"
modelsDir = PROJECT_ROOT / "models"
promptsDir = PROJECT_ROOT / "prompts"
sandboxDir = PROJECT_ROOT / "sandbox"
toolsDir = PROJECT_ROOT / "tools"
vmDir = PROJECT_ROOT / "vm"