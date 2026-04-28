import os
import paramiko
from paths import vmDir
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("VM_IP")
password = os.getenv("VM_PASSWORD")

folder = Path(vmDir)
remoteBase = f"/root/{folder.name}"

sshClient = paramiko.SSHClient()
sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
sshClient.connect(hostname=host, port=22, username="root", password=password, look_for_keys=False, allow_agent=False)

sftpClient = sshClient.open_sftp()

try:
    sftpClient.mkdir(remoteBase)
except IOError:
    pass

for file in folder.rglob("*"):
    if file.is_file():
        remotePath = f"{remoteBase}/{file.relative_to(folder)}"
        try:
            sftpClient.mkdir(str(Path(remotePath).parent))
        except IOError:
            pass
        sftpClient.put(str(file), remotePath)

sftpClient.close()
sshClient.exec_command(r"rm -rf '\root\vm'")
sshClient.close()