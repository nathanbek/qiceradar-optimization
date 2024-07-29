# GeoPackage Creation and Styling

## radar_wrangler Repository Information

- **repo logo**
- **radar_wrangler**
- **qiceradar**
- **Language**: Jupyter Notebook
- **Created**: 11/03/2022
- **Last updated**: 07/08/2024
- **License**: BSD 3-Clause "New" or "Revised"
- **Software Version**: u-0.0.1Basic
- **Generated from Commit**: be70b3
- **Generated on**: 07/24/2024

### Architecture Diagram for radar_wrangler

The radar_wrangler repository provides tools for downloading, indexing, and processing radar data from various Antarctic research institutions. It solves the problem of managing and organizing large amounts of radar data from different sources by providing a unified workflow for data acquisition, storage, and visualization.

The repository is organized into three main components:

1. **Data Download and Organization** (…/download)
2. **Data Indexing and GeoPackage Creation** (…/index)
3. **BEDMAP Data Processing** (…/data_exploration)

The data download component uses a GeoPackage database to store metadata about the downloaded files. It includes scripts for downloading data from institutions such as BAS, UTIG, AWI, NSIDC, and LDEO. The download process is handled by institution-specific scripts (e.g., download_bas.py, download_utig_tdr.py) that use various methods including web scraping, API calls, and command-line tools like wget.

Data indexing is performed using scripts in the …/index directory. Key steps in this process include:

- Extracting and subsampling radar flight paths using the Ramer-Douglas-Peucker (RDP) algorithm
- Creating a GeoPackage database to store the indexed tracks
- Styling the GeoPackage layers for visualization in QGIS

The BEDMAP data processing utilities in …/data_exploration provide functions for loading, subsampling, and analyzing BEDMAP datasets. Notable functions include:

- `load_bedmap_ll()` and `load_bedmap_xy_new()` for loading BEDMAP data in different coordinate systems
- `subsample_tracks_uniform()` for reducing data density
- `find_closest_bedmap()` for matching survey data to BEDMAP points
- `segment_indices()` and `segment_indices_gap()` for identifying contiguous sections of BEDMAP data

Key design choices in the repository include:

- Modular organization of scripts by institution and functionality
- Use of GeoPackage for efficient storage and retrieval of geospatial data
- Integration with QGIS for visualization through QLR files
- Emphasis on data deduplication and subsampling to manage large datasets efficiently

