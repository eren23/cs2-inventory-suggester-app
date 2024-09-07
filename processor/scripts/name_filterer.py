import pandas as pd

df = pd.read_csv("itemsData.csv")

item_types = [
    "(Factory New)",
    "(Minimal Wear)",
    "(Field-Tested)",
    "(Well-Worn)",
    "(Battle-Scarred)",
]

filtered_df = df[df["Name"].str.contains("|".join(item_types))]
filtered_df["priority"] = filtered_df["Name"].apply(lambda x: next((i for i, t in enumerate(item_types) if t in x), len(item_types)))
filtered_df["item_name"] = filtered_df["Name"].apply(lambda x: x.split("(")[0].strip())
filtered_df = filtered_df.sort_values(["item_name", "priority"]).drop_duplicates("item_name")
filtered_df = filtered_df.drop(["priority", "item_name"], axis=1)

filtered_df.to_csv("filteredItemsData.csv", index=False, encoding="utf-8")

print("Filtered CSV file has been created successfully.")
