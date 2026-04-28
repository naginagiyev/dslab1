import os
import shutil
from paths import sandboxDir, configDir, dataDir, modelsDir, vmDir

for item in os.listdir(sandboxDir):
    item_path = os.path.join(sandboxDir, item)
    if os.path.isfile(item_path) or os.path.islink(item_path):
        os.remove(item_path)
    elif os.path.isdir(item_path):
        shutil.rmtree(item_path)

for item in os.listdir(modelsDir):
    item_path = os.path.join(modelsDir, item)
    if os.path.isfile(item_path) or os.path.islink(item_path):
        os.remove(item_path)
    elif os.path.isdir(item_path):
        shutil.rmtree(item_path)

keywords = ["train", "test", "val", "processed"]
for item in os.listdir(dataDir):
    if any(keyword in item for keyword in keywords):
        item_path = os.path.join(dataDir, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)

for filename in ["configuration.json"]:
    file_path = configDir / filename
    if file_path.exists():
        os.remove(file_path)