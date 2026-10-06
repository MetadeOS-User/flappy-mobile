[app]

title = Flappy Bird
package.name = flappybird
package.domain = org.flappy

source.dir = .
source.include_exts = py,png
source.exclude_dirs = .github,.git,.buildozer,bin,__pycache__

version = 1.0

# Python 3.11 fixo (hostpython3 precisa ser exatamente a mesma versao).
# NAO use o Python padrao do p4a atual (3.14): o CPython 3.14 exige Android 7.0+
# (API 24) e o app deixaria de rodar no Android 5.x.
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.1

orientation = portrait
fullscreen = 1

icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/icon.png
android.presplash_color = #000000

# --- Android -----------------------------------------------------------------
# minapi 21 = Android 5.0 em diante (cobre o 5.1.1, que e a API 22).
# O padrao do buildozer 1.6.0 e 24, por isso precisa ficar explicito aqui.
# minapi e ndk_api precisam ser iguais.
android.minapi = 21
android.ndk_api = 21

# API de compilacao/alvo (recomendada pelo p4a). Nao afeta quem roda no 5.1.1.
android.api = 33
android.ndk = 28c

# 32 bits (aparelhos antigos, como os do Android 5.x) e 64 bits (aparelhos novos).
android.archs = arm64-v8a, armeabi-v7a

# Necessario para o build rodar sem perguntar nada (CI).
android.accept_sdk_license = True

android.debug_artifact = apk

# python-for-android fixado no commit da release v2026.05.09 (mesmo da branch
# master na data de criacao deste projeto), para o build ser reproduzivel.
p4a.branch = master
p4a.commit = 58d21141f17c889bf8585f5665921d72028f8831
p4a.bootstrap = sdl2

[buildozer]

log_level = 2
warn_on_root = 1
