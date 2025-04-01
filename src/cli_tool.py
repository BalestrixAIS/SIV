import argparse
import cv2
import numpy as np
import time
import sys
import os
from tqdm import tqdm  # For the progress bar
import pyfiglet  # For ASCII text banners
from termcolor import colored  # For colored output
from dehazer import dehaze_image

sys.dont_write_bytecode = True  # Prevents __pycache__ generation

def print_banner():
    banner = pyfiglet.figlet_format("Dehaze Tool")
    print(colored(banner, "cyan"))
    print(colored("###############################################", "light_magenta"))
    print(colored("#         IMAGE DEHAZING TOOL v1.0            #", "light_magenta"))
    print(colored("#   Using Dark Channel Prior Algorithm        #", "light_magenta"))
    print(colored("###############################################\n", "light_magenta"))

def print_separator():
    print(colored("--------------------------------------------------", "light_magenta"))

def save_image(image, input_path, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    base_name, ext = os.path.splitext(os.path.basename(input_path))
    output_filename = f"{base_name}_dehazed{ext}"
    output_path = os.path.join(output_dir, output_filename)

    # Convert image to proper format and save
    image = (image * 255).astype(np.uint8)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, image)

    return output_path

def main():
    print_banner()
    print_separator()
    print(colored("Welcome to the Image Dehazing Tool!", "blue"))
    print("This tool removes haze from images using the Dark Channel Prior algorithm.")
    print("Simply enter the path to your image, and let the tool do the work!\n")
    print_separator()

    image_path = input(colored("Enter the path to the image you want to dehaze: ", "blue"))

    # Define the processed images output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed_images/")
    
    print_separator()
    print(colored("✨ Processing image... Please wait...", "blue"))
    print_separator()
    
    try:
        progress_bar = tqdm(total=100, desc=colored("Dehazing", "blue"), bar_format="{l_bar}{bar} {n_fmt}/{total_fmt} [{elapsed}<{remaining}]")
        for i in range(1, 101, 20):
            time.sleep(0.3)  # Simulating processing time
            progress_bar.update(20)
        progress_bar.close()
        
        image, dark_channel, transmission, dehazed_image = dehaze_image(image_path)
        saved_path = save_image(dehazed_image, image_path, output_dir)

        print_separator()
        print(colored(f"✅ Done! The dehazed image has been saved at: {saved_path}", "green"))
        print_separator()
    except Exception as e:
        print_separator()
        print(colored(f"❌ Error: {e}", "red"))
        print_separator()

if __name__ == "__main__":
    main()