import os
from analysis.feature_extraction import extract_frequency_features
from analysis.clustering import cluster_features, visualize_clusters
from utils.file_handling import save_clustered_images
from utils.constants import FREQ_RANGE, POWER_RANGE, MARGINS, COLOR_RANGE
def main():
    INPUT_DIR = "data/raw"  # Directory containing raw PSD images
    OUTPUT_DIR = "data/clustered"  # Directory to save clustered images


    print("Starting feature extraction...")
    features, image_paths = extract_frequency_features(INPUT_DIR, FREQ_RANGE, POWER_RANGE, MARGINS, COLOR_RANGE)

    print("Clustering features...")
    num_clusters = 5  # Define the number of clusters
    labels = cluster_features(features, num_clusters)

    print("Visualizing clusters...")
    visualize_clusters(features, labels)

    print("Saving clustered images...")
    save_clustered_images(image_paths, labels, OUTPUT_DIR)

    print("Clustering process complete!")

if __name__ == "__main__":
    main()
