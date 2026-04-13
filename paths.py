from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
workspaceDir = PROJECT_ROOT / "sandbox"
agentsDir = PROJECT_ROOT / "agents"
configDir = PROJECT_ROOT / "configuration"
dataDir = PROJECT_ROOT / "data"
modelsDir = PROJECT_ROOT / "llms"
promptsDir = PROJECT_ROOT / "prompts"
toolsDir = PROJECT_ROOT / "tools"