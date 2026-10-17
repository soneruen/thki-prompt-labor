"""
app.py – Web-Oberfläche des THKI Prompt-Labors (Streamlit)
===========================================================

Interaktive Oberfläche für die Experimente aus prompt_labor.py, damit auch
Personen ohne Programmierkenntnisse die Versuche ausführen und bewerten können.
ASC-Lernportfolio (DIS20a, Prof. Linde) · Autor: Necdet Soner Ünal

Design
------
  Dunkles, GitHub-inspiriertes Erscheinungsbild: Theme in
  .streamlit/config.toml, Feinschliff (Karten, Badges, klare Rahmen) in
  assets/style.css.

Aufbau
------
  Seitenleiste   Verbindung (THKI-Schlüssel oder Demo-Modus), Modellauswahl,
                 „Alle Experimente starten“, Ergebnisse zurücksetzen
  Tab 1          Experimente E1–E6: Erklärung, Start, Antworten nebeneinander,
                 automatische Prüfung, Bewertung (Beobachtung / Vor- und
                 Nachteile / Fazit), Bericht als Markdown herunterladen
  Tab 2          Freier Modus: eigener Prompt gegen mehrere Modelle
  Tab 3          Über das Projekt (Kontext, Kompetenzen, Datenschutz)

Start:  Run-Button in VS Code oder „python app.py“ – prüft beim Start
        automatisch Python, .venv, Pakete und .env (fragt ggf. nach dem
        API-Schlüssel) und startet dann Streamlit (siehe setup_check.py).
        Alternativ direkt: streamlit run app.py
Der Schlüssel wird nur lokal verwendet (aus .env oder Eingabefeld) und
nirgends gespeichert.
"""

# --- Imports (Standardbibliothek) ---------------------------------------
import html
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

# --- Ein-Klick-Start ------------------------------------------------------
# Direkt gestartet (Run-Button / „python app.py“) ist Streamlit noch nicht
# geladen: dann prüft setup_check.py Python, .venv, Pakete und .env und
# startet die App anschließend über „streamlit run“. Läuft die Datei bereits
# unter Streamlit, wird dieser Block übersprungen.
if __name__ == "__main__" and "streamlit" not in sys.modules:
    from setup_check import starte
    starte(Path(__file__).resolve())

# --- Imports (Pakete) -----------------------------------------------------
import streamlit as st  # noqa: I001
from dotenv import load_dotenv

from prompt_labor import (
    EXPERIMENTE,
    FACHBEGRIFFE,
    STANDARD_URL,
    Experiment,
    bericht_text,
    chat_modelle,
    erstelle_client,
    frage,
    pruefe,
)


# --- Grundeinstellungen ---------------------------------------------------
st.set_page_config(page_title="THKI Prompt-Labor", page_icon="🧪", layout="wide")
load_dotenv()
ss = st.session_state
ss.setdefault("ergebnisse", {})     # {eid: [ergebnis, ...]}
ss.setdefault("bewertungen", {})    # {eid: {beobachtung, vorteile, fazit}}
ss.setdefault("frei", [])           # Ergebnisse des freien Modus
MAX_MODELLE = 4
KURZ = {"E1": "Modellvergleich", "E2": "Klarheit", "E3": "Prompt-Injection",
        "E4": "JSON", "E5": "Halluzination", "E6": "Priming"}   # kurze Tab-Namen

