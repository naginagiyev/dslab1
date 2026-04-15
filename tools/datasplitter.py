import json
import pandas as pd
from paths import configDir, dataDir
from sklearn.model_selection import train_test_split

def split():
    with open(configDir / "constants.json", 'r') as f:
        constants = json.load(f)

    runtimeConfigPath = configDir / "runtimeconfig.json"
    with open(runtimeConfigPath, 'r') as f:
        runtimeConfig = json.load(f)

    trainSplit = constants["trainSplit"]
    testSplit = constants["testSplit"]
    validationSplit = 1 - trainSplit - testSplit
    seed = constants["seed"]

    processedDataPath = runtimeConfig["processedDataFile"]
    processedData = pd.read_csv(dataDir / processedDataPath)

    train, test = train_test_split(processedData, test_size=testSplit, random_state=seed)

    if validationSplit > 0:
        adjustedValSplit = validationSplit / (1 - testSplit)
        train, val = train_test_split(train, test_size=adjustedValSplit, random_state=seed)
        val.to_csv(dataDir / "val.csv", index=False)
        runtimeConfig['valFile'] = "val.csv"

    train.to_csv(dataDir / "train.csv", index=False)
    test.to_csv(dataDir / "test.csv", index=False)

    runtimeConfig['trainFile'] = "train.csv"
    runtimeConfig['testFile'] = "test.csv"

    with open(runtimeConfigPath, 'w') as f:
        json.dump(runtimeConfig, f, indent=2)
