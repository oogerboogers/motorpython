## Code for focus check:
## The current code checks a folder for image files ('.png', '.jpg', '.jpeg', '.bmp', '.tif') and outputs a focus value for each image. The larger the value, the better the focus. 
## Need to be careful of multiple objects which may be in focus at 2 different z positions. Possible usage: run the check_focus command on each image at changing Z and only save the focus value. 
## Or save images at each Z position and save the value. Move to the highest value position and reiterate for finer movement.

import cv2
import os
import matplotlib.pyplot as plt

def is_image_in_focus(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    laplacian = cv2.Laplacian(image, cv2.CV_64F)
    variance = laplacian.var()
    
    return variance

def display_image_with_focus(image_path, focus_score):
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    resized_image = cv2.resize(image, (width // 4, height // 4))
    resized_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(12, 8))
    plt.imshow(resized_image)
    plt.title(f"Focus Score: {focus_score:.2f}")
    plt.axis('off')
    plt.show()

def find_best_focus_image(folder_path):
    best_focus_score = -1
    best_focus_image = None
    
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif')):
            image_path = os.path.join(folder_path, filename)
            focus_score = is_image_in_focus(image_path)
            display_image_with_focus(image_path, focus_score)
            print(f"Image: {filename}, Focus Score: {focus_score:.2f}")
            
            if focus_score > best_focus_score:
                best_focus_score = focus_score
                best_focus_image = filename
    
    print(f"\nImage with the best focus: {best_focus_image}, Focus Score: {best_focus_score:.2f}")

folder_path = '/Focus_2/'
find_best_focus_image(folder_path)
