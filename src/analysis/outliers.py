import os
import cv2
import numpy as np
from obspy.signal.spectral_estimation import get_nlnm, get_nhnm
from visualization.analyze_psd_curves import (
    crop_plot_region,
    extract_psd_curve,
    highlight_deviations,
    map_pixel_to_values,
)
from tqdm import tqdm
from utils.constants import FREQ_RANGE, POWER_RANGE, MARGINS, COLOR_RANGE

def categorize_outliers(num_outliers):
    """
    Categorize the image based on the number of outliers.
    """
    if num_outliers == 0:
        return "Normal"
    elif num_outliers <= 10:
        return "Low Deviation"
    elif num_outliers <= 50:
        return "Moderate Deviation"
    elif num_outliers <= 100:
        return "High Deviation"
    else:
        return "Extreme Deviation"


def process_images(input_dir, base_output_dir, report_path, freq_range, power_range, margins, color_range):
    """
    Process all images, highlight deviations, categorize them, and generate a report.
    """
    # Fetch NLNM and NHNM curve data
    nlnm_freq, nlnm_power = get_nlnm()
    nhnm_freq, nhnm_power = get_nhnm()

    # Prepare output directories
    categories = ["Normal", "Low Deviation", "Moderate Deviation", "High Deviation", "Extreme Deviation"]
    category_dirs = {cat: os.path.join(base_output_dir, cat) for cat in categories}
    for cat_dir in category_dirs.values():
        os.makedirs(cat_dir, exist_ok=True)

    # Ensure the report directory exists
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    # Initialize the report
    report_lines = []

    # Process each image
    all_files = [
        os.path.join(root, file)
        for root, _, files in os.walk(input_dir)
        for file in files if file.lower().endswith((".png"))
    ]

    for image_path in tqdm(all_files, desc="Processing images"):
        file_name = os.path.basename(image_path)

        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to load image: {image_path}")
            continue

        # Crop the plot region
        try:
            cropped_plot = crop_plot_region(image, margins)
        except Exception as e:
            print(f"Error cropping plot region for {image_path}: {e}")
            continue

        # Extract PSD points
        try:
            psd_points, crop_width, crop_height = extract_psd_curve(cropped_plot, color_range)
        except Exception as e:
            print(f"Error extracting PSD points for {image_path}: {e}")
            continue

        # Identify outliers
        outliers = []
        for pixel_x, pixel_y in psd_points:
            freq, power = map_pixel_to_values(pixel_x, pixel_y, crop_width, crop_height, freq_range, power_range)

            closest_nhnm_idx = np.argmin(np.abs(np.array(nhnm_freq) - freq))
            closest_nlnm_idx = np.argmin(np.abs(np.array(nlnm_freq) - freq))

            nhnm_power_at_freq = nhnm_power[closest_nhnm_idx]
            nlnm_power_at_freq = nlnm_power[closest_nlnm_idx]

            if power > nhnm_power_at_freq or power < nlnm_power_at_freq:
                outliers.append((freq, power))

        # Categorize the image and save
        num_outliers = len(outliers)
        category = categorize_outliers(num_outliers)
        output_image_path = os.path.join(category_dirs[category], file_name)

        if num_outliers > 0:
            highlighted_image = highlight_deviations(
                cropped_plot.copy(),
                psd_points,
                nhnm_freq,
                nhnm_power,
                nlnm_freq,
                nlnm_power,
                crop_width,
                crop_height,
                freq_range,
                power_range,
            )
            cv2.imwrite(output_image_path, highlighted_image)
        else:
            cv2.imwrite(output_image_path, cropped_plot)

        # Append details to the report
        report_lines.append(f"{file_name}: {num_outliers} outliers, Category: {category}")

    # Save the report
    with open(report_path, "w") as report_file:
        report_file.write("\n".join(report_lines))
    print(f"Report saved to: {report_path}")


def main():
    INPUT_DIR = "data/raw"  # Directory containing raw PSD images
    BASE_OUTPUT_DIR = "data/categorized"  # Base directory for categorized images
    REPORT_PATH = "data/reports/outlier_report.txt"  # Path to save the report


    print("Starting PSD image processing...")
    process_images(INPUT_DIR, BASE_OUTPUT_DIR, REPORT_PATH, FREQ_RANGE, POWER_RANGE, MARGINS, COLOR_RANGE)
    print("PSD image processing complete.")


if __name__ == "__main__":
    main()
