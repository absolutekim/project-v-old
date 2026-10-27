import os
import django
import pandas as pd

# ✅ Django environment settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  # Specify Django project settings
django.setup()  # Configure Django ORM to be available

from destinations.models import Location  # ✅ Use Django ORM

# ✅ Load CSV file
csv_path = "dataset_tripadvisor_2025-03-06_08-09-58-598.csv"  # Check file extension
df = pd.read_csv(csv_path)

# ✅ Columns to be used
main_columns = [
    "id", "name", "description", "category",
    "address", "addressObj/city", "addressObj/state", "addressObj/country", "addressObj/postalcode",
    "addressObj/street1", "addressObj/street2",
    "latitude", "longitude", "localAddress", "localName", "locationString",
    "image", "website", "email",
    "type"
]

# ✅ Filter columns that actually exist (original data)
df_filtered = df[[col for col in main_columns if col in df.columns]].copy()

# ✅ Get `subcategories/` and `subtype/` columns dynamically
subcategories_cols = [col for col in df.columns if col.startswith("subcategories/")]
subtypes_cols = [col for col in df.columns if col.startswith("subtype/")]

# ✅ Check if the column exists in the DataFrame and add it (original data)
for col in subcategories_cols + subtypes_cols:
    df_filtered.loc[:, col] = df[col].fillna("").copy()

# ✅ Use Django ORM to insert data (prevent duplicate data)
for _, row in df_filtered.iterrows():
    location, created = Location.objects.update_or_create(
        id=row["id"],  # ✅ The key to be used
        defaults={  # ✅ If it already exists, it will be updated
            "name": row["name"],
            "description": row["description"] if pd.notna(row["description"]) else None,
            "category": row["category"] if pd.notna(row["category"]) else None,

            "address": row["address"] if pd.notna(row["address"]) else None,
            "city": row["addressObj/city"] if pd.notna(row["addressObj/city"]) else None,
            "state": row["addressObj/state"] if pd.notna(row["addressObj/state"]) else None,
            "country": row["addressObj/country"] if pd.notna(row["addressObj/country"]) else None,
            "postal_code": row["addressObj/postalcode"] if pd.notna(row["addressObj/postalcode"]) else None,
            "street1": row["addressObj/street1"] if pd.notna(row["addressObj/street1"]) else None,
            "street2": row["addressObj/street2"] if pd.notna(row["addressObj/street2"]) else None,

            "latitude": row["latitude"] if pd.notna(row["latitude"]) else None,
            "longitude": row["longitude"] if pd.notna(row["longitude"]) else None,

            "local_address": row["localAddress"] if pd.notna(row["localAddress"]) else None,
            "local_name": row["localName"] if pd.notna(row["localName"]) else None,
            "location_string": row["locationString"] if pd.notna(row["locationString"]) else None,

            "image": row["image"] if pd.notna(row["image"]) else None,
            "website": row["website"] if pd.notna(row["website"]) else None,
            "email": row["email"] if pd.notna(row["email"]) else None,

            "type": row["type"] if pd.notna(row["type"]) else None,

            # ✅ Save only the existing `subcategories/` and `subtype/` columns as a list
            "subcategories": [row[col] for col in subcategories_cols if col in row.index and pd.notna(row[col]) and row[col] != ""],
            "subtypes": [row[col] for col in subtypes_cols if col in row.index and pd.notna(row[col]) and row[col] != ""]
        }
    )

    if created:
        print(f"✅ Add new data: {location.name}")
    else:
        print(f"🔄 Update existing data: {location.name}")

print("✅ Data insertion complete!")
