import argparse
import cv2
import numpy as np
from dehazer import dehaze_image  # Assuming your original script is named 'dehaze_script.py'

def save_image(image, output_path):
    image = (image * 255).astype(np.uint8)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, image)

def main():
    parser = argparse.ArgumentParser(description="CLI tool for image dehazing using Dark Channel Prior.")
    parser.add_argument("-i", "--image", required=True, help="Path to the input image.")
    parser.add_argument("-o", "--output", default="dehazed.jpg", help="Path to save the dehazed image (default: dehazed.jpg).")
    
    args = parser.parse_args()
    
    try:
        image, dark_channel, transmission, dehazed_image = dehaze_image(args.image)
        save_image(dehazed_image, args.output)
        print(f"Dehazed image saved at: {args.output}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
