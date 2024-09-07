import json
import csv

with open("itemsData.json") as json_file:
    data = json.load(json_file)

csv_data = []
headers = [
    "Name",
    "Marketable",
    "Tradable",
    "ClassID",
    "IconURL",
    "Rarity",
    "RarityColor",
    "24_hours_Average",
    "24_hours_Median",
    "24_hours_Sold",
    "7_days_Average",
    "7_days_Median",
    "7_days_Sold",
    "30_days_Average",
    "30_days_Median",
    "30_days_Sold",
    "All_time_Average",
    "All_time_Median",
    "All_time_Sold",
]

for item_name, item_details in data["items_list"].items():
    row = [
        item_details["Name"],
        item_details["Marketable"],
        item_details["Tradable"],
        item_details["ClassID"],
        item_details["IconURL"],
        item_details["Rarity"],
        item_details["RarityColor"],
    ]

    for period in ["24_hours", "7_days", "30_days", "All_time"]:
        period_data = item_details["Price"].get(period, {})
        row.extend(
            [
                period_data.get("Average", 0),
                period_data.get("Median", 0),
                period_data.get("Sold", 0),
            ]
        )

    csv_data.append(row)

with open("itemsData.csv", "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headers)
    writer.writerows(csv_data)

print("CSV file has been created successfully.")
