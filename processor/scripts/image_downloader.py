import os
import pandas as pd
import requests

output_dir = "downloaded_images"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

df = pd.read_csv("filteredItemsData.csv")

url_prefix = "https://community.akamai.steamstatic.com/economy/image/"

for index, row in df.iterrows():
    full_url = url_prefix + row["IconURL"]

    filename = row["Name"].replace("|", "-").replace(" ", "_").replace("(", "").replace(")", "") + ".jpg"
    file_path = os.path.join(output_dir, filename)

    try:
        response = requests.get(full_url, stream=True)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Image saved: {file_path}")
        else:
            print(f"Failed to download image from {full_url}")
    except Exception as e:
        print(f"Error downloading {full_url}: {e}")

print("Image download process completed.")
