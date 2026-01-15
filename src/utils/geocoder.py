import requests

class Geocoder:
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': 'ProiectLogis_MapApp/1.0'
        }

    def search(self, query):
        """
        Search for a location string.
        Returns a dictionary with lat, lon, and display_name if found, else None.
        """
        params = {
            'q': query,
            'format': 'json',
            'limit': 1
        }
        
        try:
            response = requests.get(self.base_url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if data:
                return {
                    'lat': float(data[0]['lat']),
                    'lon': float(data[0]['lon']),
                    'display_name': data[0]['display_name']
                }
            return None
            
            
        except requests.RequestException as e:
            print(f"Geocoding error: {e}")
            return None

    def get_route(self, coordinates_list):
        if len(coordinates_list) < 2:
            return None
            
        coords_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates_list])
        
        url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}"
        params = {
            'overview': 'full',
            'geometries': 'geojson',
            'alternatives': 'true' # Request multiple routes
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 'Ok' and data.get('routes'):
                parsed_routes = []
                
                for route in data['routes']:
                    geometry = route['geometry']['coordinates']
                    leaflet_coords = [[coord[1], coord[0]] for coord in geometry]
                    
                    parsed_routes.append({
                        'coordinates': leaflet_coords,
                        'distance': route['distance'],
                        'duration': route['duration'],
                        'summary': route.get('weight_name', 'Route')
                    })
                
                return parsed_routes
            return None
        except requests.RequestException as e:
            print(f"Routing error: {e}")
            return None

    def get_current_location(self):
        """
        Get current location based on IP address.
        """
        try:
            response = requests.get('http://ip-api.com/json')
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'success':
                return {
                    'lat': float(data['lat']),
                    'lon': float(data['lon']),
                    'display_name': f"{data.get('city', 'Unknown')}, {data.get('country', 'Location')}"
                }
            return None
        except Exception as e:
            print(f"Location error: {e}")
            return None
