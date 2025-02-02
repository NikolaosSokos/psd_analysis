import cv2
import numpy as np
import logging

# Configure logging for debugging purposes
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def map_pixel_to_values(pixel_x, pixel_y, crop_width, crop_height, freq_range, power_range):
    """
    Map pixel coordinates in the cropped plot region to real-world frequency and power values.
    """
    # Logarithmic scaling for frequency (x-axis)
    frequency = freq_range[0] * (freq_range[1] / freq_range[0]) ** (pixel_x / crop_width)

    # Linear scaling for power (y-axis)
    power = power_range[1] - (pixel_y * (power_range[1] - power_range[0]) / crop_height)

    return frequency, power

def map_values_to_pixels(frequency, power, crop_width, crop_height, freq_range, power_range):
    """
    Map real-world frequency and power values to pixel coordinates in the cropped plot region.
    """
    # Logarithmic scaling for frequency (x-axis)
    pixel_x = int(crop_width * np.log10(frequency / freq_range[0]) / np.log10(freq_range[1] / freq_range[0]))

    # Linear scaling for power (y-axis)
    pixel_y = int(crop_height * (power_range[1] - power) / (power_range[1] - power_range[0]))

    return pixel_x, pixel_y

def crop_plot_region(image, margins):
    """
    Crop the plot region based on the provided margins.
    """
    left, right, top, bottom = margins
    cropped_image = image[top:-bottom, left:-right]
    logger.debug(f"Cropped image with dimensions: {cropped_image.shape}")
    return cropped_image

def extract_psd_curve(image, color_range):
    """
    Extract PSD curve points from the plot region using HSV color masking.
    """
    # Convert the image to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color_range[0], color_range[1])

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    psd_points = []
    crop_height, crop_width = image.shape[:2]
    for contour in contours:
        for point in contour:
            pixel_x, pixel_y = point[0]
            psd_points.append((pixel_x, pixel_y))

    logger.debug(f"Extracted PSD points: {psd_points}")
    return psd_points, crop_width, crop_height

def extract_psd_curve_with_color(image, color_range, freq_range, power_range, margins):
    """
    Extract PSD curve points from the plot region using HSV color masking.
    Each point will include its color intensity information.
    """
    # Convert to HSV and create a mask
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color_range[0], color_range[1])

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    psd_points = []
    crop_height, crop_width = image.shape[:2]

    # Iterate through contours to extract points and their HSV values
    for contour in contours:
        for point in contour:
            pixel_x, pixel_y = point[0]

            # Extract HSV values at the point
            hue, sat, val = hsv[pixel_y, pixel_x]

            # Map pixel coordinates to frequency and power values
            frequency, power = map_pixel_to_values(pixel_x, pixel_y, crop_width, crop_height, freq_range, power_range)

            # Append point with intensity (value from HSV)
            psd_points.append((pixel_x, pixel_y, val, frequency, power))

    return psd_points



def highlight_deviations(image, psd_points, nhnm_freq, nhnm_power, nlnm_freq, nlnm_power, crop_width, crop_height, freq_range, power_range):
    """
    Highlight points in the plot region that deviate outside the NHNM and NLNM curves.
    """
    for pixel_x, pixel_y in psd_points:
        freq, power = map_pixel_to_values(pixel_x, pixel_y, crop_width, crop_height, freq_range, power_range)

        # Find the closest NHNM and NLNM frequencies
        closest_nhnm_idx = np.argmin(np.abs(np.array(nhnm_freq) - freq))
        closest_nlnm_idx = np.argmin(np.abs(np.array(nlnm_freq) - freq))

        nhnm_power_at_freq = nhnm_power[closest_nhnm_idx]
        nlnm_power_at_freq = nlnm_power[closest_nlnm_idx]

        # Check for deviations
        if power > nhnm_power_at_freq or power < nlnm_power_at_freq:
            logger.debug(f"Outlier detected: Frequency={freq}, Power={power}")
            cv2.circle(image, (pixel_x, pixel_y), radius=3, color=(0, 0, 255), thickness=-1)

    return image

def draw_nlnm_nhnm_curves(image, nhnm_freq, nhnm_power, nlnm_freq, nlnm_power, crop_width, crop_height, freq_range, power_range):
    """
    Draw NLNM and NHNM curves on the cropped plot region.
    """
    logger.debug("Drawing NLNM and NHNM curves...")
    for i in range(len(nhnm_freq) - 1):
        x1, y1 = map_values_to_pixels(nhnm_freq[i], nhnm_power[i], crop_width, crop_height, freq_range, power_range)
        x2, y2 = map_values_to_pixels(nhnm_freq[i + 1], nhnm_power[i + 1], crop_width, crop_height, freq_range, power_range)
        cv2.line(image, (x1, y1), (x2, y2), color=(255, 0, 0), thickness=2)

    for i in range(len(nlnm_freq) - 1):
        x1, y1 = map_values_to_pixels(nlnm_freq[i], nlnm_power[i], crop_width, crop_height, freq_range, power_range)
        x2, y2 = map_values_to_pixels(nlnm_freq[i + 1], nlnm_power[i + 1], crop_width, crop_height, freq_range, power_range)
        cv2.line(image, (x1, y1), (x2, y2), color=(255, 0, 0), thickness=2)

    return image
