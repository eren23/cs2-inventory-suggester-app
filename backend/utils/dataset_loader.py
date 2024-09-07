from datasets import load_dataset


def dataset_loader(hf_token):
    dataset = load_dataset(
        "eren23/cs_item_caption_embeddings",
        token=hf_token,
    )
    return dataset
