import os
from PIL import Image

# Define the relative paths
input_folder = 'hero_images'
output_folder = 'hero_images_reversed'

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Iterate through all files in the input folder
for filename in os.listdir(input_folder):
    # Construct the full file path
    input_path = os.path.join(input_folder, filename)
    
    # Check if the file is an image
    if os.path.isfile(input_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
        # Open the image
        with Image.open(input_path) as img:
            # Flip the image
            flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)
            
            # Construct the output file path
            output_path = os.path.join(output_folder, filename)
            
            # Save the flipped image
            flipped_img.save(output_path)

print(f"Flipped images have been saved to {output_folder}")
