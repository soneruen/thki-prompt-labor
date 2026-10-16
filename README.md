# THKI Prompt-Labor

Ein kleines Versuchslabor mit **Web-Oberfläche**, das dieselben kontrollierten Prompts an mehrere Sprachmodelle der TH-Köln-KI (**THKI**, über KI:connect.nrw) schickt, die Antworten automatisch vorprüft und daraus einen Versuchsbericht erstellt. Das Projekt wurde im Rahmen des **ASC-Lernportfolios** als praktische Anwendung der im Kurs **„Data and AI Literacy“** erworbenen Kompetenzen entwickelt.

**Autor:** Necdet Soner Ünal
**Kontext:** ASC-Lernportfolio (Modul DIS20a, Prof. Dr. Frank Linde), TH Köln, WS 2026/27

---

## Anlass und Ziel des Projekts

Im Sommersemester 2026 habe ich als erste ASC-Aktivität den Kurs **„Data and AI Literacy“** (Prof. Dr. Simone Fühles-Ubach, 4 ECTS, 7 Module mit Projektaufgaben) abgeschlossen. Im Rahmen des ASC-Lernportfolios sollte das im Kurs erworbene Wissen nicht nur theoretisch dokumentiert, sondern in eine praktische Anwendung überführt werden. Prof. Dr. Frank Linde hat dazu angeregt, den Kurs durch konkrete praktische Aktivitäten zu begleiten und die erworbenen Kompetenzen an einem eigenen Projekt anzuwenden.

Dieses Projekt setzt diesen Impuls um. Ich habe aus den Kursmodulen zentrale Erkenntnisse und Fähigkeiten – unter anderem strukturiertes Prompting, das Erkennen von Halluzinationen, die Bewertung von KI-Ausgaben sowie die Auseinandersetzung mit Sicherheit und Ethik – in sechs überprüfbare Experimente übersetzt. Diese Experimente werden mit echten Sprachmodellen durchgeführt und in einem Bericht nachvollziehbar ausgewertet.

Es zahlt außerdem auf meine beiden Portfolio-Ziele ein:

- **Klarheit:** Experiment E2 misst, wie sich Fachbegriff-Dichte und Verständlichkeit mit der Zielgruppe ändern. Dieses README und die Berichte sind für Leser:innen ohne KI-Vorwissen geschrieben.
- **Feedbackfähigkeit:** Jede Bewertung folgt dem Schema *Beobachtung → Vor- und Nachteile → Fazit* (wie in Projektaufgabe 07). Statt „gut/schlecht“ werden konkrete, belegbare Punkte benannt.

## Was wird getestet?

| Nr. | Experiment | Kursmodul | Erworbene Kompetenz | Was geprüft wird |
|---|---|---|---|---|
| E1 | Modellvergleich | 01 Grundlagen KI | Ausgaben verschiedener Modelle vergleichen und Unterschiede begründen | gleiche Frage an mehrere Modelle: Länge, Inhalt, Zeit |
| E2 | System-Prompt & Klarheit | 02 Daten bereitstellen | KI-Verhalten über System-Prompts steuern | dieselbe Erklärung ohne Vorgabe, für Fachpublikum und für Laien; Anzahl Fachbegriffe |
| E3 | Prompt-Injection | 02/03 Prompting & Sicherheit | Sicherheitsgrenzen gezielt testen | drei Angriffe (direkt, „Debug-Modus“, Umweg über Gedicht) auf ein geheimes Codewort |
| E4 | JSON-Ausgabe | 04 Daten auswerten (OpenWebUI, System-Prompts) | maschinenlesbare, überprüfbare Ausgaben erzeugen | wird ein vorgegebenes JSON-Schema exakt eingehalten? |
| E5 | Halluzination | 05/06 Interpretieren & Einordnen | Glaubwürdigkeit von Richtigkeit unterscheiden | Frage nach einer **erfundenen** Studie: gibt das Modell Unwissen zu? |
| E6 | Priming (Trolley-Problem) | 07 Ethik & Publizieren | Abhängigkeit moralischer KI-Aussagen vom Prompt erkennen | neutrale vs. deontologisch bzw. utilitaristisch vorgeprägte Frage |

