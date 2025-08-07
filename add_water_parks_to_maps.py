import geopandas as gpd
import pandas as pd
import json
import numpy as np
from shapely.geometry import Point, LineString, Polygon
import requests
import os

def fetch_osm_data(bbox, feature_type):
    """Fetch data from OpenStreetMap Overpass API"""
    
    # Define queries for different feature types
    queries = {
        'water': '''
            [out:json][timeout:25];
            (
                way["natural"="water"]({bbox});
                way["waterway"="river"]({bbox});
                way["waterway"="stream"]({bbox});
                way["waterway"="canal"]({bbox});
                relation["natural"="water"]({bbox});
                relation["waterway"="river"]({bbox});
            );
            out body;
            >;
            out skel qt;
        ''',
        'parks': '''
            [out:json][timeout:25];
            (
                way["leisure"="park"]({bbox});
                way["leisure"="recreation_ground"]({bbox});
                way["landuse"="recreation_ground"]({bbox});
                way["natural"="wood"]({bbox});
                way["natural"="forest"]({bbox});
                relation["leisure"="park"]({bbox});
                relation["landuse"="recreation_ground"]({bbox});
            );
            out body;
            >;
            out skel qt;
        ''',
        'coastline': '''
            [out:json][timeout:25];
            (
                way["natural"="coastline"]({bbox});
                relation["natural"="coastline"]({bbox});
            );
            out body;
            >;
            out skel qt;
        '''
    }
    
    if feature_type not in queries:
        return None
    
    query = queries[feature_type].format(bbox=bbox)
    url = "https://overpass-api.de/api/interpreter"
    
    try:
        response = requests.post(url, data=query)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching {feature_type}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching {feature_type}: {e}")
        return None

def get_metro_bbox(metro_name):
    """Get bounding box for metro area"""
    
    # Approximate bounding boxes for major metro areas
    bboxes = {
        "New York-Newark-Jersey City, NY-NJ-PA": "40.4,-74.3,40.9,-73.6",
        "Los Angeles-Long Beach-Anaheim, CA": "33.6,-118.7,34.3,-117.9",
        "Chicago-Naperville-Elgin, IL-IN-WI": "41.6,-88.2,42.2,-87.4",
        "Dallas-Fort Worth-Arlington, TX": "32.5,-97.4,33.2,-96.6",
        "Houston-The Woodlands-Sugar Land, TX": "29.4,-95.8,30.2,-94.9",
        "Washington-Arlington-Alexandria, DC-VA-MD-WV": "38.7,-77.3,39.1,-76.8",
        "Miami-Fort Lauderdale-West Palm Beach, FL": "25.4,-80.8,26.4,-80.0",
        "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD": "39.8,-75.4,40.2,-74.9",
        "Atlanta-Sandy Springs-Roswell, GA": "33.5,-84.8,34.2,-84.2",
        "Phoenix-Mesa-Chandler, AZ": "33.2,-112.4,33.8,-111.6",
        "Boston-Cambridge-Newton, MA-NH": "42.2,-71.3,42.5,-70.9",
        "San Francisco-Oakland-Fremont, CA": "37.6,-122.6,38.1,-122.0",
        "Riverside-San Bernardino-Ontario, CA": "33.7,-117.8,34.3,-117.0",
        "Detroit-Warren-Dearborn, MI": "42.1,-83.5,42.6,-82.8",
        "Seattle-Tacoma-Bellevue, WA": "47.4,-122.6,47.8,-122.0",
        "Minneapolis-St. Paul-Bloomington, MN-WI": "44.8,-93.6,45.2,-92.9",
        "Tampa-St. Petersburg-Clearwater, FL": "27.7,-82.8,28.2,-82.3",
        "San Diego-Chula Vista-Carlsbad, CA": "32.5,-117.4,33.2,-116.8",
        "Denver-Aurora-Centennial, CO": "39.5,-105.2,40.0,-104.6",
        "Orlando-Kissimmee-Sanford, FL": "28.2,-81.6,28.8,-80.9",
        "Charlotte-Concord-Gastonia, NC-SC": "35.0,-81.2,35.5,-80.5",
        "Baltimore-Columbia-Towson, MD": "39.1,-76.9,39.4,-76.4",
        "St. Louis, MO-IL": "38.4,-90.6,38.9,-89.9",
        "San Antonio-New Braunfels, TX": "29.2,-98.8,29.8,-98.1",
        "Austin-Round Rock-San Marcos, TX": "30.0,-98.0,30.6,-97.3",
        "Las Vegas-Henderson-North Las Vegas, NV": "36.0,-115.5,36.4,-114.8",
        "Sacramento-Roseville-Folsom, CA": "38.3,-121.8,38.8,-121.0"
    }
    
    return bboxes.get(metro_name)

