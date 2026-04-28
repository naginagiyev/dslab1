import json
from paths import configDir, modelsDir

class DeploymentAgent:
    def __init__(self):
        configurationPath = configDir / "configuration.json"
        with open(configurationPath, 'r', encoding="utf-8") as f:
            self.configuration = json.load(f)
        self.consultation = self.configuration
        self.runtimeConfig = self.configuration