from src.data import get_merchant_files, get_merchant, load_data


# Test finding all merchants
merchants = get_merchant_files()

print("\n--- AVAILABLE MERCHANTS ---")

for merchant in merchants:
    print(merchant["merchant"])


# Test loading one merchant
merchant = get_merchant("cheekbonebeauty")

print("\n--- SELECTED MERCHANT ---")
print(merchant)


products, reviews = load_data(
    merchant["products"],
    merchant["reviews"]
)


print("\n--- PRODUCTS ---")
print(products.shape)

print("\n--- REVIEWS ---")
print(reviews.shape)

print("\n--- REVIEW SAMPLE ---")
print(reviews.head())