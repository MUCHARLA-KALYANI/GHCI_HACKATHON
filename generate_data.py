import json
import random
import pandas as pd
from faker import Faker
from sklearn.model_selection import train_test_split

# 1. Load the Taxonomy
try:
    with open('taxonomy.json', 'r') as f:
        taxonomy = json.load(f)['categories']
except FileNotFoundError:
    print("Error: taxonomy.json not found.")
    exit()

# Set up Faker for generating realistic identifiers
fake = Faker()
N_SAMPLES = 15000  # Target size of the training set

# Prepare data structure for generation based on weights
category_choices = []
weights = []
for cat in taxonomy:
    category_choices.append(cat)
    weights.append(cat['weight'])

# 2. Define Noise Patterns (Crucial for Robustness)
POS_PREFIXES = ["VISA POS ", "DEBIT PURCHASE ", "EFT ", "POS SALE ", "CARD PURCHASE "]
NOISE_SUFFIXES = [
    f" ID:{fake.bban()}",
    f" LOC:{fake.city_prefix()}{random.randint(1000, 9999)}",
    f" T:{fake.date_of_birth().strftime('%m%d%y')}",
    f" {random.randint(100, 999)}",
    "" # For clean strings
]

def generate_transaction(category_data):
    """Generates one synthetic transaction string and its label."""
    category_name = category_data['name']
    
    # 2.1 Core Merchant: Pick a random keyword/seed
    merchant = random.choice(category_data['keywords'])
    
    # 2.2 Add Prefixes (POS/EFT/etc.) - Use for non-Transfer categories
    if category_name not in ["Transfer/Income", "Utilities"]:
        prefix = random.choice(POS_PREFIXES)
    else:
        prefix = ""
        
    # 2.3 Add Noise/Identifier Suffixes - Use for all categories 50% of the time
    suffix = random.choice(NOISE_SUFFIXES) if random.random() < 0.5 else ""

    # Combine parts: {Prefix} {Merchant} {Suffix}
    raw_string = f"{prefix}{merchant}{suffix}".upper().strip()
    
    return raw_string, category_name

# 3. Generate the Dataset
data = []
# Randomly sample categories based on their defined weights
for _ in range(N_SAMPLES):
    chosen_category = random.choices(category_choices, weights=weights, k=1)[0]
    
    raw_text, category_label = generate_transaction(chosen_category)
    data.append([raw_text, category_label])

# 4. Save and Split Data
df = pd.DataFrame(data, columns=['raw_transaction_string', 'category_label'])

# Split the data (80/10/10 as planned)
train_df, test_val_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['category_label'])
val_df, test_df = train_test_split(test_val_df, test_size=0.5, random_state=42, stratify=test_val_df['category_label'])

# Save the final splits (Crucial for Reproducibility)
train_df.to_csv('data/train.csv', index=False)
val_df.to_csv('data/validation.csv', index=False)
test_df.to_csv('data/test.csv', index=False) 

print(f"Generated {N_SAMPLES} samples. Saved Train, Validation, and Test sets.")