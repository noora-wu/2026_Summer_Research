# Plant Growth Analysis from Images

This project provides an automated workflow to analyze plant growth using time-series images. It extracts plant information from photos, generates growth and health trends, and creates an interactive web dashboard for visualization.

## Features

### Image Analysis (`analyze.py`)
- **Automatic Area Measurement**: Calculates plant coverage area in pixels
- **Health Index Calculation**: Analyzes green vs yellow pixels to assess plant health (0-1 scale)
- **Height Measurement**: Measures plant height from bottom to top
- **Density Calculation**: Computes plant density as percentage of image coverage
- **Anomaly Detection**: Identifies unusual growth patterns using statistical analysis
- **Growth Prediction**: Linear trend prediction for future growth
- **Overlay Generation**: Creates visual overlays showing detected green and yellow regions

### Interactive Dashboard (`dashboard.py`)
- **Interactive Charts**: Four synchronized charts showing Area, Health, Height, and Density trends
- **Statistical Overview**: Key metrics including growth rate, peak area, health score, and max height
- **Image Viewer**: Click any data point to view original and overlay images in a modal popup
- **Chart Download**: Export charts as high-resolution PNG images
- **Responsive Design**: Works on desktop and mobile devices

## How It Works

### Image Processing Pipeline

1. **Image Loading**: Reads all JPG images from the `img/` folder, sorted by date
2. **Color Detection**: 
   - Converts images to HSV color space
   - Detects green pixels (HSV: 35-85, 40-255, 40-255)
   - Detects yellow pixels (HSV: 20-35, 40-255, 40-255)
3. **Measurement Calculation**:
   - **Area**: Total number of green pixels
   - **Health**: Ratio of green to (green + yellow) pixels
   - **Height**: Distance from bottom to topmost green pixel
   - **Density**: Green pixels / total image pixels
4. **Overlay Generation**: Creates colored overlays showing detected regions
5. **Anomaly Detection**: Identifies data points with growth rate > 2 standard deviations
6. **Data Export**: Saves all metrics to `plant_analysis.csv`

### Dashboard Generation

1. **Data Loading**: Reads analysis results from CSV
2. **Image Encoding**: Converts all images to base64 for embedding
3. **Chart Creation**: Generates interactive Plotly charts
4. **HTML Generation**: Creates self-contained HTML file with embedded data

## Requirements

### Python Libraries

```bash
# For image analysis
pip install opencv-python numpy matplotlib

# For dashboard generation
pip install plotly pandas
```

Or install all at once:

```bash
pip install opencv-python numpy matplotlib plotly pandas
```

## Project Structure

```
plant_project/
├── img/                    # Input images (JPG format, named as YYYY-M-D.jpg)
├── overlay/                # Generated overlay images (created automatically)
├── analyze.py              # Main analysis script
├── dashboard.py            # Dashboard generator
├── plant_analysis.csv      # Analysis results (generated)
└── dashboard.html          # Interactive dashboard (generated)
```

## How to Use

### Step 1: Prepare Images

1. Place your plant images in the `img/` folder
2. Name images in format: `YYYY-M-D.jpg` (e.g., `2023-10-16.jpg`)
3. Ensure images are taken from the same angle for consistent analysis

### Step 2: Run Analysis

```bash
python analyze.py
```

This will:
- Process all images in `img/` folder
- Generate overlay images in `overlay/` folder
- Create `plant_analysis.csv` with all measurements
- Display growth charts (optional)

**Output Files:**
- `plant_analysis.csv`: Contains Image, Area, Health, Height, Density, GrowthRate, Anomaly columns
- `overlay/`: Folder with processed images showing green/yellow detection

### Step 3: Generate Dashboard

```bash
python dashboard.py
```

This will:
- Read analysis data from CSV
- Generate `dashboard.html` with interactive visualizations
- Embed all images for offline viewing

### Step 4: View Dashboard

Open `dashboard.html` in any web browser. The dashboard includes:

- **Top Statistics Cards**: 
  - Growth Rate: Percentage increase from first to last image
  - Peak Area: Maximum area reached
  - Health Score: Average health index
  - Max Height: Maximum height measured

- **Interactive Charts**:
  - Plant Area Growth (with anomaly markers)
  - Health Index over time
  - Plant Height progression
  - Density trends

- **Image Viewer**:
  - Click any data point to open modal
  - View original and overlay images side-by-side
  - See detailed metrics for selected image

## Dashboard Features

### Chart Interactions
- **Zoom**: Click and drag to zoom in
- **Pan**: Click and drag to pan
- **Reset**: Double-click to reset view
- **Hover**: Hover over points to see details
- **Download**: Click download button (camera icon) to save as PNG

### Image Modal
- Click any data point in charts
- View original and processed images
- See detailed metrics:
  - Image name
  - Area (pixels)
  - Health index
  - Height (pixels)
  - Density

## Best Practices

### Image Quality
- Use consistent camera angle and distance
- Ensure stable background
- Good lighting conditions
- Consistent image resolution

### File Naming
- Use format: `YYYY-M-D.jpg` (e.g., `2023-10-16.jpg`)
- Ensure dates are in chronological order
- Avoid special characters in filenames

### Analysis Settings
- Adjust HSV color ranges in `analyze.py` if needed:
  - Green detection: `lower_green` and `upper_green`
  - Yellow detection: `lower_yellow` and `upper_yellow`


## Acknowledgments

Built using:
- OpenCV for image processing
- Plotly for interactive visualizations
- Pandas for data analysis
- NumPy for numerical computations
