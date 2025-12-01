import os
import subprocess
import psutil
import time
import urllib.request
import tarfile
import json

# ----------------- الإعدادات -----------------
xmrig_url = "https://github.com/xmrig/xmrig/releases/download/v6.24.0/xmrig-6.24.0-linux-static-x64.tar.gz"
xmrig_dir = os.path.expanduser("~/xmrig")
wallet_address = "89cPJqfcFTHchVthB5mraBN7AgmLJh7C4EHdD35vbgVj4sT4dtvNiQuGjuh4FZ6fcUcwCPPqKD5hg9wcnUvdM7ACRhRxd8e"
pool = "pool.supportxmr.com:7777"
worker_name = "MyWorker" # يمكنك تغيير هذا الاسم لتمييز عمالك

# ----------------- تحميل وفك ضغط XMRig إذا لم يكن موجودًا -----------------
xmrig_exe_path = os.path.join(xmrig_dir, "xmrig-6.24.0", "xmrig")

if not os.path.exists(xmrig_exe_path):
    print("XMRig غير موجود، سيتم التحميل...")
    os.makedirs(xmrig_dir, exist_ok=True)
    tar_path = os.path.join(xmrig_dir, "xmrig.tar.gz")
    
    print("تحميل XMRig...")
    urllib.request.urlretrieve(xmrig_url, tar_path)
    
    print("فك ضغط XMRig...")
    with tarfile.open(tar_path, "r:gz") as tar:
        # The filter argument is added to address the DeprecationWarning
        tar.extractall(path=xmrig_dir, filter='data')
    os.remove(tar_path)
    
    if not os.path.exists(xmrig_exe_path):
        raise FileNotFoundError(f"ملف XMRig لم يتم العثور عليه في المسار المتوقع: {xmrig_exe_path}")
    
    os.chmod(xmrig_exe_path, 0o755)
    print("تم تثبيت XMRig بنجاح.")

# ----------------- إنشاء ملف الإعدادات config.json -----------------
config = {
    "autosave": True,
    "cpu": {
        "enabled": True,
        "huge-pages": True,
        "hw-aes": None,
        "priority": 5,
        "yield": False,
        "asm": True,
        "rdmsr": True,
        "wrmsr": True,
        "randomx": {
            "1gb-pages": True,
            "mode": "auto",
            "numa": True
        }
    },
    "pools": [
        {
            "algo": "rx/0",
            "coin": "monero",
            "url": pool,
            "user": f"{wallet_address}.{worker_name}",
            "pass": "x",
            "keepalive": True,
            "tls": False
        }
    ]
}

config_path = os.path.join(xmrig_dir, "xmrig-6.24.0", "config.json")
with open(config_path, 'w') as f:
    json.dump(config, f, indent=4)

print("تم إنشاء ملف config.json بالإعدادات المثلى.")

# ----------------- تشغيل XMRig -----------------
print("بدء تشغيل XMRig...")

# تم تعديل هذا الجزء: تمت إزالة 'sudo' من أمر التشغيل
cmd = [
    xmrig_exe_path,
    "--config", config_path
]

try:
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(f"تم تشغيل XMRig بنجاح. معرّف العملية (PID): {process.pid}")
    print("يمكنك متابعة المخرجات أدناه. اضغط Ctrl+C لإيقاف العرض (لن يوقف التعدين).")

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
            
except KeyboardInterrupt:
    print("\nتم إيقاف عرض المخرجات. عملية التعدين مستمرة في الخلفية.")
    print(f"لإيقاف التعدين، يمكنك استخدام الأمر: kill {process.pid}")
except Exception as e:
    print(f"حدث خطأ أثناء تشغيل XMRig: {e}")

