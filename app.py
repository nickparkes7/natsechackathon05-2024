from flask import Flask, render_template, request
import pandas as pd
import geopandas as gpd
from frechetdist import frdist
import keplergl

app = Flask(__name__)

def get_frechet(df, flight_id):
    flight_coords = df[df['UniqueFlightId'] == int(flight_id)][['DetectionLatitude', 'DetectionLongitude']].to_records(index=False).tolist()

    similarity_dict = {}
    for unique_flight_id in df['UniqueFlightId'].unique():
        if unique_flight_id == flight_id:
            continue
        other_coords = df[df['UniqueFlightId'] == int(unique_flight_id)][['DetectionLatitude', 'DetectionLongitude']].to_records(index=False).tolist()
        distance = frdist(flight_coords, other_coords)
        similarity_dict[unique_flight_id] = distance
        print(f"Distance between {flight_id} and {unique_flight_id}: {distance}")
    return [key for key, distance in similarity_dict.items() if distance < 0.01]

@app.route('/input')
def input():
    return render_template('input.html')

@app.route('/similarity')
def similarity():
    return render_template('similarity.html')

@app.route('/result', methods=['POST'])
def result():
    min_lat = request.form['min_lat']
    max_lat = request.form['max_lat']
    min_lon = request.form['min_lon']
    max_lon = request.form['max_lon']
    min_timestamp = request.form['min_timestamp']
    max_timestamp = request.form['max_timestamp']

    df = pd.read_csv('synthetic_data_full.csv')

    # Filter the DataFrame based on the input values
    filtered_df = df[
        (df['DetectionLatitude'] >= float(min_lat)) &
        (df['DetectionLatitude'] <= float(max_lat)) &
        (df['DetectionLongitude'] >= float(min_lon)) &
        (df['DetectionLongitude'] <= float(max_lon)) &
        (df['SensorTime'] >= min_timestamp) &
        (df['SensorTime'] <= max_timestamp)
    ]

    # get unique flight ids in filtered_df
    flight_ids = filtered_df['UniqueFlightId'].unique()

    df = df[df['UniqueFlightId'].isin(flight_ids)]

    # Create a GeoDataFrame from the filtered DataFrame
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['DetectionLongitude'], df['DetectionLatitude']))

    # Create a Kepler.gl map
    map_1 = keplergl.KeplerGl(height=800)
    map_1.add_data(data=gdf, name='synthetic_data')

    # Save the map to an HTML file
    map_1.save_to_html(file_name='templates/synthetic_data_map.html')

    return render_template('synthetic_data_map.html')

@app.route('/similarpaths', methods=['POST'])
def similarpaths():
    flight_id = request.form['flight_id_query']

    df = pd.read_csv('synthetic_data_full.csv')
    
    closest_flight_path_ids = get_frechet(df, flight_id)

    # Filter the DataFrame based on the input values
    df = df[
        (df['UniqueFlightId'].isin(closest_flight_path_ids))
    ]

    # Create a GeoDataFrame from the filtered DataFrame
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['DetectionLongitude'], df['DetectionLatitude']))

    # Create a Kepler.gl map
    map_1 = keplergl.KeplerGl(height=800)
    map_1.add_data(data=gdf, name='synthetic_data')

    # Save the map to an HTML file
    map_1.save_to_html(file_name='templates/synthetic_data_map.html')

    return render_template('synthetic_data_map.html')

if __name__ == '__main__':
    app.run(debug=True)