**Einfach erklärt:**

- **System-Prompt:** eine versteckte Anweisung, die einem Chatbot vorab sagt, wie er sich verhalten soll, etwa „Erkläre alles für Kinder“.
- **Prompt-Injection:** der Versuch, diese Anweisung durch geschickte Formulierungen auszuhebeln.
- **Halluzination:** Die KI erfindet etwas, das überzeugend klingt, aber nicht stimmt.
- **Priming:** Eine vorangestellte Meinung lenkt die Antwort in eine Richtung.

## Warum THKI?

- Die offenen Modelle laufen in Deutschland bzw. NRW, und es gehen keine Daten an die Modellanbieter (Datenschutz, Modul 06/07).
- Über eine einzige, OpenAI-kompatible Schnittstelle lassen sich viele Modelle direkt vergleichen.
- Es ist die Infrastruktur, die alle TH-Angehörigen nutzen. Die Ergebnisse helfen also anderen Studierenden, die Hochschul-KI kritisch einzusetzen.

## Erste Nutzung: herunterladen und starten

Voraussetzung ist **Python 3.9 oder neuer**. Für den Start per Mausklick in
VS Code wird außerdem die offizielle Erweiterung **Python** von Microsoft
benötigt.

### Variante A: Repository klonen

1. Das Repository auf GitHub öffnen:
   https://github.com/soneruen/thki-prompt-labor
2. **Code → HTTPS** auswählen und die URL kopieren.
3. Im Terminal an den gewünschten Speicherort wechseln und das Projekt klonen:

   ```bash
   git clone https://github.com/soneruen/thki-prompt-labor.git
   cd thki-prompt-labor
   ```

4. Den Ordner in VS Code öffnen:

   ```bash
   code .
   ```

### Variante B: ZIP-Datei herunterladen

Auf GitHub **Code → Download ZIP** auswählen, die ZIP-Datei entpacken und den
entpackten Ordner in VS Code öffnen. Wichtig ist, dass `app.py` direkt im
geöffneten Projektordner liegt.

### Start per Mausklick

In VS Code die Datei `app.py` öffnen und oben rechts auf **▶ Run Python File**
(*Python-Datei ausführen*) klicken. Beim ersten Start erledigt das Projekt
automatisch:

1. Betriebssystem und Python-Version prüfen (Windows, macOS und Linux)
2. die virtuelle Umgebung `.venv` anlegen
3. alle Pakete aus `requirements.txt` installieren
4. `.env` lokal anlegen und optional nach dem THKI-API-Schlüssel fragen
5. die Streamlit-App starten und den Browser öffnen

Beim ersten Start kann die Paketinstallation etwas dauern. Danach genügt es,
`app.py` erneut zu öffnen und wieder auf den Run-Button zu klicken.

### Start über das Terminal

Falls der Run-Button in VS Code nicht angezeigt wird:

```bash
python app.py
```

Unter macOS/Linux funktioniert alternativ:

```bash
python3 app.py
```

`setup_check.py` erkennt das Betriebssystem selbst und verwendet automatisch
den passenden Pfad für die virtuelle Umgebung. Die App öffnet sich danach
unter `http://localhost:8501`.

Wenn kein API-Schlüssel vorhanden ist, kann die Abfrage mit **Enter** oder
`q` übersprungen werden. Die App startet dann im Demo-Modus; ein Schlüssel
kann später links in der Seitenleiste eingegeben werden. `.env` steht in
`.gitignore` und wird nie hochgeladen.

## Manuelle Installation

Falls der automatische Start nicht verwendet werden soll:

