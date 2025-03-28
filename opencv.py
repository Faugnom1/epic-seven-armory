import numpy as np
import cv2
import os

# Load the main image (lobby)
img = cv2.imread('', 0)

# Define the directory containing your hero images
hero_images_dir = 'hero_images'
hero_images_dir_reveres = 'hero_images_reveresed '

# List of methods to try
methods = [cv2.TM_SQDIFF_NORMED]

# Loop through all files in the hero images directory
for filename in os.listdir(hero_images_dir):
    if filename.endswith(".png"):  # Check file extension
        # Full path to hero image
        template_path = os.path.join(hero_images_dir, filename)

        # Extract the hero's name from the filename
        unit_name = os.path.splitext(os.path.basename(template_path))[0]

        # Load the template image, and dynamically crop it around the center
        template_full = cv2.imread(template_path, 0)
        h_full, w_full = template_full.shape
        crop_size = 50  # Size of the crop, centered
        start_x = w_full // 2 - crop_size // 2
        start_y = h_full // 2 - crop_size // 2
        template = template_full[start_y:start_y + crop_size, start_x:start_x + crop_size]
        h, w = template.shape

        for method in methods:
            img2 = img.copy()

            # Perform template matching
            result = cv2.matchTemplate(img2, template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # Determine the best match location
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                location = min_loc
                match_value = min_val
            else:
                location = max_loc
                match_value = max_val

            # Draw rectangle around the matched area
            bottom_right = (location[0] + w, location[1] + h)
            cv2.rectangle(img2, location, bottom_right, 255, 5)

            # # Show the result
            # cv2.imshow(f'Match using {method}', img2)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            # Check if the method is cv2.TM_SQDIFF_NORMED and if the match is below a certain threshold
            if method == cv2.TM_SQDIFF_NORMED:
                threshold = 0.08  # Example threshold, adjust based on your application's needs
                if match_value < threshold:
                    print(f"Match found for {unit_name} using {method} with a value of {match_value:.4f}")
                else:
                    print(f"No match found for {unit_name} using {method}, value is {match_value:.4f}")

