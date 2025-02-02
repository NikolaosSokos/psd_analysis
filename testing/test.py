import cv2
import numpy as np
from visualization.analyze_psd_curves import crop_plot_region,map_pixel_to_values
from utils.constants import FREQ_RANGE, POWER_RANGE, MARGINS

def preprocess_image(image):
    """
    Preprocess the image to improve color detection.
    """
    # Apply Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(image, (5, 5), 0)

    # Convert to HSV and apply histogram equalization on the V channel
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    hsv[:, :, 2] = cv2.equalizeHist(hsv[:, :, 2])  # Equalize the V channel

    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def extract_psd_curve_with_multiple_colors(image, hsv_ranges, freq_range, power_range, margins):
    """
    Extract PSD curve lines for each HSV range and combine results.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    crop_height, crop_width = image.shape[:2]

    all_lines = []

    for hsv_range in hsv_ranges:
        # Create a mask for the current HSV range
        mask = cv2.inRange(hsv, hsv_range[0], hsv_range[1])

        # Find contours for the current mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Extract line segments from contours
        for contour in contours:
            for i in range(len(contour) - 1):
                pixel_x1, pixel_y1 = contour[i][0]
                pixel_x2, pixel_y2 = contour[i + 1][0]

                # Extract HSV values at the first point
                hue, sat, val = hsv[pixel_y1, pixel_x1]

                # Map pixel coordinates to frequency and power values
                freq1, power1 = map_pixel_to_values(pixel_x1, pixel_y1, crop_width, crop_height, freq_range, power_range)
                freq2, power2 = map_pixel_to_values(pixel_x2, pixel_y2, crop_width, crop_height, freq_range, power_range)

                # Append the line segment with intensity
                all_lines.append(((pixel_x1, pixel_y1), (pixel_x2, pixel_y2), val, freq1, power1, freq2, power2))

    return all_lines

def visualize_psd_lines(image_path, hsv_ranges):
    """
    Visualize PSD curve as lines for each HSV range extracted from the plot region.
    """
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load image: {image_path}")
        return

    # Crop the plot region
    cropped_image = crop_plot_region(image, MARGINS)

    # Extract PSD curve as lines
    psd_lines = extract_psd_curve_with_multiple_colors(cropped_image, hsv_ranges, FREQ_RANGE, POWER_RANGE, MARGINS)

    if not psd_lines:
        print("No lines detected. Check the HSV ranges or the input image.")
        return

    # Create a blank canvas for visualization
    canvas = cropped_image.copy()

    # Draw lines with extracted intensity as color
    for (pixel_x1, pixel_y1), (pixel_x2, pixel_y2), intensity, _, _, _, _ in psd_lines:
        color = (int(intensity), 255 - int(intensity), int(intensity))  # Example color mapping
        cv2.line(canvas, (int(pixel_x1), int(pixel_y1)), (int(pixel_x2), int(pixel_y2)), color=color, thickness=2)

    # Create a resizable window
    cv2.namedWindow("PSD Lines Visualization", cv2.WINDOW_NORMAL)
    cv2.imshow("PSD Lines Visualization", canvas)

    # Wait for a key press and then close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage
if __name__ == "__main__":
    image_path = "data/raw/HL/ATH/2024-01-01.png"  # Path to a sample PSD image

    # Define multiple HSV ranges for detecting different parts of the PSD curve
    HSV_RANGES = [
        ((100, 50, 50), (140, 255, 255)),  # Blue hues
        ((20, 50, 50), (30, 255, 255)),   # Yellow hues
        ((0, 50, 50), (10, 255, 255)),    # Red hues
    ]

    visualize_psd_lines(image_path, HSV_RANGES)
