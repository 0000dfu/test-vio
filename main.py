import os
import subprocess
import time
import urllib.request
import tarfile
import json

# ----------------- الإعدادات -----------------
xmrig_url = "https://github.com/xmrig/xmrig/releases/download/v6.24.0/xmrig-6.24.0-linux-static-x64.tar.gz"
# استخدم مسارًا داخل مجلد المستخدم الحالي لضمان الصلاحية
home_dir = os.path.expanduser("~")
xmrig_dir = os.path.join(home_dir, "xmrig")
wallet_address = "89cPJqfcFTHchVthB5mraBN7AgmLJh7C4EHdD35vbgVj4sT4dtvNiQuGjuh4FZ6fcUcwCPPqKD5hg9wcnUvdM7ACRhRxd8e"
pool = "pool.supportxmr.com:7777"
worker_name = "MyWorker"

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
        tar.extractall(path=xmrig_dir)
    os.remove(tar_path)
    
    if not os.path.exists(xmrig_exe_path):
        raise FileNotFoundError(f"ملف XMRig لم يتم العثور عليه في المسار المتوقع: {xmrig_exe_path}")
    
    os.chmod(xmrig_exe_path, 0o755)
    print("تم تثبيت XMRig بنجاح.")

# ----------------- إنشاء ملف الإعدادات config.json -----------------
config_dir = os.path.join(xmrig_dir, "xmrig-6.24.0")
config_path = os.path.join(config_dir, "config.json")
os.makedirs(config_dir, exist_ok=True)

# تم تعديل الإعدادات لتعطيل الميزات التي تتطلب صلاحيات عالية
config = {
    "autosave": True,
    "cpu": {
        "enabled": True,
        "huge-pages": False,  # تعطيل لأنها تتطلب صلاحيات
        "rdmsr": False,       # تعطيل لأنها تتطلب صلاحيات
        "wrmsr": False,       # تعطيل لأنها تتطلب صلاحيات
        "priority": 0,        # أولوية عادية
        "asm": True,
        "randomx": {
            "mode": "auto",
            "numa": True
        }
    },
    "pools": [{
        "algo": "rx/0", "coin": "monero", "url": pool,
        "user": f"{wallet_address}.{worker_name}",
        "pass": "x", "keepalive": True, "tls": False
    }]
}

with open(config_path, 'w') as f:
    json.dump(config, f, indent=4)

print("تم إنشاء ملف config.json بالإعدادات المتوافقة مع البيئة الحالية.")

# ----------------- تشغيل XMRig -----------------
print("بدء تشغيل XMRig...")

cmd = [xmrig_exe_path, "--config", config_path]

try:
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(f"تم تشغيل XMRig بنجاح. معرّف العملية (PID): {process.pid}")
    print("يمكنك متابعة المخرجات أدناه.")

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
            
except KeyboardInterrupt:
    print("\nتم إيقاف عرض المخرجات.")
except Exception as e:
    print(f"حدث خطأ أثناء تشغيل XMRig: {e}")