![image](https://github.com/user-attachments/assets/fcbe442e-894d-482e-b47d-bd36172bfcf5)


## References: code/index

### GeoPackage Creation

**Script: `create_geopackage_index.py`**

1. **Connect to GeoPackage**: Uses `sqlite3` to connect to the GeoPackage file.
2. **Extract Data**: Retrieves `ps71_easting` and `ps71_northing` columns from CSV files using `load_xy()`.
3. **Process Campaign Directories**: Adds campaign directories as single layers using `add_campaign_directory_gpkg()`.
4. **Handle Naming Conventions**: Manages different segment and granule naming conventions.
5. **Add CSV Files**: Incorporates individual CSV files into the GeoPackage using `add_csv_gpkg()`.
6. **Process Various Data Types**: Handles BEDMAP, radargram, and ice thickness data by institution and campaign.
7. **Special Case**: Adds SPRI data specifically.

![image](https://github.com/user-attachments/assets/9fed0c30-af4f-4e4f-9926-f9a9b3dd76d1)


### GeoPackage Styling

**Script: `style_geopackage_index.py`**

1. **Extract Information**: Retrieves campaign and institution information from the GeoPackage.
2. **Create QGIS Project**: Builds a QGIS project with a hierarchical structure for institutions and campaigns.
3. **Add and Style Layers**: Uses `add_campaign()` to style layers based on availability status:
   - Supported Campaigns: Blue
   - Available Campaigns: Grey
   - Unavailable Campaigns: Salmon
4. **Create Symbols**: Generates appropriate symbols for different geometry types (LINESTRING or MULTIPOINT).
5. **Set Coordinate Reference System**: Uses EPSG:3413 for Arctic and EPSG:3031 for Antarctic.
6. **Export Project**: Exports the styled project to a QGIS Layer Definition (QLR) file.

### GeoPackage Styling and QGIS Layer Definition

**Script: `style_geopackage_index.py`**

1. **Extract and Organize**: Extracts campaign and institution information from the GeoPackage and creates a hierarchical QGIS project structure.
2. **Layer Styling**: Adds and styles layers using `add_campaign()` with specific colors for availability statuses.
3. **Symbol Creation**: Creates symbols for different geometry types.
4. **Coordinate System**: Sets EPSG codes for Arctic and Antarctic.
5. **Export to QLR**: Exports the project to a QGIS Layer Definition file.

### Flight Path Visualization

**References: code/index**

#### Extract and Process Data

**Script: `extract_radargram_tracks.py`**

1. Traverses directories to identify relevant files.
2. Extracts latitude and longitude coordinates using provider-specific functions.
3. Subsamples tracks with `subsample_tracks_rdp()` to reduce points while preserving path shape.

**Script: `extract_icethk_tracks.py`**

1. Processes ice thickness data for specific regions and campaigns.
2. Projects geographic coordinates to Cartesian system.
3. Uses Ramer-Douglas-Peucker (RDP) algorithm to subsample flight paths.

**Script: `extract_bedmap_tracks.py`**

1. Loads latitude and longitude from CSV files.
2. Removes duplicate points.
3. Maintains minimum 200-meter spacing between points.
4. Transforms coordinates to PS71 system.

![image](https://github.com/user-attachments/assets/6dc95e65-9995-43e1-b7b1-e4fbfcf17e2f)

![image](https://github.com/user-attachments/assets/fd3c4099-5bc6-46fa-afa8-8019faba1809)



#### Combine and Style Data

**Script: `create_geopackage_index.py`**

1. Extracts easting and northing coordinates from CSV files.
2. Adds layers for different data types (BEDMAP, radargrams, ice thickness).
3. Manages various naming conventions and metadata.

**Script: `style_geopackage_index.py`**

1. Extracts campaign and institution information from GeoPackage.
2. Creates hierarchical structure in QGIS project.
3. Styles layers based on availability status.
4. Exports project to QGIS Layer Definition (QLR) file.

This process ensures efficient visualization of radar flight paths in QGIS, organized by institution and campaign.

### Data Indexing and GeoPackage Creation

**References: code/index**

#### Index Creation

**Script: `create_geopackage_index.py`**

1. **Extract Coordinate Data**: Uses `load_xy()` to retrieve `ps71_easting` and `ps71_northing` columns from CSV files.
2. **Process Directories and Files**: Utilizes `add_campaign_directory_gpkg()` and `add_csv_gpkg()` to handle different naming conventions.
3. **Add Data Layers**: Adds layers for different data types (BEDMAP, radargrams, ice thickness, SPRI data).
4. **SQLite Connection**: Uses SQLite to connect to the GeoPackage file and add layers.

#### GeoPackage Styling

**Script: `style_geopackage_index.py`**

1. **Extract Information**: Uses SQLite queries to extract campaign and institution information.
2. **Create QGIS Project**: Structures QGIS project with institutions as top-level groups and campaigns as subgroups.
3. **Style Layers**: Styles each campaign layer based on availability status with different colors.
4. **Export to QLR**: Exports styled project to QGIS Layer Definition (QLR) file.

   ![image](https://github.com/user-attachments/assets/3191b6b9-f34c-4755-be95-c00aca2f6df4)


### Subsampling Radar Flight Paths

Scripts such as `extract_radargram_tracks.py` and `extract_icethk_tracks.py` use the Ramer-Douglas-Peucker (RDP) algorithm to reduce points while preserving the overall shape of flight paths.
