### Using Ollama to generate captions

import os
import json
import requests
import base64
from PIL import Image
from io import BytesIO
import time
import csv


def encode_image_to_base64(image_path):
    with Image.open(image_path) as img:
        if img.mode == "RGBA":
            img = img.convert("RGB")
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode()


def generate_caption(image_base64, image_name):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llava:13b",
            "prompt": f"This is a CS-GO item called {image_name}, describe what kind of an item it is, not the type of the item but the color, pattern, etc. Just describe the item don't put too many comments, don't repeat the fact that it's a CS-GO item or the item name. In the output I just want this structure: {{'name': 'item name', 'description': 'item description'}}",
            "images": [image_base64],
        },
    )
    caption = ""
    for line in response.iter_lines():
        if line:
            decoded_line = json.loads(line.decode("utf-8"))
            caption += decoded_line["response"]
            if decoded_line.get("done", False):
                break
    return caption


def process_images(directory, output_file, limit=10):
    start_time = time.time()
    images = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith((".png", ".jpg", ".jpeg"))]

    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Image Name", "Caption"])

        print(f"Processing {len(images)} images...")

        for image_path in images:
            image_name = os.path.basename(image_path)
            image_base64 = encode_image_to_base64(image_path)
            caption = generate_caption(image_base64, image_name)
            writer.writerow([image_name, caption])
            print(f"Processed {image_name}")

    end_time = time.time()
    print(f"Processed {len(images)} images in {end_time - start_time} seconds.")


if __name__ == "__main__":
    images_dir = "path/to/downloaded_images"
    output_csv = "captions.csv"
    process_images(images_dir, output_csv)
