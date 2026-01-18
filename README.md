# CheapMaps

CheapMaps is a modern desktop navigation application built with Python (PyQt5) and Leaflet.js. It provides a sleek, dark-themed interface for route planning and location services, utilizing open-source data.

## Features

- **Interactive Mapping**: seamless navigation using OpenStreetMap data with multiple layer options (Dark, Light, Satellite, Terrain).
- **Location Search**: Quick search functionality for cities, streets, and points of interest.
- **Route Planning**: Optimized driving routes with support for multiple waypoints and drag-and-drop reordering.
- **Rocket Route**: Automatic calculation of the fastest route with distance and duration estimates.
- **Weather Integration**: Real-time weather updates and 7-day detailed forecasts for any selected location.
- **Geolocation**: Automatic detection of the current user location via IP-based services.

## Technology Stack

- **Language**: Python 3
- **GUI Framework**: PyQt5 / PyQtWebEngine
- **Maps**: Leaflet.js
- **Services**:
  - Geocoding: OpenStreetMap Nominatim
  - Routing: OSRM (Open Source Routing Machine)
  - Weather: Open-Meteo API
  - Geolocation: ip-api

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/username/CheapMaps.git
    cd CheapMaps
    ```

2.  Create a virtual environment (Recommended):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Launch the application by running the main entry point:

```bash
python src/main.py
```

## Project Structure

- `src/main.py`: Application entry point.
- `src/map_app.html`: Leaflet map interface and JavaScript logic.
- `src/ui/`: User Interface components (Main Window, Weather Widget, Panels).
- `src/utils/`: Utility modules for Geocoding and Weather services.

## Note

This application utilizes public APIs which may have usage limits. For high-volume usage, consider hosting self-hosted instances of OSRM and Nominatim.
