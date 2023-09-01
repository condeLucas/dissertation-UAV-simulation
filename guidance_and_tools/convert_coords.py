import pyproj

def convert_coordinate(lon, lat):
    # Convert from EPSG:4326 to EPSG:3857 (Web Mercator)
    dst_proj = pyproj.Proj('epsg:3857')

    # Convert from EPSG:3857 to UTM
    # To find UTM zone
    # utm_zone = int((lon + 180) / 6) + 1 if lat >= 0 else int((lon + 180) / 6) + 31
    # print(f"UTM zone:{utm_zone}\n")
    # # src_proj = pyproj.Proj('epsg:3857')
    dst_proj = pyproj.Proj(f"+proj=utm +zone=32 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    # easting, northing = pyproj.transform(src_proj, dst_proj, lon, lat)
    easting, northing = dst_proj(lon, lat)

    # Add displacement
    easting += 150
    northing += 112
    
    # Convert back to EPSG:4326
    # src_proj = pyproj.Proj("+proj=utm +zone=32 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    # dst_proj = pyproj.Proj('epsg:5555')
    # x, y = pyproj.transform(src_proj, dst_proj, easting, northing)
    lon, lat = dst_proj(easting, northing, inverse=True)

    return lon, lat

# Coordinate in GPS (EPSG:4326)
lon = 7.33577
lat = 51.43672

# Convert to EPSG:3857
x, y = convert_coordinate(lon, lat)

print(f"EPSG:4326 - lon: {x}, lat: {y}")