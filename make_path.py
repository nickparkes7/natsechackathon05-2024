# path = {
#     "type": "Polygon",
#     "coordinates": [
#         [
#             [-122.42254774828349, 37.8264234543935],
#             [-122.40359625414386, 37.7873913304346],
#             [-122.37452503012375, 37.82954803953667],
#             [-122.42254774828349, 37.8264234543935],
#         ]
#     ],
# }
import geopandas as gpd
from shapely.geometry import LineString

# Coordinates for 6th and Market, Treasure Island, and Alcatraz
coords = [
    (37.7749, -122.4194),  # 6th and Market
    (37.8230, -122.3708),  # Treasure Island
    (37.8267, -122.4233)   # Alcatraz
]

# chatgpt and kepler need some help to get along
for i, v in enumerate(coords):
    coords[i] = v[1], v[0]

# Create a LineString geometry
line = LineString(coords)

# Generate 50 points along the line
curved_line = [line.interpolate(i / 50, normalized=True) for i in range(51)]

# Create a GeoDataFrame from the curved line
gdf = gpd.GeoDataFrame(geometry=curved_line, crs="EPSG:4326")

# Convert to GeoJSON format
geojson_str = gdf.to_json()

print(geojson_str)

# Save the GeoJSON string to a file
with open('drug.geojson', 'w') as f:
    f.write(geojson_str)