from flask import Flask, render_template, request
import pandas as pd
import geopandas as gpd
import keplergl

app = Flask(__name__)

@app.route('/input')
def input():
    return render_template('input.html')

@app.route('/result')
def result():

    # Load the GeoJSON file
    gdf = gpd.read_file('synthetic_data_full.geojson')

    # Create a Kepler.gl map
    map_1 = keplergl.KeplerGl(height=800)
    map_1.add_data(data=gdf, name='synthetic_data')

    # Save the map to an HTML file
    map_1.save_to_html(file_name='templates/synthetic_data_map.html')

    return render_template('synthetic_data_map.html')

if __name__ == '__main__':
    app.run(debug=True)