from datetime import datetime, timedelta
from tqdm import tqdm
import requests
import os
from scraper.config_loader import load_config


def build_query_url(base_url, network, station, location, channel, starttime, endtime, options):
    """Build a query URL with all parameters."""
    params = {
        "network": network,
        "station": station,
        "location": location,
        "channel": channel,
        "starttime": starttime,
        "endtime": endtime,
        **options
    }
    return requests.Request("GET", base_url, params=params).prepare().url


def create_output_path(output_root, channel, network, station, date, extension):
    """Create output directory and return full path."""
    path = os.path.join(output_root, channel, network, station)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{date}.{extension}")


def download_psd_image(query_url, output_path):
    """Download and save the PSD image."""
    try:
        response = requests.get(query_url)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"Failed to fetch: {query_url} - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"Error fetching {query_url}: {e}")
        return False


def run_downloader(config):
    stations = config["stations"]
    date_ranges = config["date_ranges"]
    base_url = config["server_url"]
    output_root = config["output_root"]
    plot_options = config["plot_options"]
    extension = plot_options.get("format", "png")

    total = len(stations) * sum(len(st["channels"]) for st in stations) * len(date_ranges)

    with tqdm(total=total, desc="Downloading PSDs") as pbar:
        for station in stations:
            for channel in station["channels"]:
                failures = 0  # Track consecutive failures for this channel

                for date in date_ranges:
                    starttime = date
                    endtime = (datetime.fromisoformat(date) + timedelta(days=1)).strftime("%Y-%m-%d")

                    query_url = build_query_url(
                        base_url,
                        station["network"],
                        station["station"],
                        station["location"],
                        channel,
                        starttime,
                        endtime,
                        plot_options
                    )

                    print(f"Querying: {query_url}")

                    output_path = create_output_path(
                        output_root,
                        channel,
                        station["network"],
                        station["station"],
                        date,
                        extension
                    )

                    success = download_psd_image(query_url, output_path)

                    if not success:
                        failures += 1
                        if failures >= 3:
                            print(f"❌ Skipping channel {channel} after 3 consecutive failures.")
                            break  # Stop querying this channel
                    else:
                        failures = 0  # Reset failure counter on success

                    pbar.update(1)


if __name__ == "__main__":
    config = load_config("config/config.yaml")
    run_downloader(config)
