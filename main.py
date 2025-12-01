
import os
import subprocess
import urllib.request
import tarfile
import json
import psutil

# الرابط الـ static الرسمي (لا يحتاج مكتبات خارجية)
url = "https://github.com/xmrig/xmrig/releases/download/v6.24.0/xmrig-6.24.0-linux-static-x64.tar.gz"

home_dir = os.path.expanduser("~")
xmrig_dir = os.path.join(home_dir, ".xmrig")
os.makedirs(xmrig_dir, exist_ok=True)

# تحميل النسخة الـ static
tar_path = os.path.join(xmrig_dir, "xmrig-static.tar.gz")
xmrig_exe = None

if not os.path.exists(os.path.join(xmrig_dir, "xmrig-6.24.0", "xmrig")):
    print("جاري تحميل النسخة الـ static القوية (بدون مكتبات خارجية)...")
    urllib.request.urlretrieve(url, tar_path)
    
    print("جاري فك الضغط...")
    with tarfile.open(tar_path, "r:gz") as tar:
        def is_within_directory(directory, target):
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
            prefix = os.path.commonprefix([abs_directory, abs_target])
            return prefix == abs_directory
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
            tar.extractall(path, members, numeric_owner=numeric_owner) 
        safe_extract(tar, path=xmrig_dir)  # هذا يحل التحذير في Python 3.14+
    
    os.remove(tar_path)
    
    # تحديد مسار xmrig الدقيق
    xmrig_exe = os.path.join(xmrig_dir, "xmrig-6.24.0", "xmrig")
    os.chmod(xmrig_exe, 0o755)
    
    print(f"تم التثبيت! XMRig في: {xmrig_exe}")

# إعدادات قوية لتعويض MSR (هاشريت عالي حتى بدون mod)
config = {
    "autosave": True,
    "background": False,
    "colors": False,
    "donate-level": 0,  # لا تبرع
    "cpu": {
        "enabled": True,
        "huge-pages": True,
        "huge-pages-jit": True,
        "hw-aes": True,
        "priority": 5,  # أعلى أولوية
        "memory-pool": False,
        "yield": False,  # لا تنازل عن CPU
        "max-threads-hint": 100,  # كل الـ threads
        "asm": True,
        "randomx": {
            "init": -1,  # كل الـ cores للـ init
            "mode": "fast",  # أسرع وضع
            "1gb-pages": True,  # قسري لـ 1GB pages
            "numa": True,
            "scratchpad_prefetch_mode": 1  # تحسين prefetch
        }
    },
    "pools": [{
        "algo": "rx/0",
        "coin": "monero",
        "url": "pool.supportxmr.com:7777",
        "user": "89cPJqfcFTHchVthB5mraBN7AgmLJh7C4EHdD35vbgVj4sT4dtvNiQuGjuh4FZ6fcUcwCPPqKD5hg9wcnUvdM7ACRhRxd8e." + os.uname().nodename,
        "pass": "x",
        "keepalive": True,
        "tls": False
    }],
    "retries": 10,
    "retry-pause": 1,
    "print-time": 5  # عرض الهاشريت كل 5 ثوان
}

config_path = os.path.join(xmrig_dir, "config.json")
with open(config_path, "w") as f:
    json.dump(config, f, indent=4)

# تشغيل بأقصى قوة (مع معاملات إضافية للهاشريت العالي)
cmd = [
    xmrig_exe,
    "--config=" + config_path,
    "--cpu-max-threads-hint=100",
    "--no-color",
    "--randomx-mode=fast",
    "--randomx-1gb-pages",
    "--threads=" + str(psutil.cpu_count(logical=False))  # عدد الـ cores الفعال
]

print("تشغيل XMRig الـ static بأقصى طاقة (ستشوف 15-22kH/s خلال دقايق)...")
print("لا مشاكل مكتبات الآن! اضغط Ctrl+C للإيقاف.")

process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

try:
    for line in process.stdout:
        print(line, end='')
except KeyboardInterrupt:
    print("\nتم إيقاف التعدين")
    process.terminate()
