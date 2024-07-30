import csv
import os
import random
import time

import geopandas as gpd
import numpy as np
import pandas as pd
from memory_profiler import memory_usage
from rdp import rdp
from shapely.geometry import LineString, MultiPoint
from simplification.cutil import simplify_coords_vw  # Visvalingam-Whyatt
from tsmoothie.smoother import LowessSmoother


# Function to create synthetic flight paths data with sine waves
def create_flight_paths(num_points, num_paths):
    """
    Generates synthetic flight path data using sine waves with added Gaussian noise.
    This creates a realistic but controlled dataset for testing subsampling algorithms.

    Parameters:
    num_points (int): Number of points per flight path.
    num_paths (int): Number of flight paths to generate.

    Returns:
    list: A list of Pandas DataFrames, each representing a synthetic flight path.
    """
    datasets = []
    for i in range(num_paths):
        x = np.linspace(-3000000, 3000000, num_points)  # Generate x-coordinates over a large range
        y = np.sin(x / 100000) * 3000000 + np.random.normal(0, 100000, num_points)  # Generate y-coordinates with sine wave and noise
        df = pd.DataFrame({'ps71_easting': x, 'ps71_northing': y})
        # Add metadata columns to simulate real-world flight path data
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
    """
    Saves each synthetic dataset to a separate CSV file.

    Parameters:
    datasets (list): A list of Pandas DataFrames to save.

    Returns:
    list: A list of file paths to the saved CSV files.
    """
    csv_filepaths = []
    for i, df in enumerate(datasets, start=1):
        csv_filepath = f'synthetic_data_{i}.csv'
        df.to_csv(csv_filepath, index=False)  # Save DataFrame to CSV without row index
        csv_filepaths.append(csv_filepath)
        print(f"Saved {csv_filepath}")
    return csv_filepaths

# Function for Uniform Subsampling
def uniform_subsampling(coords, step):
    """
    Selects every nth point from the dataset for uniform subsampling.

    Parameters:
    coords (list): List of coordinate tuples.
    step (int): Step size for subsampling.

    Returns:
    list: Subsampled coordinates.
    """
    return coords[::step]

# Function for Random Sampling
def random_subsampling(coords, n_out):
    """
    Randomly selects a specified number of points from the dataset.

    Parameters:
    coords (list): List of coordinate tuples.
    n_out (int): Number of points to select.

    Returns:
    list: Randomly subsampled coordinates.
    """
    return random.sample(coords, min(n_out, len(coords)))

