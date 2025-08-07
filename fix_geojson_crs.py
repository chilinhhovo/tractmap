import geopandas as gpd
import json
import os

def fix_geojson_crs():
    """Fix CRS of existing GeoJSON files"""
    
    # Find all metro tract GeoJSON files
    geojson_files = [f for f in os.listdir('.') if f.startswith('metro_tracts_') and f.endswith('.geojson')]
    
    print(f"Found {len(geojson_files)} GeoJSON files to fix")
    
    for filename in geojson_files:
        print(f"Processing {filename}...")
        
        try:
            # Load the GeoJSON
            gdf = gpd.read_file(filename)
            
            # Set CRS to WGS84 if not already set
            if gdf.crs is None:
                gdf.set_crs('EPSG:4326', inplace=True)
                print(f"  Set CRS to EPSG:4326 for {filename}")
            else:
                print(f"  CRS already set: {gdf.crs} for {filename}")
            
            # Save back to file
            gdf.to_file(filename, driver='GeoJSON')
            print(f"  Saved {filename}")
            
        except Exception as e:
            print(f"  Error processing {filename}: {e}")
    
    print("CRS fix complete!")

if __name__ == "__main__":
    fix_geojson_crs() 