# Metro Area Tract-Level Approval Gap Maps

Interactive visualization showing Black-White mortgage approval rate gaps by census tract across 27 major US metropolitan areas.

## 🏙️ Features

- **27 Metro Areas** with tract-level detail
- **Canvas rendering** for optimal performance
- **Year selection** (2018-2023) with year buttons
- **Color-coded approval gaps** with legend
- **Water features and landmarks** for geographic context

## 📊 Data

- `metro_tracts_*.geojson` - Tract-level approval data (162 files)
- `landmarks_*.geojson` - Major landmarks for each metro area
- `water_parks_*.geojson` - Water features and parks
- `metro_race_summary.csv` - Metro-level summary data

## 🚀 Setup

1. **Start local server:**
   ```bash
   python -m http.server 8000
   ```

2. **Open in browser:**
   ```
   http://localhost:8000/metro_maps/metro_tracts_simple.html
   ```

## 🎯 Usage

- **Click year buttons** to change year (2018-2023)
- **View 27 metro areas** with tract-level detail
- **Hover over tracts** to see approval gap data
- **View legend** for gap categories

## 📁 Files

### Core Files
- `metro_tracts_simple.html` - Main visualization
- `metro_race_summary.csv` - Metro-level data
- `export_metro_maps.py` - Export maps as SVG
- `add_water_parks_to_maps.py` - Add water features
- `add_landmarks_to_maps.py` - Add landmarks
- `fix_geojson_crs.py` - Fix coordinate systems

### Data Files
- `metro_tracts_*.geojson` - Tract boundaries with approval data
- `landmarks_*.geojson` - Landmark points
- `water_parks_*.geojson` - Water and park features
- `metro_area_shapefile/` - Metro area boundaries

## 🎨 Design

- **Color scheme**: Orange for gaps, Blue for no gap/positive
- **Canvas rendering**: Optimized for performance with many small maps
- **Gap categories**: Low (<5%), Medium (5-10%), High (10-15%), Very High (>15%)
- **Grey areas**: Insufficient data (<5 applications)

## 🗺️ Metro Areas Included

1. New York-Newark-Jersey City, NY-NJ-PA
2. Los Angeles-Long Beach-Anaheim, CA
3. Chicago-Naperville-Elgin, IL-IN-WI
4. Houston-The Woodlands-Sugar Land, TX
5. Phoenix-Mesa-Chandler, AZ
6. Philadelphia-Camden-Wilmington, PA-NJ-DE-MD
7. San Antonio-New Braunfels, TX
8. San Diego-Chula Vista-Carlsbad, CA
9. Dallas-Fort Worth-Arlington, TX
10. San Jose-Sunnyvale-Santa Clara, CA
11. Austin-Round Rock-San Marcos, TX
12. Jacksonville, FL
13. Fort Worth-Arlington, TX
14. Columbus, OH
15. Charlotte-Concord-Gastonia, NC-SC
16. San Francisco-Oakland-Fremont, CA
17. Indianapolis-Carmel-Anderson, IN
18. Seattle-Tacoma-Bellevue, WA
19. Denver-Aurora-Centennial, CO
20. Washington-Arlington-Alexandria, DC-VA-MD-WV
21. Boston-Cambridge-Newton, MA-NH
22. El Paso, TX
23. Detroit-Warren-Dearborn, MI
24. Nashville-Davidson-Murfreesboro-Franklin, TN
25. Portland-Vancouver-Hillsboro, OR-WA
26. Memphis, TN-MS-AR
27. Oklahoma City, OK
