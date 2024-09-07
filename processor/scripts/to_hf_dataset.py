from datasets import Dataset, Features, ClassLabel, Image, Value
from huggingface_hub import HfFolder
import pandas as pd
from PIL import Image as PILImage
import os
import io


def load_image_to_byte_array(image_path):
    with PILImage.open(image_path) as image:
        if image.mode == "RGBA":
            image = image.convert("RGB")
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="JPEG")
        img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


# Prepare the data for the dataset
def prepare_data(images_dir, csv_file):
    df = pd.read_csv(csv_file)
    data = []
    for index, row in df.iterrows():
        image_path = os.path.join(
            images_dir,
            row["Name"].replace("|", "-").replace(" ", "_").replace("(", "").replace(")", "") + ".jpg",
        )
        if os.path.exists(image_path):
            image_byte_array = load_image_to_byte_array(image_path)
            data.append({"image": image_byte_array, "label": row["Name"]})
    return data


def main():
    images_dir = "downloaded_images"
    csv_file = "filteredItemsData.csv"
    dataset_name = "hfdatasetname"
    hf_token = "hf_token"

    HfFolder.save_token(hf_token)

    data = prepare_data(images_dir, csv_file)
    features = Features({"image": Image(decode=True), "label": Value("string")})
    dataset = Dataset.from_pandas(pd.DataFrame(data), features=features)

    dataset.save_to_disk("hf_dataset")
    print("Dataset created.")

    dataset.push_to_hub(dataset_name)
    print(f"Dataset pushed to Hugging Face Hub: {dataset_name}")


if __name__ == "__main__":
    main()
