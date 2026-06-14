[app]
title = Nadea
package.name = nadea
package.domain = org.unahur
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 7.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,plyer,cython==3.0.11,pillow,pyjnius==1.5.0

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,SEND_SMS,READ_SMS,RECEIVE_SMS,BLUETOOTH,ACCESS_COARSE_LOCATION,ACCESS_FINE_LOCATION
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a
p4a.branch = v2023.09.16

[buildozer]
log_level = 2
warn_on_root = 1
