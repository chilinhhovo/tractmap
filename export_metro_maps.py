import os
import json
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

# Create metro-areas folder
os.makedirs('metro-areas', exist_ok=True)

# Metro areas with their codes and names
metro_areas = {
    "35620": "New York-Newark-Jersey City, NY-NJ-PA",
    "31080": "Los Angeles-Long Beach-Anaheim, CA", 
    "16980": "Chicago-Naperville-Elgin, IL-IN-WI",
    "19100": "Dallas-Fort Worth-Arlington, TX",
    "26420": "Houston-The Woodlands-Sugar Land, TX",
    "47900": "Washington-Arlington-Alexandria, DC-VA-MD-WV",
    "33100": "Miami-Fort Lauderdale-West Palm Beach, FL",
    "37980": "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD",
    "12060": "Atlanta-Sandy Springs-Roswell, GA",
    "38060": "Phoenix-Mesa-Chandler, AZ",
    "14460": "Boston-Cambridge-Newton, MA-NH",
    "41860": "San Francisco-Oakland-Fremont, CA",
    "40140": "Riverside-San Bernardino-Ontario, CA",
    "19820": "Detroit-Warren-Dearborn, MI",
    "42660": "Seattle-Tacoma-Bellevue, WA",
    "33460": "Minneapolis-St. Paul-Bloomington, MN-WI",
    "45300": "Tampa-St. Petersburg-Clearwater, FL",
    "41740": "San Diego-Chula Vista-Carlsbad, CA",
    "19740": "Denver-Aurora-Centennial, CO",
    "36740": "Orlando-Kissimmee-Sanford, FL",
    "16740": "Charlotte-Concord-Gastonia, NC-SC",
    "12580": "Baltimore-Columbia-Towson, MD",
    "41180": "St. Louis, MO-IL",
    "41700": "San Antonio-New Braunfels, TX",
    "12420": "Austin-Round Rock-San Marcos, TX",
    "29820": "Las Vegas-Henderson-North Las Vegas, NV",
    "40900": "Sacramento-Roseville-Folsom, CA"
}

def get_gap_color(gap, white_total, black_total):
    """Get color based on gap and application count - Orange for gaps, Blue for no gap/positive"""
    if white_total + black_total < 5:
        return '#cccccc'  # Grey for insufficient data
    
    if gap < 0:
        return '#4A90E2'  # Blue for positive (no gap)
    elif gap < 0.05:
        return '#FFE5CC'  # Light orange for low gap
    elif gap < 0.10:
        return '#FFB366'  # Medium orange for medium gap
    elif gap < 0.15:
        return '#FF8000'  # Dark orange for high gap
    else:
        return '#CC6600'  # Very dark orange for very high gap

def create_metro_map(geojson_file, metro_name, year):
    """Create and save a metro area map as SVG"""
    
    # Load the GeoJSON data
    with open(geojson_file, 'r') as f:
        geojson_data = json.load(f)
    
    if not geojson_data['features']:
        print(f"No features found in {geojson_file}")
        return
    
    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Color the tracts based on gap and application count
    colors = []
    for idx, row in gdf.iterrows():
        gap = row['gap']
        white_total = row['white_total']
        black_total = row['black_total']
        colors.append(get_gap_color(gap, white_total, black_total))
    
    # Plot the tracts
    gdf.plot(color=colors, ax=ax, edgecolor='white', linewidth=0.5)
    


    # Add water and park features if available
    try:
        water_parks_file = f'water_parks_{metro_name.replace("/", "-").replace(",", "").replace(" ", "_")}.geojson'
        if os.path.exists(water_parks_file):
            with open(water_parks_file, 'r') as f:
                water_parks_data = json.load(f)
            
            # Convert water/parks to GeoDataFrame
            water_parks_gdf = gpd.GeoDataFrame.from_features(water_parks_data['features'])
            
            # Plot water features (rivers, lakes, coastline)
            water_features = water_parks_gdf[water_parks_gdf['type'].isin(['water', 'coastline'])]
            if not water_features.empty:
                water_features.plot(ax=ax, color='#808080', linewidth=2, alpha=0.7)
                
                # Add labels for major water features
                major_water = water_features[water_features['name'].str.contains('River|Lake|Ocean|Bay', case=False)]
                for idx, water in major_water.iterrows():
                    if water.geometry.geom_type == 'LineString':
                        coords = list(water.geometry.coords)[0]
                    else:
                        coords = list(water.geometry.exterior.coords)[0]
                    ax.annotate(water['name'], 
                               xy=coords,
                               xytext=(5, -5), textcoords='offset points',
                               fontsize=7, fontweight='bold', color='#696969',
                               bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
            
            # Plot park features
            park_features = water_parks_gdf[water_parks_gdf['type'] == 'park']
            if not park_features.empty:
                park_features.plot(ax=ax, color='#D3D3D3', edgecolor='#696969', linewidth=1, alpha=0.6)
                
    except Exception as e:
        print(f"  Could not add water/parks: {e}")
    
    # Remove axes
    ax.set_axis_off()
    
    # Add title
    plt.suptitle(f'{metro_name}\nBlack-White Mortgage Approval Rate Gaps ({year})', 
                 fontsize=16, fontweight='bold', y=0.95)
    
    # Add legend
    legend_elements = [
        mpatches.Patch(color='#CC6600', label='Very High Gap (>15%)'),
        mpatches.Patch(color='#FF8000', label='High Gap (10-15%)'),
        mpatches.Patch(color='#FFB366', label='Medium Gap (5-10%)'),
        mpatches.Patch(color='#FFE5CC', label='Low Gap (<5%)'),
        mpatches.Patch(color='#4A90E2', label='No Gap/Positive'),
        mpatches.Patch(color='#cccccc', label='Insufficient Data (<5 applications)')
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1), 
              fontsize=10, frameon=True, fancybox=True, shadow=True)
    
    # Calculate and display statistics
    valid_tracts = gdf[gdf['white_total'] + gdf['black_total'] >= 5]
    if len(valid_tracts) > 0:
        avg_gap = valid_tracts['gap'].mean()
        avg_white_rate = valid_tracts['white_rate'].mean()
        avg_black_rate = valid_tracts['black_rate'].mean()
        
        stats_text = f'Average White Rate: {avg_white_rate:.1%}\n'
        stats_text += f'Average Black Rate: {avg_black_rate:.1%}\n'
        stats_text += f'Average Gap: {avg_gap:.1%}\n'
        stats_text += f'Total Tracts: {len(gdf)}'
        
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                verticalalignment='top', fontsize=12, 
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Save as SVG
    safe_name = metro_name.replace('/', '-').replace(',', '').replace(' ', '_')
    filename = f'metro-areas/{year}_{safe_name}.svg'
    plt.savefig(filename, format='svg', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {filename}")

def main():
    """Export all metro area maps for all years"""
    years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
    
    for year in years:
        print(f"\nProcessing year {year}...")
        for code, name in metro_areas.items():
            geojson_file = f'metro_tracts_{code}_{year}.geojson'
            
            if os.path.exists(geojson_file):
                print(f"Creating map for {name} ({year})...")
                create_metro_map(geojson_file, name, year)
            else:
                print(f"File not found: {geojson_file}")
    
    print(f"\nAll maps exported to metro-areas/ folder!")

if __name__ == "__main__":
    main() 