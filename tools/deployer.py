import os
import time
import json
import paramiko
from paths import configDir
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("VM_IP")
password = os.getenv("VM_PASSWORD")
authToken = os.getenv("NGROK_AUTH_TOKEN")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=host, username="root", password=password)

vmDir = "vm"

def runCommand(cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    stdout.channel.settimeout(timeout)
    try:
        out = stdout.read().decode().strip()
    except Exception:
        out = ""
    try:
        err = stderr.read().decode().strip()
    except Exception:
        err = ""
    return out if out else err

def runBackground(cmd):
    transport = ssh.get_transport()
    channel = transport.open_session()
    channel.exec_command(f"bash -c '{cmd} > /dev/null 2>&1 &'")
    channel.close()

print("[RUNNING] checking ngrok")

if not runCommand("command -v ngrok"):
    print("[INFO] installing ngrok")
    runCommand("curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null")
    runCommand("echo 'deb https://ngrok-agent.s3.amazonaws.com buster main' | tee /etc/apt/sources.list.d/ngrok.list")
    runCommand("apt update -y", timeout=120)
    runCommand("apt install -y ngrok", timeout=120)
    runCommand(f"ngrok config add-authtoken {authToken}")

print("[SUCCESS] ngrok ready")

print("[RUNNING] checking project")

files = runCommand(f"ls {vmDir}")
required = ["api", "configuration", "model", "prediction", "preprocessor", "requirements.txt"]

for f in required:
    if f not in files:
        print(f"[ERROR] missing {f}")
        ssh.close()
        exit(1)

print("[SUCCESS] project OK")

print("[RUNNING] venv setup")

if "dslab1" not in runCommand(f"ls {vmDir}"):
    runCommand(f"cd {vmDir} && python3.10 -m venv dslab1", timeout=60)

print("[SUCCESS] venv ready")

print("[RUNNING] installing dependencies")
runCommand(
    f"cd {vmDir} && bash -c 'source dslab1/bin/activate && pip install -r requirements.txt'",
    timeout=300
)
print("[SUCCESS] dependencies installed")

print("[RUNNING] starting API")
runBackground(
    f"cd {vmDir} && source dslab1/bin/activate && uvicorn api:app --host 0.0.0.0 --port 5000 > /tmp/api.log 2>&1"
)
time.sleep(3)
print("[SUCCESS] API started")

print("[RUNNING] starting ngrok")
runCommand("pkill ngrok || true")
runBackground(
    f"cd {vmDir} && ngrok http 5000 --log=stdout > /tmp/ngrok.log 2>&1"
)
time.sleep(5)

print("[RUNNING] fetching public URL")

publicUrl = ""
for _ in range(10):
    raw = runCommand("curl -s http://localhost:4040/api/tunnels")
    try:
        data = json.loads(raw)
        for t in data.get("tunnels", []):
            if t.get("proto") == "https":
                publicUrl = t.get("public_url")
                break
        if publicUrl:
            break
    except Exception:
        pass
    time.sleep(2)

if publicUrl:
    print("[SUCCESS] PUBLIC URL:", publicUrl)
    configPath = configDir / "configuration.json"
    with open(configPath, "r", encoding="utf-8") as f:
        config = json.load(f)
    config["endPoint"] = publicUrl
    with open(configPath, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

else:
    print("[ERROR] failed to get ngrok URL")
    print(runCommand("cat /tmp/ngrok.log"))

ssh.close()
print("[DONE]")