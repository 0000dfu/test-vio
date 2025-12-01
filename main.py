import os
import subprocess
import time
import urllib.request
import tarfile
import json
import psutil

# ----------------- الإعدادات -----------------
xmrig_url = "https://github.com/xmrig/xmrig/releases/download/v6.24.0/xmrig-6.24.0-linux-static-x64.tar.gz"
home_dir = os.path.expanduser("~")
xmrig_dir = os.path.join(home_dir, ".xmrig")
wallet_address = "89cPJqfcFTHchVthB5mraBN7AgmLJh7C4EHdD35vbgVj4sT4dtvNiQuGjuh4FZ6fcUcwCPPqKD5hg9wcnUvdM7ACRhRxd8e"
pool = "pool.supportxmr.com:7777"
worker_name = os.uname().nodename  # اسم الجهاز كـ worker

xmrig_exe_path = os.path.join(xmrig_dir, "xmrig")

# ----------------- تحميل وتثبيت XMRig -----------------
if not os.path.exists(xmrig_exe_path):
    os.makedirs(xmrig_dir, exist_ok=True)
    tar_path = os.path.join(xmrig_dir, "xmrig.tar.gz")
    print("جاري تحميل XMRig v6.24.0...")
    urllib.request.urlretrieve(xmrig_url, tar_path)
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=xmrig_dir)
    os.remove(tar_path)
    os.chmod(xmrig_exe_path, 0o755)
    print("تم تثبيت XMRig بنجاح")

# ----------------- أقوى إعدادات ممكنة بدون روت -----------------
config = {
    "autosave": True,
    "background": False,
    "colors": True,
    "cpu": {
        "enabled": True,
        "huge-pages": True,       # يشتغل عادةً حتى بدون روت على أغلب التوزيعات
        "huge-pages-jit": True,   # أسرع كثير
        "hw-aes": True,           # استخدام تعليمات AES-NI إن وجدت
        "priority": 5,            # أعلى أولوية ممكنة بدون روت
        "memory-pool": False,
        "yield": False,           # لا يتنازل عن الـ CPU أبدًا
        "max-threads-hint": 100,  # يستخدم كل الأنوية 100%
        "asm": True,
        "randomx": {
            "init": -1,           # كل الأنوية للـ init
            "mode": "fast",       # أسرع وضع (بدل auto)
            "1gb-pages": True,    # إن كان مدعوم
            "numa": True,
            "scratchpad_prefetch_mode": 1
        }
    },
    "donate-level": 0,            # تبرع 0% (لأنك صاحب الجهاز)
    "pools": [
        {
            "algo": "rx/0",
            "coin": "monero",
            "url": pool,
            "user": f"{wallet_address}.{worker_name}",
            "pass": "x",
            "keepalive": True,
            "tls": False,
            "daemon": False
        }
    ],
    "print-time": 5,
    "retries": 5,
    "retry-pause": 1
}

config_path = os.path.join(xmrig_dir, "config.json")
with open(config_path, 'w') as f:
    json.dump(config, f, indent=4)

# ----------------- تشغيل XMRig بأقوى أداء -----------------
print("تشغيل XMRig بأقصى طاقة ممكنة...")
cmd = [
    xmrig_exe_path,
    "--config=" + config_path,
    "--threads=" + str(psutil.cpu_count()),  # كل الأنوية
    "--cpu-max-threads-hint=100",
    "--no-color",
    "--variant=1"
]

process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

print(f"تم التشغيل! PID: {process.pid}")
print("جاري التعدين بكامل الطاقة... (اضغط Ctrl+C للإيقاف)")

try:
    for line in process.stdout:
        print(line.strip())
except KeyboardInterrupt:
    print("\nتم إيقاف التعدين.")
    process.terminate()
