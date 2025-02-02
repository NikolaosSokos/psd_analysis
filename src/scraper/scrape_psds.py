from datetime import datetime, timedelta
from query_server import fetch_and_save_psd
from tqdm import tqdm  # For the progress bar

def generate_date_ranges(start_date, num_days):
    """Generate (start, end) date ranges for each day."""
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    date_ranges = []
    for i in range(num_days):
        start = start_date_obj + timedelta(days=i)
        end = start + timedelta(days=1)
        date_ranges.append((start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")))
    return date_ranges

def scrape_psds(base_url, stations, start_date, output_dir, options):
    """Scrape PSDs day by day for multiple stations with a progress bar."""
    date_ranges = generate_date_ranges(start_date, 300)

    # Calculate total number of tasks for the progress bar
    total_tasks = len(stations) * len(date_ranges)

    with tqdm(total=total_tasks, desc="Scraping PSDs", unit="task") as pbar:
        for station in stations:
            network, station_code, location, channel = station.values()
            for start, end in date_ranges:
                metadata = {
                    "network": network,
                    "station": station_code,
                    "channel": channel,
                    "starttime": start,
                    "endtime": end,
                    "options": options
                }
                fetch_and_save_psd(
                    base_url=base_url,
                    network=network,
                    station=station_code,
                    location=location,
                    channel=channel,
                    starttime=start,
                    endtime=end,
                    output_dir=output_dir,
                    options=options,
                    metadata=metadata
                )
                pbar.update(1)  # Update the progress bar

if __name__ == "__main__":
    BASE_URL = "http://10.0.0.248:8000/histogram"
    OUTPUT_DIR = "data/raw"
    
    # Station configuration
    stations = [
        {"network": "HL", "station": "ATH", "location": "--", "channel": "HHZ"}
    ]
    
    # Start date and query options
    START_DATE = "2024-01-01"
    OPTIONS = {
        "dpi": 300,
        "width": 800,
        "height": 600,
        "format": "png",
        "cmap": "viridis",
        "mean": "true",
        "noisemodels": "true",
        "xmin": 0.1,
        "xmax": 50,
        "ymin": -200,
        "ymax": -50
    }
    
    # Scrape PSDs with progress tracking
    scrape_psds(BASE_URL, stations, START_DATE, OUTPUT_DIR, OPTIONS)
