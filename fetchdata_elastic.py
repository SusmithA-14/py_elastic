from elasticsearch import Elasticsearch
import pandas as pd
import os

# === CONFIGURATION ===
ES_ENDPOINT = "https://my-elasticsearch-project-e5302c.es.us-central1.gcp.elastic.cloud:443"
ES_API_KEY = "ZTJod1Nab0J6dXpSVWFWeWlKdGw6VzZjT0xGbGFva1ZadUhHSTJLakxSQQ=="
OUTPUT_DIR = "elastic_exports" #this is where fetched records from elastic search will be saved

# === CONNECT TO ELASTIC ===
es = Elasticsearch(
    ES_ENDPOINT,
    api_key=ES_API_KEY,
    verify_certs=False
)

# === CHECK CONNECTION ===
if not es.ping():
    print("❌ Connection failed! Please check endpoint or API key.")
    exit()
else:
    print("✅ Connected to Elasticsearch!")

# === CREATE OUTPUT FOLDER ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === GET ALL INDICES ===
indices = es.cat.indices(format="json")
index_names = [idx['index'] for idx in indices]

print("\n📦 Available Indices:")
for i, name in enumerate(index_names, start=1):
    print(f"{i}. {name}")

# === ASK USER FOR CHOICE ===
choice = input("\n👉 Enter index number to export (or 'all' to export all): ").strip()

# === DETERMINE WHICH INDICES TO EXPORT ===
if choice.lower() == "all":
    selected_indices = index_names
else:
    try:
        idx_num = int(choice)
        if 1 <= idx_num <= len(index_names):
            selected_indices = [index_names[idx_num - 1]]
        else:
            print("⚠️ Invalid choice. Exiting.")
            exit()
    except ValueError:
        print("⚠️ Invalid input. Exiting.")
        exit()

# === FETCH AND EXPORT DATA ===
for index_name in selected_indices:
    print(f"\n🔍 Fetching data from index: {index_name}")

    # Fetch up to 10,000 documents (can be increased or scrolled)
    result = es.search(index=index_name, body={"query": {"match_all": {}}}, size=10000)

    if 'hits' not in result or len(result['hits']['hits']) == 0:
        print(f"⚠️ No data found in index: {index_name}")
        continue

    # Extract _source data
    data = [doc['_source'] for doc in result['hits']['hits']]

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Save to CSV
    csv_path = os.path.join(OUTPUT_DIR, f"{index_name}.csv")
    df.to_csv(csv_path, index=False)
    print(f"✅ Saved {len(df)} records to {csv_path}")

print("\n🎉 Export complete!")
