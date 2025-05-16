# Berkeley Police Department Sector Optimization 👉 [Streamlit Dashboard](https://www.youtube.com/watch?v=nM0Bpt6fSuw&t=29s)

This project optimizes patrol sector boundaries for the Berkeley Police Department by balancing workload (NPPS) across sectors and snapping boundaries to street centerlines.
 

## Data Availability

**Note:** The data files required for this project (e.g., `2024.csv`, `Balanced_Beats_V2.shp`, `Centerlines.shp`, etc.) are **not included in this GitHub repository** due to file size and copyright considerations.

If you need access to the data, please download it from the following link:

- [Download data from Google Drive](https://drive.google.com/drive/folders/1K7m15MCzmZeWsxBR7TwEvf65l-apLIXd?usp=drive_link)

After downloading, place the data files in the project directory as described above.


## Overview

The workflow:
1. Loads patrol sector shapefile and incident data
2. Creates a grid and assigns sectors to grid cells
3. Calculates NPPS (Normalized Patrol Priority Score) for each incident
4. Aggregates NPPS by grid and sector
5. Optimizes sector boundaries by moving boundary grids between sectors
6. Snaps sector boundaries to street centerlines
7. Visualizes results

## Setup

### Prerequisites

- Python 3.6+
- Required packages:
  - geopandas
  - pandas
  - matplotlib
  - shapely
  - scikit-learn

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/bpd_sector_optimization.git
   cd bpd_sector_optimization
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Place your data files in the project directory:
   - `Balanced_Beats_V2.shp` (patrol sector shapefile)
   - `2024.csv` (incident data)
   - `Centerlines.shp` (street centerlines)

## Module Structure

- `config.py`: All parameters and file paths
- `data_preprocessing.py`: Data loading, cleaning, NPPS calculation
- `grid_utils.py`: Grid creation, spatial joins, boundary detection
- `npps_analysis.py`: NPPS aggregation, outlier handling, scoring
- `sector_optimization.py`: Grid reassignment, optimization logic
- `snapping.py`: Snapping sectors to street centerlines
- `visualization.py`: Plotting and visualization functions
- `main.py`: Main script to run the workflow

## Usage

### Running the Workflow

Run the main script:
```bash
python main.py
```

### Modifying Parameters

Edit `config.py` to change:
- File paths
- Grid cell size
- NPPS weights
- Outlier handling
- Snapping tolerance
- Sector neighbors

Example:
```python
# config.py
CELL_SIZE = 0.001  # 100m grid
PRIORITY_WEIGHTS = {1: 1.0, 2: 0.7, 3: 0.4, 4: 0.2, 5: 0.1}
```

### Example Output

- Initial NPPS heatmap
- Grid transfers from excess sectors
- Grid transfers to deficient sectors
- Final snapped sector boundaries

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Berkeley Police Department for data
- Contributors and maintainers 