# Function for Sliding Window Subsampling
def sliding_window_subsampling(coords, window_size):
    """
    Selects the middle point of each window of specified size.

    Parameters:
    coords (list): List of coordinate tuples.
    window_size (int): Size of the sliding window.

    Returns:
    list: Subsampled coordinates.
    """
    subsampled_coords = []
    for i in range(0, len(coords), window_size):
        window = coords[i:i + window_size]
        if window:
            subsampled_coords.append(window[len(window) // 2])  # Choose the middle point in the window
    return subsampled_coords

# Function for Grid-based Subsampling
def grid_subsampling(coords, grid_size):
    """
    Selects one point per grid cell based on the specified grid size.

    Parameters:
    coords (list): List of coordinate tuples.
    grid_size (int): Size of the grid cells.

    Returns:
    list: Subsampled coordinates.
    """
    grid_coords = []
    grid_dict = {}
    for coord in coords:
        grid_key = (round(coord[0] / grid_size) * grid_size, round(coord[1] / grid_size) * grid_size)  # Calculate grid cell key
        if grid_key not in grid_dict:
            grid_dict[grid_key] = coord
    grid_coords = list(grid_dict.values())
    return grid_coords

# Function for Lowess Smoothing Subsampling
def lowess_subsampling(coords, frac):
    """
    Applies Lowess smoothing and selects points based on the smoothing fraction.

    Parameters:
    coords (list): List of coordinate tuples.
    frac (float): Smoothing fraction for Lowess algorithm.

    Returns:
    list: Smoothed coordinates.
    """
    x = np.array([coord[0] for coord in coords])
    y = np.array([coord[1] for coord in coords])
    smoother = LowessSmoother(smooth_fraction=frac, iterations=1)
    smoother.smooth(y)
    return list(zip(x, smoother.smooth_data[0]))

# Function for Visvalingam-Whyatt Algorithm
def visvalingam_whyatt_subsampling(coords, tolerance):
    """
    Simplifies the geometry by removing points with the least perceptible change using the Visvalingam-Whyatt algorithm.

    Parameters:
    coords (list): List of coordinate tuples.
    tolerance (float): Tolerance for simplification.

    Returns:
    list: Simplified coordinates.
    """
    return simplify_coords_vw(coords, tolerance)

# Wrapper function for saving GeoDataFrame to file
def to_file_wrapper(gdf, filepath, layer_name):
    """
    Wrapper function to save GeoDataFrame to a file, used for profiling.

    Parameters:
    gdf (GeoDataFrame): GeoDataFrame to save.
    filepath (str): File path to save the GeoDataFrame.
    layer_name (str): Name of the layer in the GeoPackage.
    """
    gdf.to_file(filepath, layer=layer_name, driver="GPKG", if_exists='replace')

# Function to process data and create GeoPackage
def process_data(csv_filepath, gpkg_filepath, subsample_levels):
    """
    Processes the synthetic data, applies subsampling algorithms, and saves the results to a GeoPackage.
    Also profiles memory usage, duration, and file size.

    Parameters:
    csv_filepath (str): File path to the CSV file containing the synthetic data.
    gpkg_filepath (str): File path to the GeoPackage to save the subsampled data.
    subsample_levels (list): List of levels for subsampling.

    Returns:
    list: Profiling results for each subsampling method.
    """
    data = pd.read_csv(csv_filepath)
    coords = data[['ps71_easting', 'ps71_northing']].values.tolist()

    # Initialize GeoDataFrames for each subsampling method
    gdfs = {
        'rdp': gpd.GeoDataFrame(columns=["geometry"]),
        'uniform': gpd.GeoDataFrame(columns=["geometry"]),
        'random': gpd.GeoDataFrame(columns=["geometry"]),
        'sliding_window': gpd.GeoDataFrame(columns=["geometry"]),
        'grid': gpd.GeoDataFrame(columns=["geometry"]),
        'lowess': gpd.GeoDataFrame(columns=["geometry"]),
        'vw': gpd.GeoDataFrame(columns=["geometry"]),
        'full': gpd.GeoDataFrame(columns=["geometry"])
    }

    # Add full resolution data as MultiPoint
    points_full = MultiPoint(coords)
    gdfs['full'] = pd.concat([gdfs['full'], gpd.GeoDataFrame([[points_full]], columns=["geometry"])], ignore_index=True)

    # Apply each subsampling algorithm at different levels
    for level in subsample_levels:
        subsampled_coords_rdp = rdp(coords, epsilon=level)
        subsampled_coords_uniform = uniform_subsampling(coords, level)
        subsampled_coords_random = random_subsampling(coords, level)
        subsampled_coords_sliding_window = sliding_window_subsampling(coords, level)
        subsampled_coords_grid = grid_subsampling(coords, level)
        smooth_frac = min(max(level / 1000.0, 0.01), 0.99)  # Ensure smooth_fraction is within (0,1)
        subsampled_coords_lowess = lowess_subsampling(coords, smooth_frac)
        subsampled_coords_vw = visvalingam_whyatt_subsampling(coords, level)

        # Create LineString for each subsampling method and add to corresponding GeoDataFrame
        if len(subsampled_coords_rdp) > 1:
            line_rdp = LineString(subsampled_coords_rdp)
            gdfs['rdp'] = pd.concat([gdfs['rdp'], gpd.GeoDataFrame([[line_rdp]], columns=["geometry"])], ignore_index=True)
        if len(subsampled_coords_uniform) > 1:
            line_uniform = LineString(subsampled_coords_uniform)
            gdfs['uniform'] = pd.concat([gdfs['uniform'], gpd.GeoDataFrame([[line_uniform]], columns=["geometry"])], ignore_index=True)
        if len(subsampled_coords_random) > 1:
            line_random = LineString(subsampled_coords_random)
            gdfs['random'] = pd.concat([gdfs['random'], gpd.GeoDataFrame([[line_random]], columns=["geometry"])], ignore_index=True)
        if len(subsampled_coords_sliding_window) > 1:
            line_sliding_window = LineString(subsampled_coords_sliding_window)
            gdfs['sliding_window'] = pd.concat([gdfs['sliding_window'], gpd.GeoDataFrame([[line_sliding_window]], columns=["geometry"])], ignore_index=True)
        if len(subsampled_coords_grid) > 1:
            line_grid = LineString(subsampled_coords_grid)
            gdfs['grid'] = pd.concat([gdfs['grid'], gpd.GeoDataFrame([[line_grid]], columns=["geometry"])], ignore_index=True)
        if len(subsampled_coords_lowess) > 1:
            line_lowess = LineString(subsampled_coords_lowess)
            gdfs['lowess'] = pd.concat([gdfs['lowess'], gpd.GeoDataFrame([[line_lowess]], columns=["geometry"])], ignore_index=True)
        if len(subsampled_coords_vw) > 1:
            line_vw = LineString(subsampled_coords_vw)
            gdfs['vw'] = pd.concat([gdfs['vw'], gpd.GeoDataFrame([[line_vw]], columns=["geometry"])], ignore_index=True)

    # Save each GeoDataFrame to the GeoPackage and profile memory and duration
    profiling_results = []
    for method, gdf in gdfs.items():
        gdf.crs = "EPSG:3031"  # Set Coordinate Reference System to Antarctic Polar Stereographic
        layer_name = f'{method}_synthetic_layer'

        start_time = time.time()
        mem_usage = memory_usage((to_file_wrapper, (gdf, gpkg_filepath, layer_name)), interval=0.1)
        duration = time.time() - start_time
        file_size = os.path.getsize(gpkg_filepath) / (1024 * 1024)  # Convert file size to MB

        profiling_results.append({
            'method': method,
            'peak_memory_usage_mb': max(mem_usage),
            'duration_sec': duration,
            'file_size_mb': file_size
        })

        print(f"Added {layer_name} with peak memory usage: {max(mem_usage)} MB, duration: {duration} sec, file size: {file_size} MB")

    return profiling_results

# Function to add synthetic data to GeoPackage
def add_synthetic_data_to_gpkg(gpkg_filepath, csv_filepaths, subsample_levels):
    """
    Processes each CSV file to add synthetic data to the GeoPackage.

    Parameters:
    gpkg_filepath (str): File path to the GeoPackage.
    csv_filepaths (list): List of file paths to the CSV files containing the synthetic data.
    subsample_levels (list): List of levels for subsampling.

    Returns:
    list: Aggregated profiling results for each subsampling method.
    """
    profiling_results = []
    for csv_filepath in csv_filepaths:
        results = process_data(csv_filepath, gpkg_filepath, subsample_levels)
        profiling_results.extend(results)
    return profiling_results

# Save profiling results to a CSV file
def save_profiling_results(profiling_results, filename):
    """
    Saves the profiling results (memory usage, duration, file size) to a CSV file.

    Parameters:
    profiling_results (list): List of profiling results for each subsampling method.
    filename (str): File path to save the profiling results.
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['method', 'peak_memory_usage_mb', 'duration_sec', 'file_size_mb'])
        writer.writeheader()
        for result in profiling_results:
            writer.writerow(result)

if __name__ == "__main__":
    num_points = 10000  # Number of points per flight path
    num_paths = 5  # Number of flight paths to generate
    datasets = create_flight_paths(num_points, num_paths)  # Generate synthetic flight paths
    csv_filepaths = save_csv_files(datasets)  # Save flight paths to CSV files

    gpkg_filepath = 'synthetic_data.gpkg'  # File path for the GeoPackage
    subsample_levels = [10, 100, 1000]  # Three levels of subsampling for different zoom levels

    profiling_results = add_synthetic_data_to_gpkg(gpkg_filepath, csv_filepaths, subsample_levels)  # Process data and save to GeoPackage

    save_profiling_results(profiling_results, 'detailed_profiling_results.csv')  # Save profiling results to CSV
    print("Detailed profiling results saved to detailed_profiling_results.csv")
