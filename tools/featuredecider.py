import json
from tools.datareader import loadData
from llms.generation import GenerationModel
from paths import configDir, promptsDir, sandboxDir, dataDir

llm = GenerationModel(systemPrompt=promptsDir / "featurecolumns.md")

configurationPath = configDir / "configuration.json"
with open(configurationPath, "r") as file:
    configuration = json.load(file)

targetColumn = configuration.get("targetCol")
data = loadData(inputPath=dataDir / configuration.get("dataFile"), targetCol=targetColumn)

with open(sandboxDir / "processing.py", "r") as file:
    processingCode = file.read()

query = (
    f"Columns Before Preprocessing: {data.columns.tolist()}\n"
    f"Target Column: {targetColumn}\n\n"
    f"Processing Code:\n{processingCode}"
)

columnsToDemand = [col.strip() for col in llm.generate(query=query).split(",")]

configuration["columnNames"] = columnsToDemand
with open(configurationPath, "w") as file:
    json.dump(configuration, file, indent=4)