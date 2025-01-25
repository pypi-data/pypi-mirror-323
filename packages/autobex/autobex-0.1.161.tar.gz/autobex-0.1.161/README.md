# Autobex

Autobex helps you find abandoned and interesting locations using OpenStreetMap data. Search by radius or polygon area to discover ruins, bunkers, and abandoned structures. Get elevation data and direct links to maps.

## Installation

```bash
pip install autobex
```

## Basic Usage

```python
from autobex import OSMSearchPlus

# Initialize searcher
searcher = OSMSearchPlus()

# Search within 5 mile radius of coordinates
results = searcher.search(
    lat=42.554056, 
    lon=-70.928823,
    radius=5.0
)

# Print results
for group in results:
    for location in group:
        print(f"Name: {location.name}")
        print(f"Type: {location.type}")
        print(f"Distance: {location.distance/1609.34:.2f} miles")
        print(f"Elevation: {location.elevation}m")
        print(f"OpenStreetMap: {location.osm_url}")
        print(f"Google Maps: {location.google_maps_url}")
        print(f"Bing Maps: {location.bing_maps_url}")
        print("Tags:", location.tags)
        print()
```

## Search Options

### Tag Search
You can search using:
- Default tags from tags.txt
- Custom tags
- Regex pattern matching with the `~` operator

```python
# List available search tags
for tag in searcher.list_tags():
    print(tag)

# Search with custom tags
results = searcher.search(
    lat=42.554056,
    lon=-70.928823,
    radius=5.0,
    use_default_tags=False,
    custom_tags=[
        "building=ruins",           # Exact match
        "name~Superfund",          # Regex match (case-insensitive)
        "abandoned"                # Simple tag
    ]
)
```

### Area Search
Search within:
- Radius (in miles) from coordinates
- Custom polygon area

### Location Results
Each location includes:
- Name and type
- Distance from search center
- Elevation (meters)
- Direct links to:
  - OpenStreetMap
  - Google Maps
  - Bing Maps
- All associated OSM tags

### Location Groups
Nearby locations are automatically grouped with:
- Intelligent group naming based on status, type, and location
- Distance-based clustering
- Group statistics

### Error Handling
- Automatic retries for API timeouts
- Detailed logging for timeout events and recovery
- Graceful fallback options

## Features

- Search by radius or polygon area
- Elevation data for each location
- Direct map links (OpenStreetMap, Google Maps, Bing Maps)
- Automatic grouping of nearby locations
- Intelligent group naming
- List available search tags
- Support for regex tag matching
- Timeout handling and logging
- Customizable search parameters

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

MIT

## Configuration Files

### tags.txt
Contains tags to search for by default. Each line should be either:
- A simple tag (e.g., `abandoned`)
- A key=value pair (e.g., `building=ruins`)
- A name pattern (e.g., `name~Factory`)

You can view all configured tags using `searcher.list_tags()`.

### excluded_tags.txt
Contains tags that will exclude locations from results. Same format as `tags.txt`.
If not found, default exclusions are used (e.g., `demolished=yes`, `highway=bus_stop`, etc.).

## Features

- List and inspect available search tags
- Intelligent group naming based on common properties
- Search by radius or polygon area
- Support for both decimal and DMS coordinates
- Automatic grouping of nearby locations (100m radius)
- Distance calculations (direct and to nearest road)
- Elevation data and reverse geocoding
- Direct links to OpenStreetMap, Google Maps, and Bing Maps
- Tag-based filtering and exclusions
- Increased timeout values for slower connections

## Quick Start

```bash
pip install autobex
```

## Location Properties

### Core Properties
- `name` - Location name (from OSM or reverse geocoding)
- `latitude`, `longitude` - Decimal coordinates
- `distance` - Direct distance from search center (miles)
- `road_distance` - Distance to nearest road (miles)
- `elevation` - Height above sea level (meters)
- `osm_url` - Direct link to OpenStreetMap node/way
- `google_maps_url` - Google Maps link (max zoom)
- `bing_maps_url` - Bing Maps link (aerial view)

### OpenStreetMap Data
- `osm_id` - OpenStreetMap ID
- `type` - Element type (node or way)
- `tags` - Dictionary of all OSM tags

## Tag Configuration

### Search Tags (tags.txt)
```
# Exact matches
building=ruins
historic=ruins

# Simple tags (match as key or value)
abandoned
ruins

# Name patterns
name~Factory
```

### Excluded Tags (excluded_tags.txt)
```
# Filter out these locations
demolished=yes
highway=bus_stop

# Exclude common noise
```

