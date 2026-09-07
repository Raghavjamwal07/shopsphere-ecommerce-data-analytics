from pathlib import Path
import pandas as pd


# --------------------------------------------------
# ShopSphere E-commerce Data Automation Pipeline
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "ShopSphere_Looker_Ecommerce.csv"
OUTPUT_FILE = BASE_DIR / "data" / "ShopSphere_Final_Processed.csv"


def load_data():
    """Load the raw ShopSphere dataset."""
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
        )

    return pd.read_csv(INPUT_FILE)


def clean_data(df):
    """Clean and standardize the dataset."""

    df = df.copy()

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Remove completely empty rows
    df = df.dropna(how="all")

    # Remove duplicate records
    df = df.drop_duplicates()

    # Clean text columns
    text_columns = df.select_dtypes(include=["object"]).columns

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()

    # Standardize ID columns
    for column in ["order_id", "customer_id", "product_id"]:
        if column in df.columns:
            df[column] = df[column].astype("string").str.strip()

    # Convert dates
    for column in ["order_date", "signup_date"]:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    # Convert numeric columns
    for column in [
        "age",
        "quantity",
        "unit_price",
        "total_amount"
    ]:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


def transform_data(df):
    """Create analytical fields."""

    df = df.copy()

    # Date features
    if "order_date" in df.columns:
        df["order_year"] = df["order_date"].dt.year
        df["order_month"] = df["order_date"].dt.month
        df["order_month_name"] = (
            df["order_date"].dt.month_name()
        )
        df["order_quarter"] = df["order_date"].dt.quarter
        df["order_day"] = df["order_date"].dt.day
        df["order_weekday"] = (
            df["order_date"].dt.day_name()
        )

    # Sales validation
    if all(
        column in df.columns
        for column in [
            "quantity",
            "unit_price",
            "total_amount"
        ]
    ):
        df["calculated_total_amount"] = (
            df["quantity"] * df["unit_price"]
        )

        df["amount_difference"] = (
            df["total_amount"]
            - df["calculated_total_amount"]
        )

    # Order count
    if "order_id" in df.columns:
        df["order_count"] = 1

    # Customer age groups
    if "age" in df.columns:
        df["age_group"] = pd.cut(
            df["age"],
            bins=[0, 18, 25, 35, 45, 55, 65, 120],
            labels=[
                "Under 18",
                "18-25",
                "26-35",
                "36-45",
                "46-55",
                "56-65",
                "66+"
            ],
            include_lowest=True
        )

    return df


def validate_data(df):
    """Run automated data-quality checks."""

    missing_values = df.isnull().sum().sum()
    duplicates = df.duplicated().sum()

    negative_quantity = (
        (df["quantity"] < 0).sum()
        if "quantity" in df.columns
        else 0
    )

    amount_mismatches = (
        (df["amount_difference"].abs() > 0.01).sum()
        if "amount_difference" in df.columns
        else 0
    )

    checks_passed = (
        missing_values == 0
        and duplicates == 0
        and negative_quantity == 0
        and amount_mismatches == 0
    )

    print("\nDATA QUALITY CHECKS")
    print("-" * 40)
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Missing values:", missing_values)
    print("Duplicate records:", duplicates)
    print("Negative quantity records:", negative_quantity)
    print("Amount mismatches:", amount_mismatches)

    if not checks_passed:
        raise ValueError(
            "Data quality validation failed."
        )

    print("\nALL AUTOMATION TESTS PASSED")


def save_data(df):
    """Save the final processed dataset."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nFINAL DATASET CREATED")
    print("-" * 40)
    print("Output:", OUTPUT_FILE)
    print("Rows:", len(df))
    print("Columns:", len(df.columns))


def main():
    print("=" * 60)
    print("SHOPSPHERE AUTOMATION PIPELINE")
    print("=" * 60)

    raw_df = load_data()

    print("\nRaw dataset:")
    print(raw_df.shape)

    clean_df = clean_data(raw_df)

    print("\nAfter cleaning:")
    print(clean_df.shape)

    final_df = transform_data(clean_df)

    print("\nAfter transformation:")
    print(final_df.shape)

    validate_data(final_df)
    save_data(final_df)

    print("\nPIPELINE COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
