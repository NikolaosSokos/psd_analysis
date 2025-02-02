import os
import cv2
import numpy as np
from visualization.analyze_psd_curves import crop_plot_region, extract_psd_curve

def extract_frequency_features(input_dir, freq_range, power_range, margins, color_range):
    """
    Extract frequency-power features from PSD images.
    """
    features = []
    image_paths = []

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith((".png")):
                image_path = os.path.join(root, file)

                # Load the image
                image = cv2.imread(image_path)
                if image is None:
                    continue

                # Crop the plot region
                try:
                    cropped_plot = crop_plot_region(image, margins)
                except Exception as e:
                    print(f"Error cropping plot for {image_path}: {e}")
                    continue

                # Extract PSD points
                try:
                    psd_points, _, _ = extract_psd_curve(cropped_plot, color_range)
                    # Convert psd_points to a 1D feature vector
                    freq_values = [freq for freq, _ in psd_points]
                    power_values = [power for _, power in psd_points]
                    feature_vector = np.histogram2d(
                        freq_values, power_values,
                        bins=(50, 50),  # Adjust bins as needed
                        range=[freq_range, power_range]
                    )[0].flatten()  # Flatten to create a 1D feature vector
                    features.append(feature_vector)
                    image_paths.append(image_path)
                except Exception as e:
                    print(f"Error extracting features for {image_path}: {e}")
                    continue

    return np.array(features), image_paths