def create_water_parks_geojson():
    """Create GeoJSON files with water features and parks for each metro area"""
    
    metro_areas = [
        "New York-Newark-Jersey City, NY-NJ-PA",
        "Los Angeles-Long Beach-Anaheim, CA",
        "Chicago-Naperville-Elgin, IL-IN-WI",
        "Dallas-Fort Worth-Arlington, TX",
        "Houston-The Woodlands-Sugar Land, TX",
        "Washington-Arlington-Alexandria, DC-VA-MD-WV",
        "Miami-Fort Lauderdale-West Palm Beach, FL",
        "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD",
        "Atlanta-Sandy Springs-Roswell, GA",
        "Phoenix-Mesa-Chandler, AZ",
        "Boston-Cambridge-Newton, MA-NH",
        "San Francisco-Oakland-Fremont, CA",
        "Riverside-San Bernardino-Ontario, CA",
        "Detroit-Warren-Dearborn, MI",
        "Seattle-Tacoma-Bellevue, WA",
        "Minneapolis-St. Paul-Bloomington, MN-WI",
        "Tampa-St. Petersburg-Clearwater, FL",
        "San Diego-Chula Vista-Carlsbad, CA",
        "Denver-Aurora-Centennial, CO",
        "Orlando-Kissimmee-Sanford, FL",
        "Charlotte-Concord-Gastonia, NC-SC",
        "Baltimore-Columbia-Towson, MD",
        "St. Louis, MO-IL",
        "San Antonio-New Braunfels, TX",
        "Austin-Round Rock-San Marcos, TX",
        "Las Vegas-Henderson-North Las Vegas, NV",
        "Sacramento-Roseville-Folsom, CA"
    ]
    
    for metro_name in metro_areas:
        print(f"Processing {metro_name}...")
        
        bbox = get_metro_bbox(metro_name)
        if not bbox:
            print(f"  No bbox found for {metro_name}")
            continue
        
        # Fetch water features
        water_data = fetch_osm_data(bbox, 'water')
        parks_data = fetch_osm_data(bbox, 'parks')
        coastline_data = fetch_osm_data(bbox, 'coastline')
        
        # Create features list
        features = []
        
        # Add water features
        if water_data:
            print(f"  Found {len(water_data.get('elements', []))} water features")
            for element in water_data.get('elements', []):
                if element['type'] == 'way':
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": []  # Would need to resolve coordinates
                        },
                        "properties": {
                            "name": element.get('tags', {}).get('name', 'Water'),
                            "type": "water",
                            "water_type": element.get('tags', {}).get('waterway', 'water')
                        }
                    }
                    features.append(feature)
        
        # Add parks
        if parks_data:
            print(f"  Found {len(parks_data.get('elements', []))} park features")
            for element in parks_data.get('elements', []):
                if element['type'] == 'way':
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": []  # Would need to resolve coordinates
                        },
                        "properties": {
                            "name": element.get('tags', {}).get('name', 'Park'),
                            "type": "park",
                            "park_type": element.get('tags', {}).get('leisure', 'park')
                        }
                    }
                    features.append(feature)
        
        # Add coastline
        if coastline_data:
            print(f"  Found {len(coastline_data.get('elements', []))} coastline features")
            for element in coastline_data.get('elements', []):
                if element['type'] == 'way':
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": []  # Would need to resolve coordinates
                        },
                        "properties": {
                            "name": "Coastline",
                            "type": "coastline"
                        }
                    }
                    features.append(feature)
        
        # Create GeoJSON structure
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        # Save to file
        safe_name = metro_name.replace('/', '-').replace(',', '').replace(' ', '_')
        filename = f'water_parks_{safe_name}.geojson'
        
        with open(filename, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        print(f"  Saved {len(features)} features to {filename}")

def create_synthetic_water_parks():
    """Create synthetic water and park features for demonstration"""
    
    metro_areas = [
        "New York-Newark-Jersey City, NY-NJ-PA",
        "Los Angeles-Long Beach-Anaheim, CA",
        "Chicago-Naperville-Elgin, IL-IN-WI",
        "Dallas-Fort Worth-Arlington, TX",
        "Houston-The Woodlands-Sugar Land, TX",
        "Washington-Arlington-Alexandria, DC-VA-MD-WV",
        "Miami-Fort Lauderdale-West Palm Beach, FL",
        "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD",
        "Atlanta-Sandy Springs-Roswell, GA",
        "Phoenix-Mesa-Chandler, AZ",
        "Boston-Cambridge-Newton, MA-NH",
        "San Francisco-Oakland-Fremont, CA",
        "Riverside-San Bernardino-Ontario, CA",
        "Detroit-Warren-Dearborn, MI",
        "Seattle-Tacoma-Bellevue, WA",
        "Minneapolis-St. Paul-Bloomington, MN-WI",
        "Tampa-St. Petersburg-Clearwater, FL",
        "San Diego-Chula Vista-Carlsbad, CA",
        "Denver-Aurora-Centennial, CO",
        "Orlando-Kissimmee-Sanford, FL",
        "Charlotte-Concord-Gastonia, NC-SC",
        "Baltimore-Columbia-Towson, MD",
        "St. Louis, MO-IL",
        "San Antonio-New Braunfels, TX",
        "Austin-Round Rock-San Marcos, TX",
        "Las Vegas-Henderson-North Las Vegas, NV",
        "Sacramento-Roseville-Folsom, CA"
    ]
    
    # Synthetic water and park features for each metro area
    metro_features = {
        "New York-Newark-Jersey City, NY-NJ-PA": [
            {"name": "Hudson River", "type": "river", "coords": [[-74.05, 40.75], [-74.02, 40.72], [-73.98, 40.70]]},
            {"name": "East River", "type": "river", "coords": [[-73.95, 40.75], [-73.92, 40.72], [-73.88, 40.70]]},
            {"name": "Central Park", "type": "park", "coords": [[-73.97, 40.78], [-73.95, 40.78], [-73.95, 40.76], [-73.97, 40.76]]},
            {"name": "Prospect Park", "type": "park", "coords": [[-73.97, 40.66], [-73.95, 40.66], [-73.95, 40.64], [-73.97, 40.64]]}
        ],
        "Los Angeles-Long Beach-Anaheim, CA": [
            {"name": "Pacific Ocean", "type": "coastline", "coords": [[-118.5, 33.7], [-118.4, 33.8], [-118.3, 33.9]]},
            {"name": "Los Angeles River", "type": "river", "coords": [[-118.2, 34.1], [-118.3, 34.0], [-118.4, 33.9]]},
            {"name": "Griffith Park", "type": "park", "coords": [[-118.3, 34.15], [-118.28, 34.15], [-118.28, 34.13], [-118.3, 34.13]]},
            {"name": "Echo Park", "type": "park", "coords": [[-118.26, 34.08], [-118.24, 34.08], [-118.24, 34.06], [-118.26, 34.06]]}
        ],
        "Chicago-Naperville-Elgin, IL-IN-WI": [
            {"name": "Lake Michigan", "type": "lake", "coords": [[-87.6, 41.9], [-87.5, 42.0], [-87.4, 42.1]]},
            {"name": "Chicago River", "type": "river", "coords": [[-87.65, 41.9], [-87.63, 41.88], [-87.61, 41.86]]},
            {"name": "Millennium Park", "type": "park", "coords": [[-87.62, 41.88], [-87.60, 41.88], [-87.60, 41.86], [-87.62, 41.86]]},
            {"name": "Grant Park", "type": "park", "coords": [[-87.62, 41.87], [-87.60, 41.87], [-87.60, 41.85], [-87.62, 41.85]]}
        ],
        "Dallas-Fort Worth-Arlington, TX": [
            {"name": "Trinity River", "type": "river", "coords": [[-96.8, 32.8], [-96.7, 32.7], [-96.6, 32.6]]},
            {"name": "White Rock Lake", "type": "lake", "coords": [[-96.72, 32.85], [-96.70, 32.85], [-96.70, 32.83], [-96.72, 32.83]]},
            {"name": "Klyde Warren Park", "type": "park", "coords": [[-96.80, 32.78], [-96.78, 32.78], [-96.78, 32.76], [-96.80, 32.76]]}
        ],
        "Houston-The Woodlands-Sugar Land, TX": [
            {"name": "Buffalo Bayou", "type": "river", "coords": [[-95.4, 29.8], [-95.3, 29.7], [-95.2, 29.6]]},
            {"name": "Hermann Park", "type": "park", "coords": [[-95.40, 29.72], [-95.38, 29.72], [-95.38, 29.70], [-95.40, 29.70]]},
            {"name": "Discovery Green", "type": "park", "coords": [[-95.36, 29.76], [-95.34, 29.76], [-95.34, 29.74], [-95.36, 29.74]]}
        ],
        "Washington-Arlington-Alexandria, DC-VA-MD-WV": [
            {"name": "Potomac River", "type": "river", "coords": [[-77.1, 38.9], [-77.0, 38.8], [-76.9, 38.7]]},
            {"name": "National Mall", "type": "park", "coords": [[-77.02, 38.89], [-77.00, 38.89], [-77.00, 38.87], [-77.02, 38.87]]},
            {"name": "Rock Creek Park", "type": "park", "coords": [[-77.05, 38.92], [-77.03, 38.92], [-77.03, 38.90], [-77.05, 38.90]]}
        ],
        "Miami-Fort Lauderdale-West Palm Beach, FL": [
            {"name": "Atlantic Ocean", "type": "coastline", "coords": [[-80.2, 25.8], [-80.1, 25.9], [-80.0, 26.0]]},
            {"name": "Biscayne Bay", "type": "bay", "coords": [[-80.15, 25.75], [-80.13, 25.75], [-80.13, 25.73], [-80.15, 25.73]]},
            {"name": "Bayfront Park", "type": "park", "coords": [[-80.19, 25.77], [-80.17, 25.77], [-80.17, 25.75], [-80.19, 25.75]]}
        ]
    }
    
    for metro_name in metro_areas:
        print(f"Processing {metro_name}...")
        
        features = []
        
        if metro_name in metro_features:
            for feature in metro_features[metro_name]:
                if feature["type"] in ["river", "lake", "bay"]:
                    geom_type = "LineString" if feature["type"] == "river" else "Polygon"
                    coords = feature["coords"]
                    if geom_type == "Polygon":
                        coords = [coords]  # Wrap in array for polygon
                    
                    feature_geojson = {
                        "type": "Feature",
                        "geometry": {
                            "type": geom_type,
                            "coordinates": coords
                        },
                        "properties": {
                            "name": feature["name"],
                            "type": "water",
                            "water_type": feature["type"]
                        }
                    }
                    features.append(feature_geojson)
                
                elif feature["type"] == "park":
                    feature_geojson = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [feature["coords"]]
                        },
                        "properties": {
                            "name": feature["name"],
                            "type": "park"
                        }
                    }
                    features.append(feature_geojson)
                
                elif feature["type"] == "coastline":
                    feature_geojson = {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": feature["coords"]
                        },
                        "properties": {
                            "name": feature["name"],
                            "type": "coastline"
                        }
                    }
                    features.append(feature_geojson)
        
        # Create GeoJSON structure
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        # Save to file
        safe_name = metro_name.replace('/', '-').replace(',', '').replace(' ', '_')
        filename = f'water_parks_{safe_name}.geojson'
        
        with open(filename, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        print(f"  Saved {len(features)} features to {filename}")

if __name__ == "__main__":
    print("Creating synthetic water and park features...")
    create_synthetic_water_parks()
    print("Water and park GeoJSON files created!") 