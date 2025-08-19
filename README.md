# Urban-vs-Rural-Temperature-Analysis
Python GIS analysis of Landsat data comparing urban vs rural land surface temperature (LST), with maps, plots, and CSV outputs.
# Urban vs Rural Temperature Analysis

This project compares land surface temperature (LST) between an urban center (Vancouver, BC) and surrounding rural areas using **Landsat 8/9 satellite imagery** and **Python GIS tools**.

---

## Data

- Landsat 8/9 Level-2 Surface Temperature TIFF
- Urban and rural boundary GeoJSON files
- Metadata included:
  - Scene Date: 2024-08-09
  - Product Generated: 2024-08-15
  - Day/Night: DAY
  - Land Cloud Cover: 18.28%
  - Scene Cloud Cover: 15.57%

---

## Tools & Libraries

- Python 3.x  
- rasterio  
- geopandas  
- matplotlib  
- numpy  
- pandas  

---

## Results

### 1️⃣ Urban vs Rural Temperature Maps

![Temperature Maps](output/temperature_maps.png)

### 2️⃣ Urban and Zoomed Rural Area Maps

![Urban and Rural Maps](output/urban_rural_maps.png)

### 3️⃣ Urban vs Rural Surface Temperature Bar Plot

![Bar Plot](output/temperature_stats_barplot.png)

### 4️⃣ CSV File with Statistics

- Saved as `output/urban_rural_LST_stats.csv`
- Example content:

| Statistic | Urban_LST_C | Rural_LST_C |
|-----------|------------|------------|
| Mean      | 17.96      | 12.06      |
| Median    | 18.55      | 14.15      |
| Max       | 18.95      | 22.15      |

---

## Usage

```bash
# Run the analysis
python pyscript.py
