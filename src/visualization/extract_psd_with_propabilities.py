import cv2
import numpy as np
# Constants
FREQ_RANGE = (0.1, 100)  # Frequency range in Hz
POWER_RANGE = (-200, -50)  # Power range in dB
MARGINS = (182, 541, 290, 385)  # Margins for cropping plot region

def extract_legend_mapping(legend_path, bins=10):
    """
    Extract the mapping of HSV values to percentages from the color bar image.
    Args:
        legend_path (str): Path to the color legend image.
        bins (int): Number of discrete bins to sample from the gradient.
    """
    legend = cv2.imread(legend_path)
    if legend is None:
        raise FileNotFoundError(f"Failed to load legend image at {legend_path}")

    # Convert to HSV
    hsv_legend = cv2.cvtColor(legend, cv2.COLOR_BGR2HSV)
    height, width, _ = hsv_legend.shape

    # Define step size based on bins
    step = height // bins

    legend_mapping = []
    for i in range(0, height, step):
        hsv_value = np.mean(hsv_legend[i:i + step, :, :], axis=(0, 1))  # Average across step height and width
        percentage = (1 - i / height) * 30  # Map y-coordinate to percentage (0-30)
        legend_mapping.append((hsv_value, percentage))

    return legend_mapping

def map_hsv_to_percentage(hsv_value, legend_mapping):
    """
    Map an HSV value to the closest percentage based on the legend mapping.
    """
    min_diff = float('inf')
    closest_percentage = 0
    for legend_hsv, percentage in legend_mapping:
        diff = np.linalg.norm(hsv_value - legend_hsv)
        if diff < min_diff:
            min_diff = diff
            closest_percentage = percentage
    return closest_percentage

def map_pixel_to_values(pixel_x, pixel_y, crop_width, crop_height, freq_range, power_range):
    """
    Map pixel coordinates in the cropped plot region to real-world frequency and power values.
    """
    frequency = freq_range[0] * (freq_range[1] / freq_range[0]) ** (pixel_x / crop_width)
    power = power_range[1] - (pixel_y * (power_range[1] - power_range[0]) / crop_height)
    return frequency, power

def crop_plot_region(image, margins):
    """
    Crop the plot region from the image based on given margins.
    """
    top, bottom, left, right = margins
    return image[top:-bottom, left:-right]

def extract_psd_curve_with_probabilities(image, legend_mapping, freq_range, power_range):
    """
    Extract PSD curve lines for each HSV range and combine results.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    crop_height, crop_width = image.shape[:2]

    psd_lines = []

    # Define a general mask for all hues (you can refine this)
    mask = cv2.inRange(hsv, (0, 50, 50), (179, 255, 255))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        for i in range(len(contour) - 1):
            pixel_x1, pixel_y1 = contour[i][0]
            pixel_x2, pixel_y2 = contour[i + 1][0]

            # Get HSV value at the first point
            hsv_value = hsv[pixel_y1, pixel_x1]

            # Map HSV to probability
            probability = map_hsv_to_percentage(hsv_value, legend_mapping)

            # Map pixel coordinates to frequency and power values
            freq1, power1 = map_pixel_to_values(pixel_x1, pixel_y1, crop_width, crop_height, freq_range, power_range)
            freq2, power2 = map_pixel_to_values(pixel_x2, pixel_y2, crop_width, crop_height, freq_range, power_range)

            psd_lines.append(((pixel_x1, pixel_y1), (pixel_x2, pixel_y2), probability, freq1, power1, freq2, power2))

    return psd_lines

def visualize_psd_lines(image_path, legend_path):
    """
    Visualize PSD curve as lines with probabilities extracted from the plot region.
    """
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load image: {image_path}")
        return

    # Crop the plot region
    cropped_image = crop_plot_region(image, MARGINS)

    # Load and process the color legend
    legend_mapping = extract_legend_mapping(legend_path)

    # Extract PSD curve with probabilities
    psd_lines = extract_psd_curve_with_probabilities(cropped_image, legend_mapping, FREQ_RANGE, POWER_RANGE)

    if not psd_lines:
        print("No lines detected. Check the HSV ranges or the input image.")
        return

    # Create a canvas for visualization
    canvas = cropped_image.copy()

    # Draw lines with extracted probability as color
    for (pixel_x1, pixel_y1), (pixel_x2, pixel_y2), probability, _, _, _, _ in psd_lines:
        color = (0, int(probability * 255 / 30), 255 - int(probability * 255 / 30))  # Color mapping based on probability
        cv2.line(canvas, (int(pixel_x1), int(pixel_y1)), (int(pixel_x2), int(pixel_y2)), color=color, thickness=2)

    cv2.namedWindow("PSD Lines Visualization", cv2.WINDOW_NORMAL)
    cv2.imshow("PSD Lines Visualization", canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Example usage
if __name__ == "__main__":
    image_path = "data/raw/HL/ATH/2024-01-01.png"  # Path to a PSD image
    legend_path = "data/color_legend.png"          # Path to the color legend
    visualize_psd_lines(image_path, legend_path)
