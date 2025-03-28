import numpy as np
import cv2
import os

template_path = 'hero_images_reversed/requiem-roana.png'

img = cv2.imread('pvp/lobby.png', 0)

# template_full = cv2.imread('hero_images_reversed/sea-phantom-politis.png', 0)
template_full = cv2.imread('hero_images/requiem-roana.png', 0)


h_full, w_full = template_full.shape
crop_size = 50 
start_x = w_full // 2 - crop_size // 2
start_y = h_full // 2 - crop_size // 2
template = template_full[start_y:start_y + crop_size, start_x:start_x + crop_size]
h, w = template.shape

unit_name = os.path.splitext(os.path.basename(template_path))[0]

methods = [cv2.TM_SQDIFF_NORMED]

# methods = [cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR,
#             cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]

for method in methods:
    img2 = img.copy()
    result = cv2.matchTemplate(img2, template, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        location = min_loc
        match_value = min_val
    else:
        location = max_loc

    bottom_right = (location[0] + w, location[1] + h)    
    cv2.rectangle(img2, location, bottom_right, 255, 5)
    cv2.imshow('Match', img2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if method == cv2.TM_SQDIFF_NORMED:
        threshold = 0.0 
        if match_value:
            print(f"Match found for {unit_name}")



