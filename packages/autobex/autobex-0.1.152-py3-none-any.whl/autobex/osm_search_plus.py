try:
    import geopy.distance
    from geopy.geocoders import Nominatim
except ImportError:
    print("Please install geopy: pip install geopy")
    raise
import requests
import logging
import os
import pkg_resources
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from statistics import mean
import numpy as np
import time

class OSMSearchError(Exception):
    """Custom exception for OSM search errors"""
    pass

@dataclass
class LocationGroup:
    """Class to handle operations on a group of locations"""
    locations: List['LocationResult']

    def __len__(self) -> int:
        """Return number of locations in group"""
        return len(self.locations)
    
    def __iter__(self):
        """Make group iterable"""
        return iter(self.locations)
    
    def __getitem__(self, index):
        """Allow indexing into group"""
        return self.locations[index]

    @property
    def name(self) -> str:
        """Generate a descriptive name for the group based on its contents"""
        if not self.locations:
            return "Empty Group"
            
        # Get all unique non-empty names
        names = {loc.name for loc in self.locations if loc.name and loc.name != "Unknown Location"}
        if not names:
            return "Unnamed Group"
            
        # If all locations have the same name, use that
        if len(names) == 1:
            return next(iter(names))
            
        # Get common tags across all locations
        common_tags = {}
        for key in self.locations[0].tags:
            if all(loc.tags.get(key) == self.locations[0].tags[key] for loc in self.locations):
                common_tags[key] = self.locations[0].tags[key]
                
        # Try to create a descriptive name from common tags
        name_parts = []
        
        # Add status description if common (abandoned, ruins, etc)
        status_tags = ['abandoned', 'ruins', 'disused', 'demolished']
        status = next((tag for tag in status_tags if tag in common_tags), None)
        if status:
            name_parts.append(status.title())
            
        # Add type description from most specific to least specific
        type_keys = ['amenity', 'military', 'building', 'historic', 'landuse']
        for key in type_keys:
            if key in common_tags and common_tags[key] not in ['yes', 'no']:
                type_value = common_tags[key].replace('_', ' ').title()
                if type_value not in name_parts:  # Avoid duplicates
                    name_parts.append(type_value)
                break  # Only use most specific type
                
        # Add location description
        center_lat, center_lon = self.center()
        try:
            geolocator = Nominatim(user_agent="autobex_osm_search")
            location = geolocator.reverse(f"{center_lat}, {center_lon}", language="en")
            if location and location.address:
                # Try to get city and state/region
                address_parts = location.address.split(", ")
                location_parts = []
                
                # Look for city
                city_found = False
                for part in address_parts:
                    if any(city_type in part.lower() for city_type in ['city', 'town', 'village', 'municipality']):
                        location_parts.append(part.split(" ")[0])  # Take first word of city part
                        city_found = True
                        break
                if not city_found and len(address_parts) > 2:
                    location_parts.append(address_parts[2])  # Usually city is third component
                    
                # Add state/region
                for part in address_parts:
                    if any(state_type in part.lower() for state_type in ['state', 'province', 'region', 'county']):
                        location_parts.append(part)
                        break
                
                if location_parts:
                    name_parts.append(", ".join(location_parts))
        except Exception:
            # If geocoding fails, use the shortest location name
            shortest_name = min(names, key=len)
            name_parts.append(shortest_name)
            
        # Add group size if more than one location
        if len(self.locations) > 1:
            name_parts.append(f"({len(self.locations)} locations)")
            
        return " - ".join(name_parts)

    def __str__(self) -> str:
        """String representation of the group"""
        return f"{self.name} | Center: {self.center()} | Span: {self.distance_span():.2f} miles"

    def center(self) -> Tuple[float, float]:
        """Calculate the center point of the group"""
        if not self.locations:
            raise OSMSearchError("Cannot calculate center of empty group")
        return (
            mean(loc.latitude for loc in self.locations),
            mean(loc.longitude for loc in self.locations)
        )

    def distance_span(self) -> float:
        """Calculate the maximum distance between any two points in miles"""
        if len(self.locations) < 2:
            return 0.0
            
        max_distance = 0.0
        for i, loc1 in enumerate(self.locations):
            for loc2 in self.locations[i+1:]:
                # Skip if any coordinates are None
                if None in (loc1.latitude, loc1.longitude, loc2.latitude, loc2.longitude):
                    continue
                    
                try:
                    dist = geopy.distance.geodesic(
                        (loc1.latitude, loc1.longitude),
                        (loc2.latitude, loc2.longitude)
                    ).miles
                    if dist is not None:
                        max_distance = max(max_distance, dist)
                except Exception:
                    continue
                    
        return max_distance

    def filter_by_tag(self, key: str, value: Optional[str] = None) -> List['LocationResult']:
        """Filter locations by tag key and optional value"""
        if value is None:
            return [loc for loc in self.locations if key in loc.tags]
        return [loc for loc in self.locations if loc.tags.get(key) == value]

    def average_elevation(self) -> Optional[float]:
        """Calculate average elevation of the group in meters"""
        elevations = [loc.elevation for loc in self.locations if loc.elevation is not None]
        return mean(elevations) if elevations else None

