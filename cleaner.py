import pandas as pd
import argparse
import os


def load_data(file_path):
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, na_values=["NA"])
        elif file_path.endswith(".xls") or file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path, engine="xlrd")
        else:
            raise ValueError("Unsupported file format")

        print("Data loaded successfully")
        return df

    except Exception as e:
        print("Error:", e)
        return None


def clean_data(df):
    report = []

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    report.append("Standard column names")

    # Remove dupes
    before = len(df)
    df = df.drop_duplicates()
    report.append(f"Removed {before - len(df)} duplicate rows")

    # Missing values
    missing = df.isnull().sum()
    report.append(f"Missing values:\n{missing}")

    # Fill NA
    for col in df.columns:
        if df[col].dtype in ["float64", "int64"]:
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna("Unknown")

    report.append("Handled missing values")

    # numeric 
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")

    # Outlier detection (IQR)
    outlier_info = []
    for col in df.select_dtypes(include=["float64", "int64"]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower) | (df[col] > upper)]
        outlier_info.append(f"{col}: {len(outliers)} outliers")

        df[col] = df[col].clip(lower, upper)

    report.append("Outlier summary:\n" + "\n".join(outlier_info))

    # statistic
    report.append("Data summary:\n" + str(df.describe()))

    return df, report


def save_outputs(df, report, output_prefix):
    cleaned_file = f"{output_prefix}_cleaned.csv"
    report_file = f"{output_prefix}_report.txt"

    df.to_csv(cleaned_file, index=False)

    with open(report_file, "w") as f:
        for line in report:
            f.write(line + "\n\n")

    print(f"Saved: {cleaned_file}")
    print(f"Saved: {report_file}")


def main():
    parser = argparse.ArgumentParser(description="Data Cleaning Tool")
    parser.add_argument("file", help="Input CSV/XLS file")

    args = parser.parse_args()

    df = load_data(args.file)

    if df is not None:
        cleaned_df, report = clean_data(df)

        name = os.path.splitext(os.path.basename(args.file))[0]
        save_outputs(cleaned_df, report, name)

        print("Cleaning complete")


if __name__ == "__main__":
    main()