## Output Format
```
Location: Example Location (OSM ID: 123456)
----------------------------------------
Direct distance: 1.23 miles
Distance to nearest road: 0.15 miles
Elevation: 42.1 meters

View on Maps:
OpenStreetMap: https://www.openstreetmap.org/way/123456
Google Maps: https://...
Bing Maps: https://...

OpenStreetMap Tags:
building             = ruins
historic            = yes
name                = Old Mill
```

## Advanced Usage

### Polygon Search
```python
polygon = [
    ("42°25'12.3\"N", "70°54'37.4\"W"),
    (42.42103, -70.90324),
    ("42°25'05.0\"N", "70°54'01.1\"W"),
    (42.41492, -70.90501)
]
results = searcher.search(polygon_coords=polygon)
```

### Location Groups
Results are automatically grouped by proximity (100m radius):
```python
for group in results:
    # Get group center
    center_lat, center_lon = group.center()
    
    # Get maximum span in miles
    span = group.distance_span()
    
    # Filter by tag
    ruins = group.filter_by_tag('building', 'ruins')
    
    # Get average elevation
    avg_height = group.average_elevation()
```

### Error Handling
```python
from autobex import OSMSearchError

try:
    results = searcher.search(lat=42.3601, lon=-71.0589, radius=1.0)
except OSMSearchError as e:
    print(f"Search failed: {e}")
```

## Performance Tips

1. Use appropriate search radius (smaller = faster)
2. Use `limit` parameter when possible
3. Keep tag files focused and minimal
4. Use `excluded_tags.txt` to filter noise
5. Enable `show_logs=True` to monitor progress

## Dependencies

- Python 3.7+
- geopy
- requests
- numpy

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- OpenStreetMap contributors
- Open-Elevation API

## Support

- Report bugs through our [Issue Tracker](https://github.com/the-Drunken-coder/Autobex/issues)
- Check out our [Documentation](https://github.com/the-Drunken-coder/Autobex#readme) for more examples

## Coordinate Input Formats

The system automatically detects and handles multiple coordinate formats:

```python
# Decimal Degrees (as string or float)
search.search(lat="41.2345", lon="-71.2345")
search.search(lat=41.2345, lon=-71.2345)

# Degrees, Minutes, Seconds (DMS)
search.search(lat="41°28'50.4\"N", lon="71°23'35.5\"W")
```

The coordinate parser automatically:
- Detects the format (decimal or DMS)
- Handles special quote characters (′ ″)
- Validates coordinate ranges (latitude: -90 to 90, longitude: -180 to 180)
- Converts everything to decimal degrees internally

### Tag Matching

The system uses two types of tag matching:

1. Exact matches (with `=`):
   ```
   building=ruins    -> matches exactly building=ruins
   ```

2. Simple tags (without `=`):
   ```
   abandoned        -> matches:
                      - abandoned=* (any value)
                      - building=abandoned
                      - historic=abandoned
   ```

3. Name patterns (with `~`):
   ```
   name~Factory    -> matches locations with "Factory" in their name
   ```

The search is optimized to:
- Use simple, reliable queries
- Avoid complex regex patterns
- Find locations quickly and efficiently
- Handle both nodes (points) and ways (areas)

You can view all configured tags using:
```python
# List all available search tags
for tag in searcher.list_tags():
    print(tag)
```

Note: All searchable tags are configured in the `tags.txt` file. Example contents:
```
building=ruins
abandoned
ruins
disused
bunker_type
building=bunker
name~Factory
```

You can customize which tags to search for by editing this file.

## Testing and Debugging

### Test Query Tool

The package includes a test query tool (`test_query.py`) that helps visualize search results in a readable format:

```python
python test_query.py
```

Sample output:
```
Querying area...

Found 1 location in 1 group

========================================
Group 1 (1 locations)
========================================

Location 1:
----------------------------------------
Name: Northeastern University Marine Science Center
Type: way
OSM ID: 123456789
Distance: 0.04 miles
Elevation: 15.2m (49.9ft)

Map Links:
  Google Maps: https://www.google.com/maps?q=42.4185,-70.9056&z=21
  Bing Maps: https://www.bing.com/maps?cp=42.4185~-70.9056&style=h&lvl=20

Tags:
  • building = yes
  • historic = ruins
  • name = Northeastern University Marine Science Center
  • abandoned = yes
----------------------------------------
```

The output includes:
1. Location basics (name, type, OSM ID)
2. Distance from search center (in miles)
3. Elevation (in meters and feet)
4. Direct links to Google Maps and Bing Maps (maximum zoom)
5. All raw OSM tags associated with the location

You can modify the search coordinates in `test_query.py` to explore different areas.
