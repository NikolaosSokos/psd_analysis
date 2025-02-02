import os
import shutil

def save_clustered_images(image_paths, labels, output_dir):
    """
    Save clustered images into separate folders based on cluster labels.
    """
    for label, path in zip(labels, image_paths):
        cluster_dir = os.path.join(output_dir, f"Cluster_{label}")
        os.makedirs(cluster_dir, exist_ok=True)
        shutil.copy(path, cluster_dir)
