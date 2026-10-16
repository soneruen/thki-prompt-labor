"""
setup_check.py – Ein-Klick-Start für das THKI Prompt-Labor
==========================================================

Wird automatisch ausgeführt, wenn app.py direkt gestartet wird (Run-Button in
VS Code oder „python app.py“). Nutzt nur die Python-Standardbibliothek, damit
es auch ohne installierte Pakete läuft. Funktioniert unter Windows, macOS
und Linux.

Ablauf
------
  1. Python-Version prüfen (mind. 3.9)
  2. Virtuelle Umgebung .venv: anlegen, falls nötig, und das Skript darin
     neu starten (Windows: .venv\\Scripts\\python.exe, sonst .venv/bin/python)
  3. Pakete aus requirements.txt prüfen und fehlende/zu alte installieren
  4. .env prüfen: fehlt sie, wird sie angelegt. Ist kein API-Schlüssel
     eingetragen, wird im Terminal danach gefragt (verdeckte Eingabe).
     Mit „q“ (oder Enter) überspringen: Die App startet dann im
     Demo-Modus und der Schlüssel kann links in der Seitenleiste
     eingegeben werden.
  5. App über „streamlit run app.py“ starten
"""

# --- Imports --------------------------------------------------------------
import getpass
import os
import platform
import re
import subprocess
import sys
from importlib import metadata
from pathlib import Path

ORDNER = Path(__file__).resolve().parent
VENV = ORDNER / ".venv"
REQUIREMENTS = ORDNER / "requirements.txt"
ENV_DATEI = ORDNER / ".env"
STANDARD_URL = "https://chat.kiconnect.nrw/api/v1"
PLATZHALTER = {"", "dein_schluessel"}
IST_WINDOWS = platform.system() == "Windows"


# --- Ausgabe --------------------------------------------------------------

def info(text):
    print(f"  {text}", flush=True)


def schritt(nr, text):
    print(f"\n[{nr}/5] {text}", flush=True)


# --- 1. Python-Version ----------------------------------------------------

def pruefe_python():
    schritt(1, "Python-Version")
    if sys.version_info < (3, 9):
        sys.exit(f"  ✗ Python {platform.python_version()} ist zu alt – bitte Python 3.9 oder neuer installieren.")
    info(f"✓ Python {platform.python_version()} ({platform.system()})")


# --- 2. Virtuelle Umgebung ------------------------------------------------

def venv_python():
    return VENV / ("Scripts/python.exe" if IST_WINDOWS else "bin/python")


def in_venv():
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix)


def sichere_venv(app):
    """Läuft das Skript außerhalb einer venv, wird .venv genutzt bzw. angelegt
    und die App mit deren Python neu gestartet (gibt dann nicht zurück)."""
    schritt(2, "Virtuelle Umgebung")
    if in_venv():
        info(f"✓ aktiv: {sys.prefix}")
        return
    if not venv_python().exists():
        info("• .venv wird angelegt …")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV)])
    info("✓ .venv bereit – Neustart darin")
    sys.exit(subprocess.call([str(venv_python()), str(app)]))


# --- 3. Pakete ------------------------------------------------------------

def _version_tupel(v):
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])


def fehlende_pakete():
    """Liest requirements.txt (Format name>=version) und gibt fehlende oder
    zu alte Pakete zurück."""
    fehlend = []
    for zeile in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        zeile = zeile.split("#")[0].strip()
        if not zeile:
            continue
        m = re.match(r"([A-Za-z0-9_.\-]+)\s*(?:>=\s*([\d.]+))?", zeile)
        name, mindest = m.group(1), m.group(2)
        try:
            installiert = metadata.version(name)
        except metadata.PackageNotFoundError:
            fehlend.append(f"{name} (nicht installiert)")
            continue
        if mindest and _version_tupel(installiert) < _version_tupel(mindest):
            fehlend.append(f"{name} ({installiert} < {mindest})")
    return fehlend


def pruefe_pakete():
    schritt(3, "Pakete aus requirements.txt")
    fehlend = fehlende_pakete()
    if not fehlend:
        info("✓ alle Pakete vorhanden")
        return
    for f in fehlend:
        info(f"• {f}")
    info("• Installation läuft …")
    code = subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "-r", str(REQUIREMENTS)])
    if code != 0 or fehlende_pakete():
        sys.exit("  ✗ Installation fehlgeschlagen – bitte Ausgabe oben prüfen.")
    info("✓ Pakete installiert")


# --- 4. .env und API-Schlüssel --------------------------------------------

def lies_env():
    werte = {}
    if ENV_DATEI.exists():
        for zeile in ENV_DATEI.read_text(encoding="utf-8").splitlines():
            if "=" in zeile and not zeile.lstrip().startswith("#"):
                k, v = zeile.split("=", 1)
                werte[k.strip()] = v.strip().strip('"').strip("'")
    return werte


def schreibe_env(key, url):
    ENV_DATEI.write_text(
        "# Lokale Zugangsdaten – diese Datei NIE committen (steht in .gitignore)\n"
        f"THKI_API_KEY={key}\n"
        f"THKI_BASE_URL={url}\n",
        encoding="utf-8",
    )


def pruefe_env():
    schritt(4, "API-Schlüssel (.env)")
    neu = not ENV_DATEI.exists()
    werte = lies_env()
    url = werte.get("THKI_BASE_URL") or STANDARD_URL
    if neu:
        schreibe_env("", url)
        info("✓ .env angelegt")
    if werte.get("THKI_API_KEY", "") not in PLATZHALTER:
        info("✓ Schlüssel in .env vorhanden")
        return
    info("Kein THKI-API-Schlüssel eingetragen.")
    try:
        eingabe = getpass.getpass("  Schlüssel eingeben (Eingabe unsichtbar) oder q zum Überspringen: ").strip()
    except (EOFError, KeyboardInterrupt):
        eingabe = "q"
    if eingabe.lower() in {"", "q"}:
        info("→ übersprungen: App startet im Demo-Modus, Schlüssel links in der Seitenleiste eingeben.")
        return
    schreibe_env(eingabe, url)
    info("✓ Schlüssel in .env gespeichert")


# --- 5. Start -------------------------------------------------------------

def starte(app):
    """Kompletter Ablauf; wird von app.py aufgerufen und kehrt nicht zurück."""
    print("THKI Prompt-Labor – Startprüfung")
    pruefe_python()
    sichere_venv(app)
    pruefe_pakete()
    pruefe_env()
    schritt(5, "App starten")
    info("Browser öffnet sich gleich · beenden mit Ctrl+C\n")
    try:
        code = subprocess.call([sys.executable, "-m", "streamlit", "run", str(app)], cwd=str(ORDNER))
    except KeyboardInterrupt:
        code = 0
    sys.exit(code)
