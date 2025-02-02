import requests
import os
import json

def build_query(base_url, network, station, location, channel, starttime, endtime, options):
    """Build a query URL with the specified parameters."""
    params = {
        "network": network,
        "station": station,
        "location": location,
        "channel": channel,
        "starttime": starttime,
        "endtime": endtime,
        **options  # Add optional parameters like dpi, width, height, etc.
    }
    return requests.Request("GET", base_url, params=params).prepare().url

def create_output_path(base_dir, network, station, date):
    """Create a structured output path for PSD plots."""
    station_dir = os.path.join(base_dir, network, station)
    os.makedirs(station_dir, exist_ok=True)
    return os.path.join(station_dir, f"{date}.png")

def fetch_and_save_psd(base_url, network, station, location, channel, starttime, endtime, output_dir, options, metadata=None):
    """Fetch PSD plot from the server and save it locally, along with metadata."""
    # Build query URL
    query_url = build_query(base_url, network, station, location, channel, starttime, endtime, options)

    # Define output path
    output_path = create_output_path(output_dir, network, station, starttime)

    try:
        # Fetch PSD data
        response = requests.get(query_url)
        if response.status_code == 200:
            # Save PSD plot
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"PSD saved: {output_path}")

            # Save metadata, if provided
            if metadata:
                metadata_path = output_path.replace(".png", ".json")
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=4)
                print(f"Metadata saved: {metadata_path}")
        else:
            print(f"Failed to fetch: {query_url} - Status: {response.status_code}")
    except Exception as e:
        print(f"Error fetching {query_url}: {e}")
