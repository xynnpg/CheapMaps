# CheapMaps 🌑

CheapMaps este o aplicație desktop modernă de hărți și navigare, construită cu **Python (PyQt5)** și **Leaflet.js**. Oferă o interfață elegantă "Dark Mode" și funcționalități esențiale pentru planificarea rutelor gratuit, folosind servicii open-source.

## 🚀 Funcționalități

- **Hărți Interactive**: Navigare fluidă folosind hărți OpenStreetMap cu o temă întunecată (CartoDB Dark Matter).
- **Căutare Locații**: Găsește rapid orașe, străzi și puncte de interes (folosind Nominatim).
- **Planificare Rute**:
  - Rută auto optimizată între mai multe puncte (OSRM).
  - Suport pentru **Waypoints** (opriri intermediare).
  - Reordonare ușoară a opririlor prin drag-and-drop (săgeți sus/jos).
  - Afișare rute alternative.
- **Rute "Rocket"**: Calcularea automată a celei mai rapide rute, afișând durata estimată și distanța.
- **Locația Mea**: Detectare automată a locației aproximative pe bază de IP.
- **Selectare de pe Hartă**: Click dreapta (sau buton dedicat) pentru a alege puncte direct de pe hartă.
- **Interfață Modernă**: Design minimalist, dark-mode, cu elemente suprapuse elegant.

## 🛠️ Tehnologii Folosite

- **Limbaj**: Python 3
- **GUI Framework**: PyQt5 / PyQtWebEngine
- **Hărți Web**: Leaflet.js
- **Servicii API (Gratuite)**:
  - *Geocoding*: OpenStreetMap Nominatim
  - *Routing*: OSRM (Open Source Routing Machine)
  - *IP Geolocation*: ip-api.com

## 📦 Instalare

1.  **Clonează repository-ul:**
    ```bash
    git clone https://github.com/username/CheapMaps.git
    cd CheapMaps
    ```

2.  **Creează un mediu virtual (recomandat):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Instalează dependențele:**
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Utilizare

Pornește aplicația rulând:

```bash
python src/main.py
```

## 📝 Structură Proiect

- `src/main.py`: Punctul de intrare în aplicație.
- `src/map_app.html`: Interfața hărții (Leaflet).
- `src/ui/`: Componentele interfeței grafice (Fereastra principală, Panou direcții).
- `src/utils/`: Utilitare pentru Geocoding și completare automată.

## ⚠️ Notă

Această aplicație folosește API-uri publice care pot avea limite de utilizare. Pentru utilizare intensivă, luați în considerare configurarea propriilor servere OSRM/Nominatim.