# --- Design laden ---------------------------------------------------------
CSS = Path(__file__).parent / "assets" / "style.css"
if CSS.exists():
    st.markdown(f"<style>{CSS.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


# --- Hilfsfunktionen ------------------------------------------------------

@st.cache_resource(show_spinner=False)
def verbinde(demo, key, url):
    """Client und Modellliste einmalig laden (pro Schlüssel zwischengespeichert)."""
    client = erstelle_client(demo, api_key=key or None, base_url=url or None)
    return client, chat_modelle(client)


def parallel_fragen(client, auftraege):
    """auftraege: Liste (modell, messages) -> Liste (antwort, sekunden, fehler)."""
    with ThreadPoolExecutor(max_workers=6) as pool:
        return list(pool.map(lambda a: frage(client, a[0], a[1]), auftraege))


def fuehre_aus(client, eid, modelle):
    """Alle Varianten eines Experiments mit allen Modellen ausführen und speichern."""
    exp: Experiment = EXPERIMENTE[eid]
    auftraege = [(v, m, msgs) for v, msgs in exp["varianten"].items() for m in modelle]
    antworten = parallel_fragen(client, [(m, msgs) for _, m, msgs in auftraege])
    ss.ergebnisse[eid] = [
        {"variante": v, "modell": m, "prompt": msgs, "antwort": a, "sekunden": sek, "fehler": f,
         "pruefung": pruefe(exp["check"], a, exp) if a else ""}
        for (v, m, msgs), (a, sek, f) in zip(auftraege, antworten)
    ]
    return sum(1 for r in ss.ergebnisse[eid] if r["fehler"])


def html_md(inhalt):
    st.markdown(inhalt, unsafe_allow_html=True)


def badge(text):
    """Prüfergebnis als farbige Pill: ✅ grün, ⚠️ gelb, ❌ rot, sonst grau."""
    art = "ok" if text.startswith("✅") else "warn" if text.startswith("⚠") else \
          "err" if text.startswith(("❌", "Fehler")) else "info"
    sauber = text.lstrip("✅⚠️❌ ").strip()
    return f'<span class="badge {art}">{html.escape(sauber)}</span>'


def zeige_antworten(eintraege, praefix):
    """Antworten einer Variante als Karten nebeneinander, eine Spalte pro Modell."""
    spalten = st.columns(len(eintraege))
    for i, (spalte, r) in enumerate(zip(spalten, eintraege)):
        with spalte, st.container(key=f"answer_{praefix}_{i}"):
            html_md(f'<div class="model">{html.escape(r["modell"])}</div>'
                    f'<div class="meta">{r["sekunden"]} s</div>')
            if r["fehler"]:
                html_md(badge("Fehler: " + r["fehler"][:200]))
                continue
            if r["pruefung"]:
                html_md(badge(r["pruefung"]))
            with st.container(height=200, border=False):
                st.markdown(r["antwort"])


def fachbegriff_info(text):
    gefunden = [b for b in FACHBEGRIFFE if b.lower() in (text or "").lower()]
    return f"{len((text or '').split())} Wörter · Fachbegriffe: {', '.join(gefunden) or 'keine'}"


# --- Seitenleiste: Verbindung, Modelle, Aktionen --------------------------
with st.sidebar:
    st.markdown("### Verbindung")
    env_key = os.getenv("THKI_API_KEY", "")
    env_key = "" if env_key in ("", "dein_schluessel") else env_key   # Platzhalter ignorieren
    demo = st.toggle("Demo-Modus", value=not env_key,
                     help="Ohne API, mit Testantworten – zum Ausprobieren der Oberfläche.")
    key, url = "", ""
    if not demo:
        key = st.text_input("THKI-API-Schlüssel", value=env_key, type="password",
                            help="Wird nur lokal verwendet. Am besten in der Datei .env eintragen.")
        url = st.text_input("API-Adresse", value=os.getenv("THKI_BASE_URL", STANDARD_URL))
    try:
        client, verfuegbar = verbinde(demo, key, url)
        html_md(badge(f"✅ Verbunden · {len(verfuegbar)} Modelle" + (" (Demo)" if demo else "")))
    except Exception as e:  # noqa: BLE001
        html_md(badge(f"❌ Keine Verbindung: {e}"))
        st.stop()

    st.markdown("### Modelle")
    standard_modelle = [m for m in verfuegbar if "glm" not in m.lower()]
    modelle = st.multiselect(f"Bis zu {MAX_MODELLE} Modelle vergleichen", verfuegbar,
                             default=standard_modelle[:min(2, len(standard_modelle))],
                             max_selections=MAX_MODELLE)
    st.caption("temperature = 0 (wo unterstützt) für möglichst wiederholbare Ergebnisse.")

    st.markdown("### Aktionen")
    if st.button("Alle Experimente starten", type="primary", disabled=not modelle, width="stretch"):
        fortschritt = st.progress(0.0, text="Starte …")
        fehler_gesamt = 0
        for i, k in enumerate(EXPERIMENTE, 1):
            fortschritt.progress((i - 1) / len(EXPERIMENTE), text=f"{k} – {EXPERIMENTE[k]['titel']}")
            fehler_gesamt += fuehre_aus(client, k, modelle)
        fortschritt.progress(1.0, text="Fertig")
        if fehler_gesamt:
            st.warning(f"{fehler_gesamt} Anfrage(n) fehlgeschlagen – Details bei den Antworten.")
    if st.button("Ergebnisse zurücksetzen", disabled=not ss.ergebnisse, width="stretch"):
        ss.ergebnisse, ss.bewertungen, ss.frei = {}, {}, []
        st.rerun()
    st.divider()
    st.caption("Keine personenbezogenen oder vertraulichen Daten eingeben.")

# --- Kopfbereich ----------------------------------------------------------
html_md("""
<div class="hero">
  <div class="eyebrow">ASC-Lernportfolio · Data and AI Literacy</div>
  <h1>THKI Prompt-Labor</h1>
  <p>Sechs Experimente, die zeigen, wie Sprachmodelle der TH Köln auf Prompts reagieren,
  wo sie zuverlässig sind und wo man genau hinsehen sollte.</p>
</div>""")

if not modelle:
    st.info("Bitte links mindestens ein Modell auswählen.")
    st.stop()

tab_exp, tab_frei, tab_info = st.tabs(["Experimente", "Freier Modus", "Über das Projekt"])

# --- Tab 1: Experimente ---------------------------------------------------
with tab_exp:
    eid = st.segmented_control("Experiment", list(EXPERIMENTE), default="E1",
                               format_func=lambda k: f"{k} · {KURZ[k]}",
                               label_visibility="collapsed") or "E1"
    exp = EXPERIMENTE[eid]

    with st.container(key="card_info"):
        links, rechts = st.columns([3, 2], gap="large")
        with links:
            st.markdown(f"## {exp['titel']}")
            html_md(f'<div class="value">{html.escape(exp["ziel"])}</div>'
                    f'<div class="simple"><b>Einfach erklärt.</b> {html.escape(exp["einfach"])}</div>')
        with rechts:
            html_md(f'<div class="label">Kursbezug</div><div class="value">{html.escape(exp["modul"])}</div>'
                    f'<div class="label">Geprüfte Kompetenz</div><div class="value">{html.escape(exp["kompetenz"])}</div>'
                    f'<div class="label">Varianten</div><div class="value">'
                    + "".join(f'<span class="chip">{html.escape(v)}</span>' for v in exp["varianten"]) + "</div>")

    k1, k2 = st.columns([1, 3])
    with k1:
        starten = st.button(f"{eid} starten", type="primary", width="stretch")
    with k2, st.expander("Verwendete Prompts ansehen"):
        for vname, msgs in exp["varianten"].items():
            st.markdown(f"**{vname}**")
            for m in msgs:
                st.markdown(f"- *{m['role']}*: {m['content']}")
    if starten:
        with st.spinner("Modelle antworten …"):
            fehler = fuehre_aus(client, eid, modelle)
        if fehler:
            st.warning(f"{fehler} Anfrage(n) fehlgeschlagen – Details bei den Antworten.")

    if eid in ss.ergebnisse:
        for vname in exp["varianten"]:
            html_md(f'<div class="section">Variante · {html.escape(vname)}</div>')
            zeige_antworten([r for r in ss.ergebnisse[eid] if r["variante"] == vname], f"{eid}_{vname}")

        html_md('<div class="section">Meine Bewertung</div>')
        with st.container(key="card_bewertung"):
            st.caption("Schema wie in Projektaufgabe 07: konkrete Beobachtung → Vor- und Nachteile → Fazit.")
            b = ss.bewertungen.setdefault(eid, {})
            b["beobachtung"] = st.text_area("Beobachtung", b.get("beobachtung", ""), key=f"beo_{eid}")
            b["vorteile"] = st.text_area("Vor- und Nachteile", b.get("vorteile", ""), key=f"vn_{eid}")
            b["fazit"] = st.text_area("Fazit", b.get("fazit", ""), key=f"fa_{eid}")

    if ss.ergebnisse:
        st.write("")
        bericht = bericht_text(ss.ergebnisse, bewertungen=ss.bewertungen)  # Modelle aus Ergebnissen
        st.download_button(f"Bericht herunterladen · {len(ss.ergebnisse)} Experiment(e)", bericht,
                           file_name=f"{datetime.now().astimezone():%Y-%m-%d_%H%M}_bericht.md", mime="text/markdown")

# --- Tab 2: Freier Modus --------------------------------------------------
with tab_frei:
    with st.container(key="card_frei"):
        st.markdown("## Eigenen Prompt testen")
        st.caption("Derselbe Prompt geht an alle ausgewählten Modelle, die Antworten erscheinen nebeneinander.")
        system = st.text_area("System-Prompt (optional)", placeholder="z. B. Erkläre alles für Laien ohne Fachbegriffe.")
        user = st.text_area("Deine Frage", placeholder="z. B. Was ist der Unterschied zwischen KI und klassischer Software?")
        senden = st.button("Senden", type="primary", disabled=not user.strip())
    if senden:
        msgs = ([{"role": "system", "content": system}] if system.strip() else []) + \
               [{"role": "user", "content": user}]
        with st.spinner("Modelle antworten …"):
            antworten = parallel_fragen(client, [(m, msgs) for m in modelle])
        ss.frei = [{"modell": m, "antwort": a, "sekunden": sek, "fehler": f,
                    "pruefung": fachbegriff_info(a) if a else ""}
                   for m, (a, sek, f) in zip(modelle, antworten)]
    if ss.frei:
        st.write("")
        zeige_antworten(ss.frei, "frei")

# --- Tab 3: Über das Projekt ----------------------------------------------
with tab_info, st.container(key="card_about"):
    st.markdown("## Worum geht es?")
    st.markdown("""
Dieses Labor ist die **praktische Anwendung** des Kurses *Data and AI Literacy* (SS 2026, Prof. Dr. Simone
Fühles-Ubach) im Rahmen meines ASC-Lernportfolios bei Prof. Dr. Frank Linde. Aus jedem der sieben Kursmodule
habe ich eine zentrale Erkenntnis in ein überprüfbares Experiment übersetzt.

**Bezug zu meinen Portfolio-Zielen**
- **Klarheit:** Jedes Experiment hat eine Erklärung in einfacher Sprache. E2 misst, wie Fachbegriffe und
  Verständlichkeit von der Zielgruppe abhängen.
- **Feedbackfähigkeit:** Bewertungen folgen dem Schema *Beobachtung → Vor- und Nachteile → Fazit*.
""")
    st.markdown("| Nr. | Experiment | Kursmodul | Kompetenz |\n|---|---|---|---|\n" + "\n".join(
        f"| {k} | {e['titel']} | {e['modul']} | {e['kompetenz']} |" for k, e in EXPERIMENTE.items()))
    st.markdown("""
**Warum THKI?** Die offenen Modelle laufen über KI:connect.nrw in Deutschland bzw. NRW, und es fließen keine
Daten an die Modellanbieter. Über eine Schnittstelle lassen sich viele Modelle direkt vergleichen.

**Grenzen:** Die automatischen Prüfungen sind einfache Regeln und ersetzen nicht die eigene Bewertung.
Modelle ändern sich durch Updates. Es gibt nur wenige Prompts pro Experiment, also ist das ein Lernlabor,
keine statistische Studie.

Die Antworten stammen von den jeweils gewählten THKI-Modellen.
""")
