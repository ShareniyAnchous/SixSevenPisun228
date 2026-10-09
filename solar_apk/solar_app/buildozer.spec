[app]

# === Идентификация ===
title = Solar
package.name = solar
package.domain = org.solar
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.0
requirements = python3,kivy,android,openssl,pyjnius

# Ориентация и UI
orientation = portrait
fullscreen = 0
os.environ = OPENSSL_VERSION=1.1.1w

# Права: только интернет
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# Иконка (создайте solar_app/solar.png 512x512 или удалите строки — будет дефолтная)
# icon.filename = solar.png

[buildozer]
log_level = 2
warn_on_root = 1
