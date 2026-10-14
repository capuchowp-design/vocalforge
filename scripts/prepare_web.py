#!/usr/bin/env python3
"""Monta a pasta www/ (o app que vai dentro do APK) a partir dos arquivos do repositório.

- Copia index.html, manifest.json, privacy.html e os ícones (NÃO copia sw.js: no APK não precisa).
- Se as bibliotecas estiverem instaladas (npm install), usa Tone.js e a fonte Inter LOCAIS (funciona offline).
  Se não estiverem, mantém os links da internet que já estão no index.html.
- Esconde o botão PIX no APK (defina SHOW_PIX=1 para mostrar).
"""
import glob, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WWW = os.path.join(ROOT, "www")
VENDOR = os.path.join(WWW, "vendor")

if os.path.isdir(WWW):
    shutil.rmtree(WWW)
os.makedirs(VENDOR)

for name in ["index.html", "manifest.json", "privacy.html"]:
    src = os.path.join(ROOT, name)
    if os.path.exists(src):
        shutil.copy(src, WWW)
for f in glob.glob(os.path.join(ROOT, "icon*.png")):
    shutil.copy(f, WWW)

index_path = os.path.join(WWW, "index.html")
html = open(index_path, encoding="utf-8").read()

# 1) Tone.js local
tone_src = os.path.join(ROOT, "node_modules", "tone", "build", "Tone.js")
tone_tag = '<script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"></script>'
if os.path.exists(tone_src) and tone_tag in html:
    shutil.copy(tone_src, os.path.join(VENDOR, "Tone.js"))
    html = html.replace(tone_tag, '<script src="vendor/Tone.js"></script>')
    print("Tone.js: local")
else:
    print("AVISO: Tone.js local não encontrado; usando o link da internet.")

# 2) Fonte Inter local
font_files = glob.glob(os.path.join(ROOT, "node_modules", "@fontsource-variable", "inter", "files", "inter-latin-wght-normal.woff2"))
import_line = "@import url('https://cdn.jsdelivr.net/fontsource/fonts/inter@5/latin.css');"
if font_files and import_line in html:
    shutil.copy(font_files[0], os.path.join(VENDOR, "inter-latin-wght-normal.woff2"))
    face = ("@font-face{font-family:'Inter';font-style:normal;font-weight:100 900;font-display:swap;"
            "src:url('vendor/inter-latin-wght-normal.woff2') format('woff2');}")
    html = html.replace(import_line, face)
    print("Inter: local")
else:
    print("AVISO: fonte Inter local não encontrada; usando o link da internet.")

# 3) PIX escondido no APK
if os.environ.get("SHOW_PIX") != "1":
    style = "<style>#btnPix{display:none!important}</style>"
    assert "</head>" in html
    html = html.replace("</head>", style + "\n</head>", 1)
    print("Botão PIX: escondido no APK")

open(index_path, "w", encoding="utf-8").write(html)
print("www pronto:", sorted(os.listdir(WWW)))
