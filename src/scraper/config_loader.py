import yaml
from datetime import datetime, timedelta


def load_config(path="config/config.yaml"):
    with open(path, "r") as f:
        raw_config = yaml.safe_load(f)

    # Extract basic fields
    stations = raw_config["stations"]
    start = datetime.strptime(raw_config["date_range"]["start"], "%Y-%m-%d")
    days = raw_config["date_range"]["days"]
    server_url = raw_config["server"]["base_url"]
    output_root = raw_config["output"]["root_dir"]
    plot_options = raw_config["plot_options"]

    # Compute date ranges (list of strings)
    date_ranges = [
        (start + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(days)
    ]

    return {
        "stations": stations,
        "date_ranges": date_ranges,
        "server_url": server_url,
        "output_root": output_root,
        "plot_options": plot_options
    }