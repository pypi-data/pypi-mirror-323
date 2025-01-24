# OSM Search Plus

A Python package for searching OpenStreetMap data with advanced features and filtering.

## Installation

```bash
pip install autobex
```

## Basic Usage

```python
from autobex import OSMSearchPlus

# Initialize searcher
searcher = OSMSearchPlus()

# Search with coordinates and radius
results = searcher.search(
    lat=42.3601,  # Latitude in decimal degrees
    lon=-71.0589, # Longitude in decimal degrees
    radius=5.0    # Search radius in miles
)

# Print results
for group in results:
    print(f"Group: {group.name}")  # Descriptive group name
    for location in group:
        print(f"  - {location}")
```

## Search Options

### Tag Configuration

You can control which tags to search for in two ways:

1. Default tags from `tags.txt`:
```python
# Use only default tags (default behavior)
results = searcher.search(lat, lon, radius)

# Disable default tags
results = searcher.search(lat, lon, radius, use_default_tags=False)
```

2. Custom tags:
```python
# Use custom tags only
results = searcher.search(
    lat, lon, radius,
    use_default_tags=False,
    custom_tags=["building=ruins", "abandoned"]
)

# Use both default and custom tags
results = searcher.search(
    lat, lon, radius,
    custom_tags=["building=ruins"]  # Will combine with default tags
)
```

### Search Area

Search by radius:
```python
results = searcher.search(lat=42.3601, lon=-71.0589, radius=5.0)  # 5 mile radius
```

Search in polygon:
```python
polygon = [
    (42.3601, -71.0589),
    (42.3702, -71.0690),
    (42.3803, -71.0791)
]
results = searcher.search(polygon_coords=polygon)
```

### Coordinate Formats

Supports both decimal degrees and DMS format:

```python
# Decimal degrees
results = searcher.search(lat=42.3601, lon=-71.0589, radius=5.0)

# DMS format
results = searcher.search(
    lat='41°28\'50.4"N',
    lon='71°23\'35.5"W',
    radius=5.0
)
```

### Logging and Debug Information

Enable detailed logging to see search progress:

```python
results = searcher.search(lat, lon, radius, show_logs=True)
```

This will show:
- Tags being searched
- Number of elements found
- Processing progress
- Number of locations added per tag
- Total unique locations found
- Grouping information

## Location Results

Each location contains:

### Core Properties (not from OSM)
- `location.name`: Generated from OSM name or reverse geocoding
- `location.latitude`, `location.longitude`: Coordinates
- `location.distance`: Direct distance from search center in meters
- `location.road_distance`: Distance to nearest road in meters
- `location.elevation`: Elevation in meters
- `location.google_maps_url`: Link to Google Maps
- `location.bing_maps_url`: Link to Bing Maps
- `location.osm_url`: Link to OpenStreetMap

### OSM-specific Data
- `location.osm_id`: OpenStreetMap ID
- `location.type`: Type of element (node or way)
- `location.tags`: Dictionary of all OpenStreetMap tags

### Accessing Tag Information

```python
# Check if a tag exists
if "abandoned" in location.tags:
    print("This is an abandoned location")

# Get tag value with fallback
building_type = location.tags.get("building", "unknown")

# Print all tags
print(location.all_tags())
```

## Location Groups

Results are automatically grouped by proximity (within 100 meters). Each group has an intelligent naming system that combines:

1. Status (if common across group):
   - Abandoned
   - Ruins
   - Disused
   - Demolished

2. Type (from most to least specific):
   - Amenity
   - Military
   - Building
   - Historic
   - Landuse

3. Location:
   - City name (when available)
   - State/Region
   - Fallback to shortest location name if geocoding fails

4. Group size:
   - Number of locations in the group

Example group names:
- "Abandoned Factory - Boston, Massachusetts (3 locations)"
- "Military Bunker - Portland, Maine"
- "Ruins - Historic Site - Burlington, Vermont (2 locations)"

```python
for group in results:
    # Access the intelligent group name
    print(f"\nGroup: {group.name}")
    
    # Get group statistics
    print(f"Center: {group.center()}")
    print(f"Distance span: {group.distance_span()} miles")
    
    # Filter group by tag
    ruins = group.filter_by_tag("building", "ruins")
    abandoned = group.filter_by_tag("abandoned")
```

## Error Handling

The package includes automatic retry logic for API timeouts and rate limits. It will:
- Retry failed queries up to 3 times
- Use progressive backoff delays
- Handle rate limiting gracefully
- Provide detailed error messages

## Configuration Files

### tags.txt
Contains tags to search for by default. Each line should be either:
- A simple tag (e.g., `abandoned`)
- A key=value pair (e.g., `building=ruins`)

### excluded_tags.txt
Contains tags that will exclude locations from results. Same format as `tags.txt`.
If not found, default exclusions are used (e.g., `demolished=yes`, `highway=bus_stop`, etc.).

## Features

- Intelligent group naming based on common properties
- Search by radius or polygon area
- Support for both decimal and DMS coordinates
- Automatic grouping of nearby locations (100m radius)
- Distance calculations (direct and to nearest road)
- Elevation data and reverse geocoding
- Direct links to OpenStreetMap, Google Maps, and Bing Maps
- Tag-based filtering and exclusions

## Quick Start

```bash
pip install autobex
```

```python
from autobex import OSMSearchPlus

# Initialize searcher
searcher = OSMSearchPlus()

# Search using decimal or DMS coordinates
results = searcher.search(
    lat="41°28'50.4\"N",  # or 41.4807
    lon="71°23'35.5\"W",  # or -71.3932
    radius=1.0  # miles
)

# Process results with intelligent group names
for group in results:
    print(f"\nGroup: {group.name}")
    for location in group:
        print(f"  - {location.name}")
        print(f"    {location.all_tags()}")
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

- Report bugs through our [Issue Tracker](https://github.com/yourusername/OSMsearch/issues)
- Join our [Discord community](https://discord.gg/yourdiscord) for help
- Check out our [Wiki](https://github.com/yourusername/OSMsearch/wiki) for more examples

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

The search is optimized to:
- Use simple, reliable queries
- Avoid complex regex patterns
- Find locations quickly and efficiently
- Handle both nodes (points) and ways (areas)

Note: All searchable tags are configured in the `tags.txt` file. Example contents:
```
building=ruins
abandoned
ruins
disused
bunker_type
building=bunker
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
