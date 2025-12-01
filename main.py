import os
import subprocess
import urllib.request
import tarfile
import json
import psutil
import glob

# ----------------- الإعدادات -----------------
xmrig_url = "https://github.com/xmrig/xmrig/releases/download/v6.24.0/xmrig-6.24.0-linux-static-x64.tar.gz"
home_dir = os.path.expanduser("~")
xmrig_dir = os.path.join(home_dir, ".xmrig")
wallet_address = "89cPJqfcFTHchVthB5mraBN7AgmLJh7C4EHdD35vbgVj4sT4dtvNiQuGjuh4FZ6fcUcwCPPqKD5hg9wcnUvdM7ACRhRxd8e"
pool = "pool.supportxmr.com:7777"
worker_name = os.uname().nodename

os.makedirs(xmrig_dir, exist_ok=True)

# ----------------- تحميل واستخراج XMRig -----------------
tar_path = os.path.join(xmrig_dir, "xmrig.tar.gz")

if not glob.glob(os.path.join(xmrig_dir, "**/xmrig"), recursive=True):
    print("جاري تحميل XMRig...")
    urllib.request.urlretrieve(xmrig_url, tar_path)
    
    print("جاري فك الضغط...")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=xmrig_dir, filter='data')  # filter='data' لتجنب التحذير في بايثون 3.14+
    
    os.remove(tar_path)
    print("تم التحميل والفك بنجاح")

# ----------------- إيجاد مسار xmrig التنفيذي تلقائيًا -----------------
xmrig_exe_path = None
for root, dirs, files in os.walk(xmrig_dir):
    if "xmrig" in files:
        candidate = os.path.join(root, "xmrig")
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK) or not candidate.endswith(".exe"):
            xmrig_exe_path = candidate
            break

if not xmrig_exe_path:
    # البحث بالـ glob (أكثر موثوقية)
    matches = glob.glob(os.path.join(xmrig_dir, "**/xmrig"), recursive=True)
    if matches:
        xmrig_exe_path = matches[0]

if not xmrig_exe_path or not os.path.exists(xmrig_exe_path):
    raise FileNotFoundError("لم يتم العثور على ملف xmrig التنفيذي! تأكد من التحميل.")

# جعله قابل للتنفيذ
os.chmod(xmrig_exe_path, 0o755)
print(f"تم العثور على XMRig في: {xmrig_exe_path}")

# ----------------- إعداد config.json بأقوى إعدادات -----------------
config = {
    "autosave": True,
    "background": False,
    "colors": False,
    "donate-level": 0,
    "cpu": {
        "enabled": True,
        "huge-pages": True,
        "huge-pages-jit": True,
        "hw-aes": True,
        "priority": 5,
        "yield": False,
        "max-threads-hint": 100,
        "asm": True,
        "randomx": {
            "init": -1,
            "mode": "fast",
            "1gb-pages": True,
            "numa": True,
            "scratchpad_prefetch_mode": 1
        }
    },
    "pools": [{
        "algo": "rx/0",
        "url": pool,
        "user": f"{wallet_address}.{worker_name}",
        "pass": "x",
        "keepalive": True,
        "tls": False
    }],
    "retries": 10,
    "retry-pause": 1,
    "print-time": 5
}

config_path = os.path.join(xmrig_dir, "config.json")
with open(config_path, 'w') as f:
    json.dump(config, f, indent=4)

# ----------------- تشغيل XMRig بكامل الطاقة -----------------
cmd = [
    xmrig_exe_path,
    "--config=" + config_path,
    "--cpu-max-threads-hint=100",
    "--no-color"
]

print("جاري تشغيل XMRig بأقصى طاقة...")
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

print("التعدين بدأ بكامل الطاقة! اضغط Ctrl+C للإيقاف")
try:
    for line in process.stdout:
        print(line, end='')
except KeyboardInterrupt:
    print("\nتم إيقاف التعدين")
    process.terminate()
