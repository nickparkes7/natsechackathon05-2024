import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import open3d as o3d
from shapely import LineString
from shapely.geometry import Point
from typing import List, Dict, Any, Tuple
import os
from frechetdist import frdist
import numpy as np


def get_record(db: pd.DataFrame, id: int) -> List[Tuple[int, int]]:
    return db[db['UniqueFlightId'] == id][['DetectionLatitude', 'DetectionLongitude']].to_records(index=False).tolist()


def down_sample_list(l: List[Tuple[int, int]], n: int) -> List[Tuple[int, int]]:
    assert n != 0

    sample_factor = len(l) // n
    return [l[i * sample_factor] for i in range(n)]


def similarity(a: List[Tuple[int, int]], b: List[Tuple[int, int]]) -> float:
    """
    Calculate the similarity between two lists of coordinates with Frechet distance by first downsampling the larger
    list into the same size
    """
    largest = None
    smallest = None
    if len(a) > len(b):
        largest = a
        smallest = b
    else:
        largest = b
        smallest = a

    assert len(largest) != 0
    assert len(smallest) != 0

    largest = down_sample_list(largest, n=len(smallest))
    return frdist(largest, smallest)


def query(db: pd.DataFrame, flight_id: int) -> Dict[str, Any]:
    id_record = get_record(db, flight_id)

    results: List[Tuple[int, float]] = []
    all_fid = db['UniqueFlightId'].unique()
    print("All flight ids")
    print(all_fid)
    for fid in all_fid:
        if flight_id == fid:
            continue

        other_record = get_record(db, fid)
        print(other_record)
        distance = similarity(id_record, other_record)
        results.append((fid, distance))

    # Sort results in ascending order by distance
    sorted_results = sorted(results, key=lambda x: x[1])

    formatted_results = [{
        "UniqueFlightId": result[0],
        "Similarity": result[1]
    } for result in sorted_results]

    return formatted_results


def get_df(name: str) -> pd.DataFrame:
    df = pd.read_csv(name)

    df['SensorTime'] = pd.to_datetime(df['SensorTime'], format='mixed')

    # Get unique drone IDs
    drone_ids = df['DroneId'].unique()

    print(len(drone_ids), " unique drone ids")

    # Loop through each drone ID and assign a flight number to each unique flight
    for drone_id in drone_ids:
        # Filter the dataframe for the current drone ID
        filtered_df = df[df['DroneId'] == drone_id]

        # sort filtered_df by SensorTime
        filtered_df = filtered_df.sort_values('SensorTime')

        # Convert the SensorTime column to numpy array
        timestamps = filtered_df['SensorTime'].values

        # Calculate the time differences between consecutive timestamps
        time_diff = np.diff(timestamps)

        # Find the indices where the time difference is greater than 30 minutes
        split_indices = np.where(time_diff > np.timedelta64(20, 'm'))[0] + 1

        # Assign flight IDs based on the split indices
        flight_ids = np.zeros(len(timestamps), dtype=int)
        current_flight_id = 1
        for idx in split_indices:
            flight_ids[idx:] = current_flight_id
            current_flight_id += 1

        # Add the flight_ids column to the DataFrame
        filtered_df['FlightNum'] = flight_ids
        df.loc[filtered_df.index, 'FlightNum'] = filtered_df['FlightNum']

    # Create a new column called UniqueFlightId by concatenating DroneId and FlightNum
    df['UniqueFlightId'] = df['DroneId'] + '_' + df['FlightNum'].astype(int).astype(str)

    # Loop through each flight ID
    flight_ids = df['UniqueFlightId'].unique()

    # for flight_id in flight_ids:
    #     # Filter the dataframe for the current flight ID
    #     filtered_df_flight = df[df['UniqueFlightId'] == flight_id]
    #
    #     if len(filtered_df_flight) < 100:
    #         df = df.drop(filtered_df_flight.index)
    #         continue
    return df


if __name__ == "__main__":
    fpath = 'synthetic_data_full.csv'
    db = get_df(fpath)
    # print(query(db, flight_id=1))

    # for every flight id, asser that the length is not zero
    flights =db['UniqueFlightId'].unique()
    for f in flights:
        assert len(get_record(db, f)) > 0

    x = get_record(db, 1)
    y = get_record(db, 1)
    assert similarity(x, y) == 0