@dataclass
class LocationResult:
    """Data class to store search results"""
    # Required properties
    latitude: float
    longitude: float
    osm_id: str
    type: str  # node, way, relation
    name: str  # Generated from OSM name or reverse geocoding
    tags: Dict[str, str]  # All raw tags from OSM
    
    # Optional properties with defaults
    distance: Optional[float] = None  # Direct distance in meters
    road_distance: Optional[float] = None  # Distance to nearest road in meters
    elevation: Optional[float] = None
    google_maps_url: Optional[str] = None
    bing_maps_url: Optional[str] = None
    osm_url: Optional[str] = None

    def __post_init__(self):
        """Generate map URLs after initialization"""
        # Google Maps URL with marker and zoom level 21 (maximum zoom)
        self.google_maps_url = f"https://www.google.com/maps?q={self.latitude},{self.longitude}&z=21"
        # Bing Maps URL with aerial view and zoom level 20 (maximum zoom)
        self.bing_maps_url = f"https://www.bing.com/maps?cp={self.latitude}~{self.longitude}&style=h&lvl=20"
        # OpenStreetMap URL with the OSM ID and type
        if self.type == 'node':
            self.osm_url = f"https://www.openstreetmap.org/node/{self.osm_id}"
        elif self.type == 'way':
            self.osm_url = f"https://www.openstreetmap.org/way/{self.osm_id}"
        else:
            self.osm_url = f"https://www.openstreetmap.org/search?query={self.latitude}%2C{self.longitude}"
        
    def all_tags(self, include_empty: bool = False) -> str:
        """
        Get all tags in a readable format.
        Args:
            include_empty: Whether to include tags with empty values
        Returns:
            Formatted string of all tags
        """
        def format_distance(meters: Optional[float]) -> str:
            """Helper to safely format distance in miles"""
            if meters is None:
                return "unknown"
            return f"{meters/1609.34:.2f} miles"
            
        lines = []
        lines.append(f"\nLocation: {self.name} (OSM ID: {self.osm_id})")
        lines.append("-" * 40)
        
        # Add distance information first
        if self.distance is not None:
            lines.append(f"Direct distance: {format_distance(self.distance)}")
        if self.road_distance is not None:
            lines.append(f"Distance to nearest road: {format_distance(self.road_distance)}")
        
        # Add elevation if available
        if self.elevation is not None:
            lines.append(f"Elevation: {self.elevation:.1f} meters")
            
        # Add map links
        lines.append(f"\nView on Maps:")
        lines.append(f"OpenStreetMap: {self.osm_url}")
        lines.append(f"Google Maps: {self.google_maps_url}")
        lines.append(f"Bing Maps: {self.bing_maps_url}")
        
        # Add OSM tags at the bottom
        if self.tags:
            lines.append(f"\nOpenStreetMap Tags:")
            # Get sorted tags for consistent output
            sorted_tags = sorted(self.tags.items())
            for key, value in sorted_tags:
                if value or include_empty:
                    lines.append(f"{key:20s} = {value}")
        else:
            lines.append("\nNo OpenStreetMap tags found")
                
        return "\n".join(lines)

    def __str__(self) -> str:
        """String representation of the location"""
        def format_distance(meters: Optional[float]) -> str:
            if meters is None:
                return "unknown distance"
            return f"{meters/1609.34:.2f} miles"
            
        parts = [f"{self.name} ({self.type} {self.osm_id})"]
        if self.distance is not None:
            parts.append(f"Distance: {format_distance(self.distance)}")
        if self.road_distance is not None:
            parts.append(f"Road distance: {format_distance(self.road_distance)}")
        return " | ".join(parts)