<details><summary>Manuell, ohne Startprüfung</summary>

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Schlüssel eintragen
streamlit run app.py
```
</details>

## Benutzung

### Web-Oberfläche (empfohlen)

```bash
streamlit run app.py
```

Die Oberfläche ist dunkel und kompakt im GitHub-Stil gehalten: klare Rahmen, gut lesbare Systemschrift und farbige Status-Badges.

- **Seitenleiste:** Hier verbindest du dich mit THKI. Ist kein Schlüssel hinterlegt, startet die App im Demo-Modus mit Testantworten. Dort wählst du auch bis zu 4 Modelle aus, startest mit **Alle Experimente starten** den kompletten Lauf und setzt die Ergebnisse zurück.
- **Experimente:** E1–E6 auswählen. Jedes Experiment zeigt eine Erklärung in einfacher Sprache, einen Start-Knopf und die Antworten der Modelle nebeneinander mit automatischer Prüfung. Darunter stehen Eingabefelder für *Beobachtung / Vor- und Nachteile / Fazit*. Den Bericht kannst du als Markdown herunterladen.
- **Freier Modus:** einen eigenen Prompt (optional mit System-Prompt) an alle gewählten Modelle schicken.
- **Über das Projekt:** Kontext, Kompetenz-Tabelle, Datenschutz, Grenzen.

### Kommandozeile

```bash
python prompt_labor.py --dry-run          # Ablauf testen, ohne API
python prompt_labor.py --list-models      # verfügbare Modelle anzeigen
python prompt_labor.py                    # alle Experimente mit den ersten 3 Modellen
python prompt_labor.py -m <modell1> <modell2> -e E2 E5
```

Die Ergebnisse landen in `results/`:

- `…_bericht.md`: lesbarer Bericht mit Tabelle pro Experiment, Antworten im Wortlaut und leeren Feldern **Beobachtung / Vor- und Nachteile / Fazit** zum Ausfüllen
- `…_rohdaten.json`: alle Prompts und Antworten, für die Nachvollziehbarkeit

## Projektstruktur

```
├── app.py             Web-Oberfläche (Streamlit), Startpunkt
├── setup_check.py     Ein-Klick-Start: Python, .venv, Pakete, .env prüfen
├── prompt_labor.py    gemeinsame Logik: Experimente, Prüfungen, API, Bericht (+ CLI)
├── assets/style.css   Design (GitHub-Dark-Stil)
├── .streamlit/        Theme-Konfiguration
├── requirements.txt
├── .env.example       Vorlage für THKI-Schlüssel (als .env kopieren)
└── results/           Berichte der Kommandozeile (nicht im Repo)
```

## Wie die Auswertung funktioniert

Die automatischen Prüfungen sind bewusst einfache, transparente Regeln, zum Beispiel „kommt das Codewort in der Antwort vor?“ oder „ist das gültiges JSON?“. Sie liefern einen ersten Anhaltspunkt, **ersetzen aber nicht die eigene Bewertung**. Das ist eine Kernerkenntnis aus Modul 03: KI-Ergebnisse müssen nachvollziehbar selbst geprüft werden.

`temperature = 0` sorgt dafür, dass die Antworten möglichst wiederholbar sind. Modelle, die das nicht unterstützen (z. B. GPT-5), werden automatisch ohne diese Einstellung angefragt. Denkschritte von Reasoning-Modellen (`<think>…</think>`) werden vor der Prüfung entfernt.

## Grenzen

- Die Heuristiken können sich irren. E5 erkennt Unsicherheit zum Beispiel nur an typischen Formulierungen.
- Die Ergebnisse sind eine Momentaufnahme, weil Modelle sich mit Updates ändern.
- Es gibt nur wenige Prompts pro Experiment. Das ist ein Lernlabor, keine statistische Studie.

## Abgrenzung

Dieses Projekt ist ein **Lern- und Vergleichstool** für das ASC-Portfolio. Es hat keinen Bezug zu meiner Bachelorarbeit und enthält keine Klassifikationsaufgaben oder Daten daraus.

## Datenschutz

Bitte keine personenbezogenen oder vertraulichen Daten in Prompts eintragen (vgl. THKI-Nutzungshinweise).

## Quellen

- TH Köln (o. J.): *THKI Chat*. https://lehrpfade.th-koeln.de/thki-chat/
- TH Köln (o. J.): *THKI*. https://lehrpfade.th-koeln.de/thki-gpt-lab/
- Fühles-Ubach, S. (2026): *Data and AI Literacy*, Kursmaterialien Module 01–07, TH Köln.
