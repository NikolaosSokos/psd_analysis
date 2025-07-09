# PSD Analysis with Machine Learning

This project provides tools for working with seismic Power Spectral Density (PSD) plots.
It includes scripts to download PSD images from a server, extract frequency features
from those images using OpenCV, and apply clustering or outlier detection.

The code is organised under `src/`:

- **scraper/** – utilities to query a PSD server and save daily PSD plots.
- **visualization/** – helper functions for cropping plots, converting pixel
  coordinates to frequency/power values and highlighting deviations.
- **analysis/** – feature extraction, clustering with K-Means and outlier
  detection relative to New High/Low Noise Models.
- **utils/** – shared constants and file helpers.

Example scripts:

- `src/scraper/scrape_psds.py` downloads PSD images to `data/raw` for a list of
  stations.
- `src/analysis/cluster_psds.py` extracts PSD features and clusters the images.
- `src/analysis/outliers.py` categorises PSDs based on deviations from NHNM and
  NLNM curves and writes a report in `data/reports`.

## Requirements

Python 3.11+ is required. The main dependencies are
[ObsPy](https://docs.obspy.org/), OpenCV, scikit‑learn, `requests` and `tqdm`.
You can install everything from the `pyproject.toml` file:

```bash
pip install -e .
```

## Usage

1. **Scrape PSD images**
   ```bash
   python src/scraper/scrape_psds.py
   ```
   This downloads images and metadata into `data/raw`.

2. **Cluster PSDs**
   ```bash
   python src/analysis/cluster_psds.py
   ```
   Cluster assignments are saved in `data/clustered`.

3. **Detect outliers**
   ```bash
   python src/analysis/outliers.py
   ```
   Results are written to `data/categorized` and `data/reports/outlier_report.txt`.

The repository also contains a sample report under `reports/` describing how PSD
analysis can be used to evaluate station performance.