class OSMSearchPlus:
    def __init__(self, logger=None):
        """Initialize OSM searcher with optional custom logger"""
        self.api_url = 'https://overpass-api.de/api/interpreter'
        self.elevation_api = 'https://api.open-elevation.com/api/v1/lookup'
        
        # Overpass API settings
        self.timeout = 25  # Increased timeout for slower connections
        self.max_retries = 3
        self.retry_delay = 1  # 1 second between retries
        self.min_query_delay = 0.5  # Half second between queries
        self.last_query_time = 0
        
        self.logger = logger or self._setup_default_logger()
        
        # Configure geocoder with same timeout
        self.geolocator = Nominatim(
            user_agent="autobex_osm_search",
            timeout=25  # Increased timeout for slower connections
        )
        
        # Rate limiting for geocoding
        self.geocoding_delay = 1.0
        self.last_geocoding_time = 0
        
        # Load tags from package resources
        try:
            self.tags_file = pkg_resources.resource_filename('autobex', 'tags.txt')
            self.excluded_tags_file = pkg_resources.resource_filename('autobex', 'excluded_tags.txt')
        except Exception as e:
            # If resource_filename fails, try to find files relative to this script
            import os
            package_dir = os.path.dirname(os.path.abspath(__file__))
            self.tags_file = os.path.join(package_dir, 'tags.txt')
            self.excluded_tags_file = os.path.join(package_dir, 'excluded_tags.txt')
        
        self.tags = self._load_tags()
        self.excluded_tags = self._load_excluded_tags()

    def _setup_default_logger(self) -> logging.Logger:
        """Set up default logging configuration"""
        logger = logging.getLogger('autobex_osm')
        # Clear any existing handlers
        logger.handlers = []
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        # Prevent logging propagation to root logger
        logger.propagate = False
        return logger

    def _load_tags(self) -> List[str]:
        """Load tags from tags.txt file"""
        try:
            # Try multiple locations for the file
            import os
            possible_locations = [
                self.tags_file,  # Try pkg_resources location first
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tags.txt'),  # Try package directory
                os.path.join(os.getcwd(), 'tags.txt'),  # Try current directory
            ]
            
            for file_path in possible_locations:
                try:
                    with open(file_path, 'r') as f:
                        tags = [line.strip() for line in f.readlines() 
                                if line.strip() and not line.startswith('#')]
                        if tags:
                            self.logger.debug(f"Loaded tags from {file_path}")
                            return tags
                except (IOError, OSError):
                    continue
                    
            self.logger.error("Could not find tags.txt in any location")
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to load tags: {e}")
            return []

    def _load_excluded_tags(self) -> List[str]:
        """Load excluded tags from excluded_tags.txt file and combine with defaults"""
        # Default exclusions always included
        default_exclusions = [
            'demolished=yes',
            'highway=bus_stop',
            'highway=traffic_signals',
            'highway=street_lamp',
            'amenity=parking',
            'amenity=bench',
            'amenity=waste_basket',
            'barrier',
            'crossing',
            # Adding manual exclusions from excluded_tags.txt
            'highway',
            'surface=asphalt'
        ]
        
        try:
            # Try multiple locations for the file
            import os
            possible_locations = [
                self.excluded_tags_file,  # Try pkg_resources location first
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'excluded_tags.txt'),  # Try package directory
                os.path.join(os.getcwd(), 'excluded_tags.txt'),  # Try current directory
            ]
            
            for file_path in possible_locations:
                try:
                    with open(file_path, 'r') as f:
                        file_exclusions = [line.strip() for line in f.readlines() 
                                if line.strip() and not line.startswith('#')]
                        if file_exclusions:
                            self.logger.debug(f"Loaded additional excluded tags from {file_path}")
                            # Combine default exclusions with file exclusions, removing duplicates
                            all_exclusions = list(set(default_exclusions + file_exclusions))
                            return all_exclusions
                except (IOError, OSError):
                    continue
            
            # If no file found, use defaults
            self.logger.debug("Using default excluded tags")
            return default_exclusions
            
        except Exception as e:
            self.logger.debug(f"Using default excluded tags (error: {e})")
            return default_exclusions

    def _should_exclude_location(self, tags: Dict[str, str]) -> bool:
        """Check if a location should be excluded based on its tags"""
        for excluded_tag in self.excluded_tags:
            if '=' in excluded_tag:
                # Exact match (e.g., highway=bus_stop)
                key, value = excluded_tag.split('=', 1)
                if tags.get(key) == value:
                    return True
            else:
                # Simple tag (e.g., barrier)
                # Exclude if it exists as a key with any value
                if excluded_tag in tags:
                    return True
                # Or if it exists as a value for common keys
                for common_key in ['building', 'historic', 'amenity', 'highway']:
                    if tags.get(common_key) == excluded_tag:
                        return True
        return False

    def get_location_name(self, lat: float, lon: float, tags: Dict[str, str]) -> str:
        """Get meaningful name for the location using tags or reverse geocoding"""
        name_parts = []
        
        # Add type description
        if any(tag in tags for tag in ['abandoned', 'ruins', 'disused']):
            name_parts.append("Abandoned")
        
        # Try to get name from tags first
        if 'name' in tags:
            name_parts.append(tags['name'])
            return " - ".join(name_parts)
            
        # Only try reverse geocoding if no name in tags
        try:
            # Respect rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_geocoding_time
            if time_since_last < self.geocoding_delay:
                time.sleep(self.geocoding_delay - time_since_last)
            
            location = self.geolocator.reverse(f"{lat}, {lon}", language="en")
            self.last_geocoding_time = time.time()
            
            if location and location.address:
                address_parts = location.address.split(", ")[:2]
                name_parts.append(", ".join(address_parts))
        except Exception as e:
            if "429" in str(e):
                self.logger.warning("Rate limit exceeded for geocoding, waiting longer...")
                time.sleep(5)  # Wait longer on rate limit
            else:
                self.logger.debug(f"Geocoding error: {e}")
        
        return " - ".join(name_parts) if name_parts else "Unknown Location"

    def calculate_distance(self, coord1: Tuple[float, float], 
                         coord2: Tuple[float, float]) -> Optional[float]:
        """Calculate distance between two coordinates in meters"""
        if None in coord1 or None in coord2:
            return None
        try:
            return geopy.distance.geodesic(coord1, coord2).meters
        except Exception:
            return None

    def get_elevation(self, lat: float, lon: float) -> Optional[float]:
        """Get elevation for coordinates using Open-Elevation API"""
        try:
            response = requests.get(
                self.elevation_api,
                params={'locations': f'{lat},{lon}'},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return data['results'][0]['elevation']
        except Exception as e:
            self.logger.debug(f"Failed to get elevation: {e}")
            return None

    def _parse_coordinate(self, coord_str: str) -> float:
        """
        Parse coordinate string to decimal degrees.
        Handles multiple formats:
        - Decimal degrees (e.g., "42.3601" or "-71.0589")
        - DMS format (e.g., "41°28'50.4"N" or "71°23'35.5"W")
        """
        try:
            # First try parsing as decimal
            try:
                decimal = float(coord_str)
                if -180 <= decimal <= 180:
                    return decimal
            except ValueError:
                pass

            # If not decimal, try DMS format
            # Remove spaces and convert special quotes to standard ones
            coord_str = coord_str.strip().replace('′', "'").replace('″', '"')
            
            # Extract direction (N/S/E/W)
            direction = coord_str[-1].upper()
            if direction not in 'NSEW':
                raise ValueError(f"Invalid direction: {direction}")
            
            # Remove direction and split into degrees, minutes, seconds
            parts = coord_str[:-1].replace('°', ' ').replace("'", ' ').replace('"', ' ').split()
            
            degrees = float(parts[0])
            minutes = float(parts[1]) if len(parts) > 1 else 0
            seconds = float(parts[2]) if len(parts) > 2 else 0
            
            # Convert to decimal degrees
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            # Make negative if South or West
            if direction in 'SW':
                decimal = -decimal
                
            # Validate range
            if (direction in 'NS' and not -90 <= decimal <= 90) or \
               (direction in 'EW' and not -180 <= decimal <= 180):
                raise ValueError("Coordinate out of valid range")
                
            return decimal
            
        except Exception as e:
            raise OSMSearchError(f"Failed to parse coordinate {coord_str}: {str(e)}")

    def _validate_coordinates(self, lat: float, lon: float) -> None:
        """Validate coordinate ranges"""
        if not -90 <= lat <= 90:
            raise ValueError(f"Latitude {lat} is out of valid range (-90 to 90)")
        if not -180 <= lon <= 180:
            raise ValueError(f"Longitude {lon} is out of valid range (-180 to 180)")

    def _send_overpass_query(self, query: str) -> dict:
        """Send query to Overpass API with retry logic and rate limiting"""
        # Respect rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_query_time
        if time_since_last < self.min_query_delay:
            time.sleep(self.min_query_delay - time_since_last)
        
        for attempt in range(self.max_retries):
            try:
                # Update query timeout to match our timeout
                query = query.replace('[timeout:30]', f'[timeout:{self.timeout}]')
                query = query.replace(f'[timeout:{self.timeout*2}]', f'[timeout:{self.timeout}]')
                
                response = requests.post(
                    self.api_url,
                    data={'data': query},
                    timeout=self.timeout
                )
                response.raise_for_status()
                self.last_query_time = time.time()
                return response.json()
                
            except requests.Timeout:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (attempt + 1)  # Progressive delay
                    self.logger.warning(f"Timeout, retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise OSMSearchError("Overpass API timeout after all retries")
                    
            except requests.RequestException as e:
                if "429" in str(e):  # Rate limit exceeded
                    if attempt < self.max_retries - 1:
                        delay = 5 * (attempt + 1)  # Shorter delay for rate limits
                        self.logger.warning(f"Rate limit exceeded, waiting {delay} seconds...")
                        time.sleep(delay)
                    else:
                        raise OSMSearchError("Rate limit exceeded after all retries")
                elif attempt < self.max_retries - 1:
                    delay = self.retry_delay * (attempt + 1)
                    self.logger.warning(f"Request failed, retrying in {delay} seconds... Error: {e}")
                    time.sleep(delay)
                else:
                    raise OSMSearchError(f"Overpass API request failed after all retries: {e}")

    def search(self, lat: Union[str, float, None] = None, 
              lon: Union[str, float, None] = None,
              radius: Optional[float] = None, 
              polygon_coords: Optional[List[Tuple[Union[str, float], Union[str, float]]]] = None,
              limit: int = 100, sort_by: str = 'distance',
              show_logs: bool = False,
              use_default_tags: bool = True,
              custom_tags: Optional[List[str]] = None) -> List[LocationGroup]:
        """Search for locations using either radius or polygon search
        
        Args:
            lat: Latitude as decimal degrees or DMS string
            lon: Longitude as decimal degrees or DMS string
            radius: Search radius in miles
            polygon_coords: List of (lat, lon) tuples defining a search polygon
            limit: Maximum number of results to return
            sort_by: How to sort results ('distance' or 'name')
            show_logs: Whether to show detailed logging
            use_default_tags: Whether to use tags from tags.txt file (default True)
            custom_tags: Optional list of custom tags to search for (e.g. ["building=ruins", "abandoned"])
        """
        # Validate required parameters
        if not polygon_coords and not all([lat, lon, radius]):
            raise ValueError("Must provide either polygon_coords or (lat, lon, radius)")

        # Validate radius if provided
        if radius is not None and radius <= 0:
            raise ValueError(f"Radius must be positive, got {radius}")

        # Convert coordinates if they're strings
        if lat is not None and lon is not None:
            if isinstance(lat, str):
                lat = self._parse_coordinate(lat)
            if isinstance(lon, str):
                lon = self._parse_coordinate(lon)
            # Validate coordinates after conversion
            self._validate_coordinates(lat, lon)
                
        # Convert and validate polygon coordinates if provided
        if polygon_coords:
            converted_polygon = []
            for p_lat, p_lon in polygon_coords:
                if isinstance(p_lat, str):
                    p_lat = self._parse_coordinate(str(p_lat))
                if isinstance(p_lon, str):
                    p_lon = self._parse_coordinate(str(p_lon))
                # Validate each polygon coordinate
                self._validate_coordinates(p_lat, p_lon)
                converted_polygon.append((p_lat, p_lon))
            polygon_coords = converted_polygon

        if polygon_coords:
            if show_logs:
                self.logger.info("\nSearching in polygon area")
        else:
            if not all([lat, lon, radius]):
                raise OSMSearchError("Must provide either polygon_coords or (lat, lon, radius)")
            if show_logs:
                self.logger.info(f"\nSearching at {lat}, {lon} with {radius} mile radius")

        # Determine which tags to use
        search_tags = []
        if use_default_tags:
            search_tags.extend(self.tags)
        if custom_tags:
            search_tags.extend(custom_tags)
            
        if not search_tags:
            raise OSMSearchError("No tags to search for. Enable default tags or provide custom tags.")

        # Convert radius to meters for API
        radius_meters = int(radius * 1609.34) if radius else None

        results = []
        node_cache = {}

        try:
            for tag in search_tags:
                if show_logs:
                    self.logger.info(f"\nQuerying for tag: {tag}")

                # Build area filter based on search type
                if polygon_coords:
                    # Format points for Overpass API: lat1 lon1 lat2 lon2 lat3 lon3 ...
                    points_str = " ".join(f"{lat} {lon}" for lat, lon in polygon_coords)
                    area_filter = f"(poly:'{points_str}')"
                else:
                    area_filter = f"(around:{radius_meters},{lat},{lon})"

                # Build a single query combining all tag patterns
                if '=' in tag:
                    # Exact match (e.g., building=ruins)
                    tag_key, tag_value = tag.split('=', 1)
                    query = f"""
                    [out:json][timeout:{self.timeout}];
                    (
                      node["{tag_key}"="{tag_value}"]{area_filter};
                      way["{tag_key}"="{tag_value}"]{area_filter};
                    );
                    out body;
                    >;
                    out skel qt;
                    """
                else:
                    # Simple tag (e.g., abandoned)
                    tag_key = tag.replace('"', '\\"')  # Escape quotes
                    query = f"""
                    [out:json][timeout:{self.timeout}];
                    (
                      // Match as key with any value
                      node["{tag_key}"]{area_filter};
                      way["{tag_key}"]{area_filter};
                      // Match as value in common keys
                      node["building"="{tag_key}"]{area_filter};
                      way["building"="{tag_key}"]{area_filter};
                      node["historic"="{tag_key}"]{area_filter};
                      way["historic"="{tag_key}"]{area_filter};
                    );
                    out body;
                    >;
                    out skel qt;
                    """

                if show_logs:
                    self.logger.debug(f"Query:\n{query}")
                    self.logger.info("Sending query to Overpass API...")

                # Send request
                data = self._send_overpass_query(query)

                if show_logs:
                    self.logger.info("Processing results...")

                # Cache nodes first
                if show_logs:
                    self.logger.info(f"Found {len(data.get('elements', []))} elements")
                
                for element in data.get('elements', []):
                    if element['type'] == 'node':
                        node_cache[element['id']] = (element['lat'], element['lon'])

                # Process results
                locations_found = 0
                for element in data.get('elements', []):
                    if 'tags' not in element:
                        continue

                    # Skip if location should be excluded based on tags
                    if self._should_exclude_location(element['tags']):
                        continue

                    # Get coordinates
                    if element['type'] == 'node':
                        result_lat = element['lat']
                        result_lon = element['lon']
                    elif element['type'] == 'way':
                        # Calculate center of way
                        way_nodes = [node_cache[n] for n in element['nodes'] if n in node_cache]
                        if not way_nodes:
                            continue
                        result_lat = sum(n[0] for n in way_nodes) / len(way_nodes)
                        result_lon = sum(n[1] for n in way_nodes) / len(way_nodes)
                    else:
                        continue

                    # Calculate distance
                    distance = self.calculate_distance((lat, lon), (result_lat, result_lon))

                    # Calculate road distance
                    road_distance = self.get_nearest_road_distance(result_lat, result_lon)

                    # Create result object
                    result = LocationResult(
                        name=self.get_location_name(result_lat, result_lon, element['tags']),
                        latitude=result_lat,
                        longitude=result_lon,
                        distance=distance,
                        road_distance=road_distance,
                        tags=element['tags'],
                        osm_id=str(element['id']),
                        type=element['type'],
                        elevation=self.get_elevation(result_lat, result_lon)
                    )

                    # Only add if not already present
                    if not any(r.osm_id == result.osm_id for r in results):
                        results.append(result)
                        locations_found += 1

                if show_logs:
                    self.logger.info(f"Added {locations_found} new locations for tag {tag}")

            # Sort results based on sort_by parameter
            if show_logs:
                self.logger.info(f"\nFound total of {len(results)} unique locations")
                self.logger.info("Sorting results...")
                
            if sort_by == 'distance':
                results.sort(key=lambda x: x.distance if x.distance is not None else float('inf'))
            elif sort_by == 'name':
                results.sort(key=lambda x: x.name)
            else:
                raise OSMSearchError(f"Invalid sort_by value: {sort_by}. Must be 'distance' or 'name'")

            # Group results with fixed 100 meter distance
            if show_logs:
                self.logger.info("Grouping nearby locations...")
                
            grouped_results = self.group_locations(results)
            
            # Convert to LocationGroup objects
            grouped_results = [LocationGroup(group) for group in grouped_results]

            if show_logs:
                self.logger.info(f"Created {len(grouped_results)} location groups")
                for i, group in enumerate(grouped_results, 1):
                    self.logger.info(f"Group {i}: {len(group)} locations")

            return grouped_results

        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            raise 

    def group_locations(self, locations: List[LocationResult]) -> List[List[LocationResult]]:
        """
        Group locations that are within 100 meters of each other
        
        Args:
            locations: List of LocationResult objects to group
            
        Returns:
            List of location groups, where each group is a list of LocationResult objects
        """
        if not locations:
            return []
        
        # Sort locations by distance from search center
        sorted_locations = sorted(locations, 
                                key=lambda x: x.distance if x.distance is not None else float('inf'))
        
        # Initialize groups
        groups = []
        unassigned = set(range(len(sorted_locations)))
        
        while unassigned:
            # Start new group with first unassigned location
            current = min(unassigned)
            current_group = {current}
            unassigned.remove(current)
            
            # Keep track of which locations we need to check
            to_check = {current}
            
            # Keep expanding group until no more nearby locations found
            while to_check:
                check_idx = to_check.pop()
                check_loc = sorted_locations[check_idx]
                
                # Look for nearby unassigned locations
                for other_idx in list(unassigned):
                    other_loc = sorted_locations[other_idx]
                    
                    # Calculate distance between locations
                    try:
                        if None in (check_loc.latitude, check_loc.longitude, 
                                  other_loc.latitude, other_loc.longitude):
                            continue
                            
                        dist = geopy.distance.geodesic(
                            (check_loc.latitude, check_loc.longitude),
                            (other_loc.latitude, other_loc.longitude)
                        ).meters
                        
                        # If within 100 meters, add to current group
                        if dist is not None and dist <= 100:  # Fixed 100 meter grouping distance
                            current_group.add(other_idx)
                            unassigned.remove(other_idx)
                            to_check.add(other_idx)
                    except Exception:
                        continue
            
            # Convert indices back to LocationResult objects and add group
            groups.append([sorted_locations[i] for i in sorted(current_group)])
        
        # Sort groups by size (largest first) and then by minimum distance
        def safe_min_distance(group):
            distances = [x.distance for x in group if x.distance is not None]
            return min(distances) if distances else float('inf')
            
        groups.sort(key=lambda g: (-len(g), safe_min_distance(g)))
        
        return groups

    def get_nearest_road_distance(self, lat: float, lon: float) -> Optional[float]:
        """Get shortest distance from point to any nearby road in meters"""
        try:
            # Query for nearby roads within 1km radius
            query = f"""
            [out:json][timeout:30];
            (
              way["highway"]["highway"!~"path|footway|cycleway|steps|corridor|elevator|escalator|proposed|construction"]
                (around:1000,{lat},{lon});
            );
            out body;
            >;
            out skel qt;
            """
            
            data = self._send_overpass_query(query)
            
            if not data.get('elements'):
                return None
                
            # Cache nodes
            node_cache = {}
            for element in data.get('elements', []):
                if element['type'] == 'node':
                    node_cache[element['id']] = (element['lat'], element['lon'])
            
            min_distance = float('inf')
            # Check each road
            for element in data.get('elements', []):
                if element['type'] == 'way' and 'nodes' in element:
                    # Get road nodes
                    road_nodes = [node_cache[n] for n in element['nodes'] if n in node_cache]
                    if len(road_nodes) < 2:
                        continue
                        
                    # Check each segment of the road
                    for i in range(len(road_nodes) - 1):
                        start = road_nodes[i]
                        end = road_nodes[i + 1]
                        
                        # Calculate distance to this segment
                        dist = self._point_to_line_distance((lat, lon), start, end)
                        if dist is not None and dist < min_distance:
                            min_distance = dist
            
            return min_distance if min_distance != float('inf') else None
            
        except Exception as e:
            self.logger.debug(f"Failed to get road distance: {e}")
            return None
            
    def _point_to_line_distance(self, point: Tuple[float, float], 
                              line_start: Tuple[float, float], 
                              line_end: Tuple[float, float]) -> Optional[float]:
        """Calculate shortest distance from point to line segment in meters"""
        # Check for None values and validate inputs
        if (point is None or line_start is None or line_end is None or
            len(point) != 2 or len(line_start) != 2 or len(line_end) != 2):
            return None
            
        try:
            lat, lon = point
            lat1, lon1 = line_start
            lat2, lon2 = line_end
            
            # Validate all coordinates are numbers
            coords = [lat, lon, lat1, lon1, lat2, lon2]
            if not all(isinstance(x, (int, float)) for x in coords):
                return None
            if any(x is None for x in coords):
                return None
            
            # Convert to meters (rough approximation)
            meters_per_degree = 111319.9  # at equator
            
            try:
                x = float((lon - lon1) * meters_per_degree * np.cos(np.radians(float(lat))))
                y = float((lat - lat1) * meters_per_degree)
                
                dx = float((lon2 - lon1) * meters_per_degree * np.cos(np.radians(float(lat))))
                dy = float((lat2 - lat1) * meters_per_degree)
                
                # Length of line segment
                line_length = float(np.sqrt(dx*dx + dy*dy))
                if line_length == 0:
                    return float(np.sqrt(x*x + y*y))
                    
                # Project point onto line
                t = float(max(0, min(1, (x*dx + y*dy) / (line_length*line_length))))
                
                # Get closest point on line segment
                proj_x = float(t * dx)
                proj_y = float(t * dy)
                
                # Calculate and return distance
                return float(np.sqrt((x - proj_x)**2 + (y - proj_y)**2))
            except (TypeError, ValueError):
                return None
                
        except Exception:
            return None 