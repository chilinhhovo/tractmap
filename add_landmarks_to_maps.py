import geopandas as gpd
import pandas as pd
import json
import numpy as np
from shapely.geometry import Point

# Landmark data with approximate coordinates
metro_landmarks = {
    "New York-Newark-Jersey City, NY-NJ-PA": [
        {"name": "Manhattan", "lat": 40.7589, "lon": -73.9851},
        {"name": "Brooklyn", "lat": 40.6782, "lon": -73.9442},
        {"name": "Queens", "lat": 40.7282, "lon": -73.7949},
        {"name": "The Bronx", "lat": 40.8448, "lon": -73.8648},
        {"name": "Staten Island", "lat": 40.5795, "lon": -74.1502},
        {"name": "Statue of Liberty", "lat": 40.6892, "lon": -74.0445},
        {"name": "Empire State Building", "lat": 40.7484, "lon": -73.9857},
        {"name": "Central Park", "lat": 40.7829, "lon": -73.9654},
        {"name": "Times Square", "lat": 40.7580, "lon": -73.9855},
        {"name": "Brooklyn Bridge", "lat": 40.7061, "lon": -73.9969},
        {"name": "One World Trade Center", "lat": 40.7127, "lon": -74.0134},
        {"name": "Wall Street", "lat": 40.7075, "lon": -74.0109},
        {"name": "Harlem", "lat": 40.8116, "lon": -73.9465},
        {"name": "Yankee Stadium", "lat": 40.8296, "lon": -73.9262}
    ],
    "Los Angeles-Long Beach-Anaheim, CA": [
        {"name": "Hollywood", "lat": 34.0928, "lon": -118.3287},
        {"name": "Santa Monica", "lat": 34.0195, "lon": -118.4912},
        {"name": "Beverly Hills", "lat": 34.0736, "lon": -118.4004},
        {"name": "Downtown LA", "lat": 34.0522, "lon": -118.2437},
        {"name": "Venice Beach", "lat": 33.9850, "lon": -118.4695},
        {"name": "Hollywood Sign", "lat": 34.1341, "lon": -118.3216},
        {"name": "Griffith Observatory", "lat": 34.1184, "lon": -118.3004},
        {"name": "Santa Monica Pier", "lat": 34.0083, "lon": -118.5000},
        {"name": "Walk of Fame", "lat": 34.1016, "lon": -118.3265},
        {"name": "Getty Center", "lat": 34.0781, "lon": -118.4743},
        {"name": "Venice Boardwalk", "lat": 33.9850, "lon": -118.4695}
    ],
    "Chicago-Naperville-Elgin, IL-IN-WI": [
        {"name": "The Loop", "lat": 41.8781, "lon": -87.6298},
        {"name": "Gold Coast", "lat": 41.9097, "lon": -87.6298},
        {"name": "Bronzeville", "lat": 41.8167, "lon": -87.6167},
        {"name": "Lincoln Park", "lat": 41.9217, "lon": -87.6339},
        {"name": "Hyde Park", "lat": 41.7947, "lon": -87.5867},
        {"name": "Old Town", "lat": 41.9100, "lon": -87.6300},
        {"name": "Willis Tower", "lat": 41.8789, "lon": -87.6359},
        {"name": "Millennium Park", "lat": 41.8825, "lon": -87.6225},
        {"name": "Cloud Gate", "lat": 41.8825, "lon": -87.6225},
        {"name": "Navy Pier", "lat": 41.8917, "lon": -87.6025},
        {"name": "Wrigley Field", "lat": 41.9484, "lon": -87.6553},
        {"name": "Magnificent Mile", "lat": 41.8975, "lon": -87.6250}
    ],
    "Dallas-Fort Worth-Arlington, TX": [
        {"name": "Downtown Dallas", "lat": 32.7767, "lon": -96.7970},
        {"name": "Uptown", "lat": 32.7875, "lon": -96.8000},
        {"name": "Bishop Arts", "lat": 32.7500, "lon": -96.8167},
        {"name": "Stockyards", "lat": 32.7883, "lon": -97.3525},
        {"name": "Sundance Square", "lat": 32.7553, "lon": -97.3306},
        {"name": "Dealey Plaza", "lat": 32.7786, "lon": -96.8083},
        {"name": "Reunion Tower", "lat": 32.7750, "lon": -96.8000},
        {"name": "AT&T Stadium", "lat": 32.7473, "lon": -97.0944},
        {"name": "Dallas Arboretum", "lat": 32.8233, "lon": -96.7167},
        {"name": "Fort Worth Stockyards", "lat": 32.7883, "lon": -97.3525}
    ],
    "Houston-The Woodlands-Sugar Land, TX": [
        {"name": "Downtown", "lat": 29.7604, "lon": -95.3698},
        {"name": "Montrose", "lat": 29.7400, "lon": -95.3900},
        {"name": "The Heights", "lat": 29.8000, "lon": -95.4000},
        {"name": "Museum District", "lat": 29.7200, "lon": -95.3900},
        {"name": "River Oaks", "lat": 29.7500, "lon": -95.4200},
        {"name": "Space Center Houston", "lat": 29.5522, "lon": -95.0972},
        {"name": "San Jacinto Monument", "lat": 29.7494, "lon": -95.0806},
        {"name": "Discovery Green", "lat": 29.7550, "lon": -95.3600},
        {"name": "Sam Houston Park", "lat": 29.7600, "lon": -95.3700}
    ],
    "Miami-Fort Lauderdale-West Palm Beach, FL": [
        {"name": "South Beach", "lat": 25.7617, "lon": -80.1918},
        {"name": "Coconut Grove", "lat": 25.7280, "lon": -80.2430},
        {"name": "Coral Gables", "lat": 25.7215, "lon": -80.2684},
        {"name": "Little Havana", "lat": 25.7617, "lon": -80.1918},
        {"name": "Wynwood", "lat": 25.8000, "lon": -80.2000},
        {"name": "Downtown", "lat": 25.7617, "lon": -80.1918},
        {"name": "Ocean Drive", "lat": 25.7617, "lon": -80.1918},
        {"name": "Art Deco District", "lat": 25.7860, "lon": -80.1300},
        {"name": "Wynwood Walls", "lat": 25.8000, "lon": -80.2000},
        {"name": "Vizcaya Gardens", "lat": 25.7490, "lon": -80.2100}
    ],
    "Atlanta-Sandy Springs-Roswell, GA": [
        {"name": "Midtown", "lat": 33.7840, "lon": -84.3720},
        {"name": "Buckhead", "lat": 33.8470, "lon": -84.3780},
        {"name": "Sweet Auburn", "lat": 33.7550, "lon": -84.3700},
        {"name": "Old Fourth Ward", "lat": 33.7600, "lon": -84.3600},
        {"name": "Little Five Points", "lat": 33.7700, "lon": -84.3500},
        {"name": "Centennial Olympic Park", "lat": 33.7630, "lon": -84.3930},
        {"name": "MLK Jr. National Historical Park", "lat": 33.7550, "lon": -84.3700},
        {"name": "Fox Theatre", "lat": 33.7720, "lon": -84.3850},
        {"name": "Georgia Aquarium", "lat": 33.7630, "lon": -84.3950}
    ],
    "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD": [
        {"name": "Old City", "lat": 39.9526, "lon": -75.1452},
        {"name": "Rittenhouse Square", "lat": 39.9490, "lon": -75.1720},
        {"name": "Society Hill", "lat": 39.9450, "lon": -75.1500},
        {"name": "Fishtown", "lat": 39.9700, "lon": -75.1300},
        {"name": "Northern Liberties", "lat": 39.9650, "lon": -75.1400},
        {"name": "Liberty Bell", "lat": 39.9490, "lon": -75.1500},
        {"name": "Independence Hall", "lat": 39.9489, "lon": -75.1500},
        {"name": "Rocky Steps", "lat": 39.9650, "lon": -75.1800},
        {"name": "Reading Terminal Market", "lat": 39.9540, "lon": -75.1600}
    ],
    "Washington-Arlington-Alexandria, DC-VA-MD-WV": [
        {"name": "Capitol Hill", "lat": 38.8899, "lon": -77.0090},
        {"name": "Georgetown", "lat": 38.9090, "lon": -77.0630},
        {"name": "National Mall", "lat": 38.8899, "lon": -77.0090},
        {"name": "Adams Morgan", "lat": 38.9200, "lon": -77.0400},
        {"name": "Dupont Circle", "lat": 38.9100, "lon": -77.0400},
        {"name": "Capitol", "lat": 38.8899, "lon": -77.0090},
        {"name": "White House", "lat": 38.8977, "lon": -77.0365},
        {"name": "Lincoln Memorial", "lat": 38.8893, "lon": -77.0502},
        {"name": "Smithsonian Museums", "lat": 38.8899, "lon": -77.0090}
    ],
    "Phoenix-Mesa-Chandler, AZ": [
        {"name": "Downtown", "lat": 33.4484, "lon": -112.0740},
        {"name": "Arcadia", "lat": 33.4800, "lon": -111.9800},
        {"name": "Roosevelt Row", "lat": 33.4500, "lon": -112.0700},
        {"name": "Scottsdale", "lat": 33.4942, "lon": -111.9261},
        {"name": "Tempe", "lat": 33.4255, "lon": -111.9400},
        {"name": "Glendale", "lat": 33.5387, "lon": -112.1860},
        {"name": "Camelback Mountain", "lat": 33.5200, "lon": -112.0200},
        {"name": "Desert Botanical Garden", "lat": 33.4600, "lon": -111.9400},
        {"name": "Heard Museum", "lat": 33.4600, "lon": -112.0700}
    ],
    "Boston-Cambridge-Newton, MA-NH": [
        {"name": "Back Bay", "lat": 42.3500, "lon": -71.0800},
        {"name": "Beacon Hill", "lat": 42.3580, "lon": -71.0700},
        {"name": "North End", "lat": 42.3650, "lon": -71.0550},
        {"name": "South Boston", "lat": 42.3400, "lon": -71.0500},
        {"name": "Cambridge", "lat": 42.3736, "lon": -71.1097},
        {"name": "Fenway Park", "lat": 42.3467, "lon": -71.0972},
        {"name": "Freedom Trail", "lat": 42.3600, "lon": -71.0600},
        {"name": "Quincy Market", "lat": 42.3600, "lon": -71.0550},
        {"name": "Boston Common", "lat": 42.3550, "lon": -71.0650}
    ],
    "Seattle-Tacoma-Bellevue, WA": [
        {"name": "Downtown", "lat": 47.6062, "lon": -122.3321},
        {"name": "Capitol Hill", "lat": 47.6200, "lon": -122.3200},
        {"name": "Ballard", "lat": 47.6800, "lon": -122.3800},
        {"name": "Fremont", "lat": 47.6500, "lon": -122.3500},
        {"name": "Queen Anne", "lat": 47.6200, "lon": -122.3600},
        {"name": "Space Needle", "lat": 47.6205, "lon": -122.3493},
        {"name": "Pike Place Market", "lat": 47.6096, "lon": -122.3420},
        {"name": "Seattle Waterfront", "lat": 47.6100, "lon": -122.3400}
    ],
    "Detroit-Warren-Dearborn, MI": [
        {"name": "Downtown", "lat": 42.3314, "lon": -83.0458},
        {"name": "Midtown", "lat": 42.3500, "lon": -83.0600},
        {"name": "Greektown", "lat": 42.3350, "lon": -83.0400},
        {"name": "Corktown", "lat": 42.3300, "lon": -83.0700},
        {"name": "Renaissance Center", "lat": 42.3290, "lon": -83.0400},
        {"name": "Motown Museum", "lat": 42.3500, "lon": -83.0900},
        {"name": "Belle Isle", "lat": 42.3500, "lon": -82.9800}
    ],
    "San Diego-Chula Vista-Carlsbad, CA": [
        {"name": "Gaslamp Quarter", "lat": 32.7157, "lon": -117.1611},
        {"name": "La Jolla", "lat": 32.8328, "lon": -117.2713},
        {"name": "Old Town", "lat": 32.7540, "lon": -117.1300},
        {"name": "Coronado", "lat": 32.6859, "lon": -117.1831},
        {"name": "Little Italy", "lat": 32.7200, "lon": -117.1700},
        {"name": "Balboa Park", "lat": 32.7320, "lon": -117.1500},
        {"name": "San Diego Zoo", "lat": 32.7353, "lon": -117.1490},
        {"name": "USS Midway", "lat": 32.7140, "lon": -117.1750}
    ],
    "San Francisco-Oakland-Fremont, CA": [
        {"name": "The Mission", "lat": 37.7599, "lon": -122.4148},
        {"name": "Chinatown", "lat": 37.7941, "lon": -122.4078},
        {"name": "Haight-Ashbury", "lat": 37.7700, "lon": -122.4500},
        {"name": "Nob Hill", "lat": 37.7900, "lon": -122.4100},
        {"name": "North Beach", "lat": 37.8000, "lon": -122.4100},
        {"name": "Golden Gate Bridge", "lat": 37.8199, "lon": -122.4783},
        {"name": "Alcatraz", "lat": 37.8270, "lon": -122.4230},
        {"name": "Fisherman's Wharf", "lat": 37.8080, "lon": -122.4100}
    ],
    "Tampa-St. Petersburg-Clearwater, FL": [
        {"name": "Ybor City", "lat": 27.9680, "lon": -82.4400},
        {"name": "Downtown", "lat": 27.9506, "lon": -82.4572},
        {"name": "Hyde Park", "lat": 27.9400, "lon": -82.4700},
        {"name": "Channelside", "lat": 27.9400, "lon": -82.4500},
        {"name": "Tampa Riverwalk", "lat": 27.9500, "lon": -82.4600},
        {"name": "Bayshore Boulevard", "lat": 27.9400, "lon": -82.4700},
        {"name": "Amalie Arena", "lat": 27.9430, "lon": -82.4500}
    ],
    "Minneapolis-St. Paul-Bloomington, MN-WI": [
        {"name": "Downtown", "lat": 44.9778, "lon": -93.2650},
        {"name": "Uptown", "lat": 44.9500, "lon": -93.3000},
        {"name": "Northeast", "lat": 45.0000, "lon": -93.2500},
        {"name": "Dinkytown", "lat": 44.9800, "lon": -93.2300},
        {"name": "North Loop", "lat": 44.9800, "lon": -93.2800},
        {"name": "Stone Arch Bridge", "lat": 44.9800, "lon": -93.2500},
        {"name": "Minneapolis Sculpture Garden", "lat": 44.9700, "lon": -93.2900}
    ],
    "Las Vegas-Henderson-North Las Vegas, NV": [
        {"name": "The Strip", "lat": 36.1699, "lon": -115.1398},
        {"name": "Downtown", "lat": 36.1699, "lon": -115.1398},
        {"name": "Fremont East", "lat": 36.1700, "lon": -115.1400},
        {"name": "Summerlin", "lat": 36.1500, "lon": -115.3300},
        {"name": "Welcome to Las Vegas sign", "lat": 36.1147, "lon": -115.1728},
        {"name": "The Strip casinos", "lat": 36.1699, "lon": -115.1398},
        {"name": "Fremont Street Experience", "lat": 36.1700, "lon": -115.1400}
    ],
    "Denver-Aurora-Centennial, CO": [
        {"name": "LoDo", "lat": 39.7392, "lon": -104.9903},
        {"name": "Capitol Hill", "lat": 39.7400, "lon": -104.9800},
        {"name": "Highlands", "lat": 39.7600, "lon": -105.0200},
        {"name": "Cherry Creek", "lat": 39.7200, "lon": -104.9500},
        {"name": "Union Station", "lat": 39.7530, "lon": -105.0000},
        {"name": "Red Rocks Amphitheatre", "lat": 39.6650, "lon": -105.2050},
        {"name": "Civic Center", "lat": 39.7400, "lon": -104.9900}
    ],
    "Riverside-San Bernardino-Ontario, CA": [
        {"name": "Riverside", "lat": 33.9533, "lon": -117.3962},
        {"name": "San Bernardino", "lat": 34.1083, "lon": -117.2898},
        {"name": "Redlands", "lat": 34.0556, "lon": -117.1825},
        {"name": "Ontario", "lat": 34.0633, "lon": -117.6509},
        {"name": "Mission Inn", "lat": 33.9533, "lon": -117.3962},
        {"name": "San Bernardino National Forest", "lat": 34.1083, "lon": -117.2898}
    ],
    "San Antonio-New Braunfels, TX": [
        {"name": "Downtown", "lat": 29.4241, "lon": -98.4936},
        {"name": "King William", "lat": 29.4200, "lon": -98.4900},
        {"name": "Pearl District", "lat": 29.4500, "lon": -98.4800},
        {"name": "Alamo Heights", "lat": 29.4600, "lon": -98.4700},
        {"name": "The Alamo", "lat": 29.4259, "lon": -98.4861},
        {"name": "San Antonio River Walk", "lat": 29.4241, "lon": -98.4936},
        {"name": "Mission San Jose", "lat": 29.3619, "lon": -98.4783}
    ],
    "Baltimore-Columbia-Towson, MD": [
        {"name": "Inner Harbor", "lat": 39.2904, "lon": -76.6122},
        {"name": "Fells Point", "lat": 39.2800, "lon": -76.5900},
        {"name": "Mount Vernon", "lat": 39.3000, "lon": -76.6200},
        {"name": "Federal Hill", "lat": 39.2700, "lon": -76.6100},
        {"name": "Fort McHenry", "lat": 39.2630, "lon": -76.5800},
        {"name": "National Aquarium", "lat": 39.2850, "lon": -76.6100},
        {"name": "Camden Yards", "lat": 39.2830, "lon": -76.6200}
    ],
    "Charlotte-Concord-Gastonia, NC-SC": [
        {"name": "Uptown", "lat": 35.2271, "lon": -80.8431},
        {"name": "NoDa", "lat": 35.2400, "lon": -80.8200},
        {"name": "South End", "lat": 35.2100, "lon": -80.8500},
        {"name": "Plaza Midwood", "lat": 35.2200, "lon": -80.8300},
        {"name": "Bank of America Stadium", "lat": 35.2250, "lon": -80.8500},
        {"name": "NASCAR Hall of Fame", "lat": 35.2250, "lon": -80.8500}
    ],
    "Austin-Round Rock-San Marcos, TX": [
        {"name": "Downtown", "lat": 30.2672, "lon": -97.7431},
        {"name": "South Congress", "lat": 30.2500, "lon": -97.7500},
        {"name": "East Austin", "lat": 30.2700, "lon": -97.7200},
        {"name": "Hyde Park", "lat": 30.3000, "lon": -97.7300},
        {"name": "Zilker", "lat": 30.2700, "lon": -97.7700},
        {"name": "Texas State Capitol", "lat": 30.2747, "lon": -97.7404},
        {"name": "Congress Avenue Bridge", "lat": 30.2650, "lon": -97.7450},
        {"name": "Barton Springs", "lat": 30.2640, "lon": -97.7700}
    ],
    "Sacramento-Roseville-Folsom, CA": [
        {"name": "Midtown", "lat": 38.5816, "lon": -121.4944},
        {"name": "Downtown", "lat": 38.5816, "lon": -121.4944},
        {"name": "East Sacramento", "lat": 38.5800, "lon": -121.4700},
        {"name": "Land Park", "lat": 38.5600, "lon": -121.4900},
        {"name": "State Capitol", "lat": 38.5767, "lon": -121.4933},
        {"name": "Old Sacramento", "lat": 38.5816, "lon": -121.4944},
        {"name": "Tower Bridge", "lat": 38.5800, "lon": -121.5100}
    ]
}

def create_landmarks_geojson():
    """Create GeoJSON files with landmark points for each metro area"""
    
    for metro_name, landmarks in metro_landmarks.items():
        print(f"Processing landmarks for {metro_name}...")
        
        # Create landmark features
        features = []
        for landmark in landmarks:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [landmark["lon"], landmark["lat"]]
                },
                "properties": {
                    "name": landmark["name"],
                    "type": "landmark"
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
        filename = f'landmarks_{safe_name}.geojson'
        
        with open(filename, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        print(f"  Saved {len(landmarks)} landmarks to {filename}")

if __name__ == "__main__":
    create_landmarks_geojson()
    print("Landmark GeoJSON files created!") 