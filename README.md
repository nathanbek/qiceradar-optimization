# GeoPackage Creation and Styling

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

### Subsampling Radar Flight Paths

Scripts such as `extract_radargram_tracks.py` and `extract_icethk_tracks.py` use the Ramer-Douglas-Peucker (RDP) algorithm to reduce points while preserving the overall shape of flight paths.
