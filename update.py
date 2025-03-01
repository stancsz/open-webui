import os
import requests
from io import BytesIO
from PIL import Image
import base64

# Updated list of file paths.
paths = [
    "static/favicon/apple-touch-icon.png",
    "static/favicon/favicon-96x96.png",
    "static/favicon/favicon.ico",
    "static/favicon/favicon.svg",
    "static/favicon/web-app-manifest-192x192.png",
    "static/favicon/web-app-manifest-512x512.png",
    "static/static/favicon.png",
    "static/static/splash.png",
    "static/static/splash-dark.png"
]

# URL of the source image.
source_url = (
    "https://gist.githubusercontent.com/stancsz/45eefbcaf0b766f70fb035dc60ff64b1/"
    "raw/4fa918d1b9980c15b673fe331933f1daef85e2de/favicon.png"
)

# Download the source image.
print("Downloading source image...")
response = requests.get(source_url)
if response.status_code != 200:
    raise Exception(f"Failed to download image: {response.status_code}")
source_image = Image.open(BytesIO(response.content))
print("Download complete.")

def create_svg_with_embedded_png(png_bytes, width, height):
    """Create an SVG string that embeds the given PNG image in base64."""
    b64_data = base64.b64encode(png_bytes).decode('utf-8')
    svg = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <image width="{width}" height="{height}" href="data:image/png;base64,{b64_data}" />
</svg>
'''
    return svg

# Process each file path.
for path in paths:
    print(f"Processing {path} ...")
    # Ensure the directory exists.
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Determine the file extension.
    ext = os.path.splitext(path)[1].lower()  # .png, .ico, .svg, etc.
    
    # Read the current image dimensions.
    # If the file exists, use its size; otherwise, default to the source image size.
    if os.path.exists(path):
        try:
            with Image.open(path) as current_img:
                target_size = current_img.size  # (width, height)
            print(f"Found existing file with size: {target_size}")
        except Exception as e:
            print(f"Could not read image size from {path}: {e}")
            target_size = source_image.size
    else:
        print(f"{path} does not exist. Using source image size.")
        target_size = source_image.size

    # Resize the source image to the target size using high-quality LANCZOS resampling.
    resized_img = source_image.resize(target_size, Image.Resampling.LANCZOS)
    
    # Save the resized image based on the file extension.
    if ext == ".png":
        resized_img.save(path, format="PNG")
        print(f"Saved resized PNG to {path}.")
        
    elif ext == ".ico":
        resized_img.save(path, format="ICO", sizes=[target_size])
        print(f"Saved resized ICO to {path}.")
        
    elif ext == ".svg":
        # For SVG, embed the resized PNG image in an SVG wrapper.
        buffer = BytesIO()
        resized_img.save(buffer, format="PNG")
        png_data = buffer.getvalue()
        svg_content = create_svg_with_embedded_png(png_data, target_size[0], target_size[1])
        with open(path, "w", encoding="utf-8") as svg_file:
            svg_file.write(svg_content)
        print(f"Saved SVG with embedded image to {path}.")
        
    else:
        print(f"Unsupported file extension for {path}. Skipping.")

print("Script completed.")
