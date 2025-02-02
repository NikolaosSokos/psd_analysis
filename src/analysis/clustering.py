from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

def cluster_features(features, num_clusters=5):
    """
    Cluster features using K-Means.
    """
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    labels = kmeans.fit_predict(features)
    return labels

def visualize_clusters(features, labels):
    """
    Visualize clusters using t-SNE.
    """
    tsne = TSNE(n_components=2, random_state=42)
    reduced_features = tsne.fit_transform(features)
    plt.figure(figsize=(10, 8))
    for label in np.unique(labels):
        cluster_points = reduced_features[labels == label]
        plt.scatter(cluster_points[:, 0], cluster_points[:, 1], label=f"Cluster {label}")
    plt.legend()
    plt.title("Cluster Visualization")
    plt.show()
