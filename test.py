from src.scraper.config_loader import load_config

config = load_config()
print(config["stations"])
print(config["plot_options"]["format"])
