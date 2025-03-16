import cv2
import numpy as np

# 1. Load the image and convert to the right format
def load_image(path):
    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image / 255.0  # Normalize to [0, 1] range
    return image

# 2. Estimate the dark channel
def get_dark_channel(image, patch_size=15):
    min_channel = np.min(image, axis=2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (patch_size, patch_size))
    dark_channel = cv2.erode(min_channel, kernel)
    return dark_channel

# 3. Estimate the atmospheric light
def get_atmospheric_light(image, dark_channel, top_percent=0.0001):
    flat_dark = dark_channel.ravel()
    num_pixels = flat_dark.size
    num_brightest = int(num_pixels * top_percent)

    indices = np.argpartition(flat_dark, -num_brightest)[-num_brightest:]
    brightest_pixels = np.unravel_index(indices, dark_channel.shape)

    atmospheric_light = np.mean(image[brightest_pixels], axis=0)
    return atmospheric_light

def refine_transmission(image, transmission, radius=60, epsilon=1e-3):
    image = (image * 255).astype(np.uint8)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    refined_transmission = cv2.ximgproc.guidedFilter(
        guide=gray.astype(np.float32),  
        src=transmission.astype(np.float32),
        radius=radius,
        eps=epsilon
    )
    return refined_transmission

# 4. Estimate the transmission map
def get_transmission_map(image, atmospheric_light, patch_size=15, omega=0.95):
    norm_image = image / atmospheric_light
    dark_channel = get_dark_channel(norm_image, patch_size)
    transmission = 1 - omega * dark_channel

    # Handle sky regions where transmission should be close to 0
    transmission = np.clip(transmission, 0.1, 1)
    #return transmission
    refined_transmission = refine_transmission(image, transmission)
    return refined_transmission

# 6. Recover the haze-free image
def recover_image(image, transmission, atmospheric_light, t0=0.1):
    transmission = np.maximum(transmission, t0)

    # Avoid over-saturation by scaling the atmospheric light properly
    J = (image - atmospheric_light) / transmission[..., np.newaxis] + atmospheric_light

    # Clamp values and avoid weird color shifts
    J = np.clip(J, 0, 1)
    return J

# Full pipeline
def dehaze_image(image_path):
    image = load_image(image_path)
    dark_channel = get_dark_channel(image)
    atmospheric_light = get_atmospheric_light(image, dark_channel)
    transmission = get_transmission_map(image, atmospheric_light)
    dehazed_image = recover_image(image, transmission, atmospheric_light)

    return (image, dark_channel, transmission, dehazed_image)

if __name__ == "__main__":
    image_path = "src/images/ristorante.jpg"
    image, dark_channel, transmission, dehazed_image = dehaze_image(image_path)

    cv2.imshow("Original Image", image)
    cv2.imshow("Dark Channel", dark_channel)
    cv2.imshow("Transmission Map", transmission)
    cv2.imshow("Dehazed Image", cv2.cvtColor((dehazed_image * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
