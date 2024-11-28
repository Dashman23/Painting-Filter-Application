from PIL import Image, ImageDraw
import numpy as np
import cv2

def halftone_dither_channel(channel, cell_size):
    width, height = channel.size
    pixels = np.array(channel, dtype=np.float32)

    # Create a new image for the halftone result
    halftone_channel = Image.new('L', (width, height), 255)
    draw = ImageDraw.Draw(halftone_channel)

    # Process the image in blocks (cells)
    for y in range(0, height, cell_size):
        for x in range(0, width, cell_size):
            # Calculate the average brightness of the cell
            cell = pixels[y:y + cell_size, x:x + cell_size]
            mean_brightness = np.mean(cell)

            # Determine the radius of the dot based on brightness
            radius = (1 - mean_brightness / 255) * (cell_size / 2)

            # Draw the dot in the center of the cell
            center_x = x + cell_size / 2
            center_y = y + cell_size / 2
            draw.ellipse(
                (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
                fill=0
            )

    return halftone_channel

def halftone_dither_color(image_path, output_path, cell_size=10):
    # Open the image
    image = Image.open(image_path)
    width, height = image.size

    # Split the image into R, G, B channels
    r, g, b = image.split()

    # Apply halftone dithering to each channel
    r_dithered = halftone_dither_channel(r, cell_size)
    g_dithered = halftone_dither_channel(g, cell_size)
    b_dithered = halftone_dither_channel(b, cell_size)

    # Merge the dithered channels back together
    halftone_image = Image.merge('RGB', (r_dithered, g_dithered, b_dithered))

    # Save the halftone image
    halftone_image.save(output_path)

def adjust_rgb(image_path, output_path, r_factor=1.1, g_factor=1.0, b_factor=1.2):
    # Open the image
    image = Image.open(image_path).convert('RGB')
    np_image = np.array(image, dtype=np.float32)

    # Split the image into R, G, B channels
    r, g, b = np_image[:,:,0], np_image[:,:,1], np_image[:,:,2]

    # Adjust each channel by the specified factor
    r = np.clip(r * r_factor, 0, 255)
    g = np.clip(g * g_factor, 0, 255)
    b = np.clip(b * b_factor, 0, 255)

    # Merge the channels back
    adjusted_image = np.stack([r, g, b], axis=2).astype(np.uint8)
    # Convert back to PIL Image and save
    result_image = Image.fromarray(adjusted_image)
    result_image.save(output_path)


# Example usage
# adjust_rgb(r'C:\Users\Heisn\Desktop\Comp_Photo\Computational_Photography_Assignment\IMG_1415.png', 'dithered_image.png')
# adjust_rgb(r'C:\Users\Heisn\Desktop\Comp_Photo\Computational_Photography_Assignment\IMG_1415.png', 'dithered_imageC.png')
# halftone_dither_color(r'C:\Users\Heisn\Desktop\Comp_Photo\Computational_Photography_Assignment\dithered_image.png', 'dithered_image.png')
#adjust_rgb(r'C:\Users\Heisn\Desktop\Comp_Photo\Computational_Photography_Assignment\dithered_image.png', 'dithered_image.png')

def dither_blur(image_path, output_path, cell_size=10):
    # Adjust RGB channels and save the intermediate image
    adjusted_image_path = 'Temp-Pictures/adjusted_image.png'
    adjust_rgb(image_path, adjusted_image_path)
    
    # Apply halftone dithering and save the result
    dithered_image_path = 'Temp-Pictures/dithered_image.png'
    halftone_dither_color(adjusted_image_path, dithered_image_path, cell_size)
    
    # Read the dithered image
    dithered_image = cv2.imread(dithered_image_path)
    if dithered_image is None:
        raise FileNotFoundError(f"Failed to load image at {dithered_image_path}")
    
    # Define the Gaussian kernel size (must be odd)
    kernel_size = (cell_size * 2 + 1, cell_size * 2 + 1)
    sigma = 0  # Standard deviation; if 0, OpenCV calculates it based on the kernel size.
    
    # Apply Gaussian Blur
    blurred_image = cv2.GaussianBlur(dithered_image, kernel_size, sigma)
    
    # Save the blurred image
    cv2.imwrite(output_path, blurred_image)


# # Read the image
# image = cv2.imread("dithered_image.png")
# imageC = cv2.imread("dithered_imageC.png")

# # Define the Gaussian kernel size (must be odd) and standard deviation
# kernel_size = (51, 51)  # Width and height of the kernel (both must be odd)
# sigma = 0 # Standard deviation. If 0, OpenCV calculates it based on the kernel size.

# # Apply Gaussian Blur
# blurred_image = cv2.GaussianBlur(image, kernel_size, sigma)
# blurred_image_control = cv2.GaussianBlur(imageC, kernel_size, sigma)
# # Save or display the result
# cv2.imwrite("DitheredandBlurred.jpg", blurred_image)
# cv2.imwrite("OnlyBlurred.jpg", blurred_image_control)