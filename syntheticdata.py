import math
import multiprocessing
import os
import random

import geopandas as gpd
import numpy as np
import pandas as pd
from rdp import rdp
from shapely.geometry import LineString, MultiPoint


# Function to create a complex wave with slight variations in Antarctic coordinates
def create_complex_wave(num_points, phase_shift, noise_factor=0.01):
    x = np.linspace(-3000000, 3000000, num_points)  # Example easting values within the Antarctic region
    y = -3000000 + 1000 * (np.random.uniform(1 - noise_factor, 1 + noise_factor, num_points) * (
        np.sin(x / 1000 + phase_shift) +
        np.sin(x / 500 + phase_shift) * 0.5 +
        np.sin(x / 2000 + phase_shift) * 0.25
    ))
    return x, y

# Generate multiple synthetic flight paths with different patterns
def generate_datasets(num_points, num_paths):
    datasets = []
    for i in range(num_paths):
        x, y = create_complex_wave(num_points, phase_shift=i * 0.1)
        df = pd.DataFrame({'ps71_easting': x, 'ps71_northing': y})
        df['institution'] = 'SYNTHETIC'
        df['region'] = 'antarctic'
        df['campaign'] = f'2023_Synthetic_Campaign_{i+1}'
        df['segment'] = f'20230101_0{i+1}'
        df['granule'] = f'Data_20230101_0{i+1}_001'
        df['availability'] = 's'
        df['uri'] = None
        df['name'] = f'SYNTHETIC_2023_Synthetic_Campaign_{i+1}_Data_20230101_0{i+1}_001'
        datasets.append(df)
    return datasets

# Save each DataFrame to a separate CSV
def save_csv_files(datasets):
    csv_filepaths = []
    for i, df in enumerate(datasets, start=1):
        csv_filepath = f'synthetic_data_{i}.csv'
        df.to_csv(csv_filepath, index=False)
        csv_filepaths.append(csv_filepath)
        print(f"Saved {csv_filepath}")
    return csv_filepaths

# Function to process data and create GeoPackage
def process_data(gpkg_filepath, csv_filepath, subsample_levels):
    data = pd.read_csv(csv_filepath)
    coords = data[['ps71_easting', 'ps71_northing']].values.tolist()

    # Initialize GeoDataFrames for each zoom level and multipoints
    gdfs = {level: gpd.GeoDataFrame(columns=["geometry"]) for level in subsample_levels}
    gdf_multipoint = gpd.GeoDataFrame(columns=["geometry"])

    # Add full resolution data to the highest level
    points_full = LineString(coords)
    gdfs[subsample_levels[-1]] = pd.concat([gdfs[subsample_levels[-1]], gpd.GeoDataFrame([[points_full]], columns=["geometry"])], ignore_index=True)

    # Subsampled levels
    for level in subsample_levels[:-1]:
        subsampled_coords = rdp(coords, epsilon=level)
        points = LineString(subsampled_coords)
        gdfs[level] = pd.concat([gdfs[level], gpd.GeoDataFrame([[points]], columns=["geometry"])], ignore_index=True)

    # Add MultiPoint layer
    multipoints = MultiPoint(coords)
    gdf_multipoint = pd.concat([gdf_multipoint, gpd.GeoDataFrame([[multipoints]], columns=["geometry"])], ignore_index=True)

    # Save each GeoDataFrame to the GeoPackage with the OVERWRITE=YES option
    for level, gdf in gdfs.items():
        gdf.crs = "EPSG:3031"
        layer_name = f'zoom_level_{level}.synthetic_layer'
        try:
            gdf.to_file(gpkg_filepath, layer=layer_name, driver="GPKG", layerCreationOptions=["OVERWRITE=YES"])
            print(f"Added layer: {layer_name}")
        except Exception as e:
            print(f"Error adding layer {layer_name}: {e}")

    # Save the MultiPoint layer
    gdf_multipoint.crs = "EPSG:3031"
    try:
        gdf_multipoint.to_file(gpkg_filepath, layer="zoom_level_multipoint.synthetic_layer", driver="GPKG", layerCreationOptions=["OVERWRITE=YES"])
        print(f"Added layer: zoom_level_multipoint.synthetic_layer")
    except Exception as e:
        print(f"Error adding layer zoom_level_multipoint.synthetic_layer: {e}")

# Function to add synthetic data to GeoPackage with parallel processing
def add_synthetic_data_to_gpkg_parallel(gpkg_filepath, csv_filepaths, subsample_levels):
    # Remove the existing GeoPackage if it exists
    if os.path.exists(gpkg_filepath):
        os.remove(gpkg_filepath)
        print(f"Removed existing file: {gpkg_filepath}")

    # Use multiprocessing to handle data processing in parallel
    with multiprocessing.Pool() as pool:
        pool.starmap(process_data, [(gpkg_filepath, csv_filepath, subsample_levels) for csv_filepath in csv_filepaths])

if __name__ == '__main__':
    # Example usage
    num_points = 10000  # 1 million points for testing
    num_paths = 5  # Create 5 paths for a more extensive test
    datasets = generate_datasets(num_points, num_paths)
    csv_filepaths = save_csv_files(datasets)

    gpkg_filepath = 'synthetic_data.gpkg'
    subsample_levels = [10, 100, 1000]  # Three levels of subsampling
    add_synthetic_data_to_gpkg_parallel(gpkg_filepath, csv_filepaths, subsample_levels)

    print(f"GeoPackage created: {gpkg_filepath}")
