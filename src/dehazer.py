import cv2
import numpy as np

# Load the image and convert to the right format
def load_image(path):
    # Read the image
    image = cv2.imread(path)
    
    # Convert from BGR to RGB (since default is BGR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Normalize the image to [0,1] range
    image = image / 255.0
    return image

# 1. Estimate the dark channel of the image
def get_dark_channel(image, patch_size=15):
    # Find the minimum pixel value across all channels (R,G,B) for each pixel
    min_channel = np.min(image, axis=2)
    
    # Create a square structuring element for the erosion operation
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (patch_size, patch_size))
    
    # Erode the minimum channel to get the dark channel
    dark_channel = cv2.erode(min_channel, kernel)
    return dark_channel

# 2. Estimate the atmospheric light in the image
def get_atmospheric_light(image, dark_channel, top_percent=0.0001):
    # Flatten the dark channel to a 1D array for further operations
    flat_dark = dark_channel.ravel()
    
    # Calculate the number of pixels corresponding to the top percentage
    num_pixels = flat_dark.size
    num_brightest = int(num_pixels * top_percent)

    # Get the indices of the brightest pixels in the dark channel
    indices = np.argpartition(flat_dark, -num_brightest)[-num_brightest:]
    
    # Convert the obtained indices back to 2D indices in the original image
    brightest_pixels = np.unravel_index(indices, dark_channel.shape)

    # Calculate the mean color of the brightest pixels to estimate the atmospheric light
    atmospheric_light = np.mean(image[brightest_pixels], axis=0)
    return atmospheric_light

# 3. Estimate the transmission map and refine it
def refine_transmission(image, transmission, radius=60, epsilon=1e-3):
    # Convert the image to an 8-bit format for processing
    image = (image * 255).astype(np.uint8)
    
    # Convert the image to grayscale (used as guidance image)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Apply guided filtering to refine the transmission map
    refined_transmission = cv2.ximgproc.guidedFilter(
        guide=gray.astype(np.float32),  
        src=transmission.astype(np.float32),
        radius=radius,
        eps=epsilon
    )
    return refined_transmission

def get_transmission_map(image, atmospheric_light, patch_size=15, omega=0.95):
    # Normalize the image by dividing each pixel by the atmospheric light
    norm_image = image / atmospheric_light
    
    # Calculate the dark channel of the normalized image
    dark_channel = get_dark_channel(norm_image, patch_size)
    
    # Estimate the transmission using the dark channel and omega parameter
    transmission = 1 - omega * dark_channel

    # Ensure that the transmission is between 0.1 and 1 (to avoid dark skies)
    transmission = np.clip(transmission, 0.1, 1)
    
    # Refine the transmission map using guided filtering
    refined_transmission = refine_transmission(image, transmission)
    return refined_transmission

# 4. Recover the haze-free image
def recover_image(image, transmission, atmospheric_light, t0=0.1):
    # Ensure transmission values are not too low (avoid division by zero)
    transmission = np.maximum(transmission, t0)
    
    # Recover the haze-free image using the proper formula (obtained from the refrence paper)
    J = (image - atmospheric_light) / transmission[..., np.newaxis] + atmospheric_light
    
    # Clip the values to ensure the result is within [0, 1]
    J = np.clip(J, 0, 1)

    return J

# Full dehazing pipeline
def dehaze_image(image_path):
    image = load_image(image_path)

    dark_channel = get_dark_channel(image)
    atmospheric_light = get_atmospheric_light(image, dark_channel)
    transmission = get_transmission_map(image, atmospheric_light)
    dehazed_image = recover_image(image, transmission, atmospheric_light)
    return (image, dark_channel, transmission, dehazed_image)
