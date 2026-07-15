import json
import numpy as np
import pandas as pd


def to_python(value):
    """
    Convert NumPy/Pandas types into native Python types.
    """

    if pd.isna(value):
        return None

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        return float(value)

    if isinstance(value, np.bool_):
        return bool(value)

    return value


def profile_dataset(df):
    """
    Generate a statistical profile of the dataset.
    Returns a JSON-compatible dictionary.
    """

    profile = {}


    # Dataset Info

    profile["dataset_info"] = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist()
    }


    # Data Types
    profile["data_types"] = {col: str(dtype)
        for col, dtype in df.dtypes.items()
    }

    
    # Column Categories
    

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    datetime_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

    profile["numeric_columns"] = numeric_cols
    profile["categorical_columns"] = categorical_cols
    profile["datetime_columns"] = datetime_cols

    
    # Missing Values

    profile["missing_values"] = {
        col: int(count)
        for col, count in df.isnull().sum().items()
    }

    
    # Duplicate Rows
    

    profile["duplicates"] = int(df.duplicated().sum())

    
    # Summary Statistics
    summary = {}

    for col in numeric_cols:

        summary[col] = {

            "count": to_python(df[col].count()),
            "mean": round(float(df[col].mean()), 2),
            "median": round(float(df[col].median()), 2),
            "std": round(float(df[col].std()), 2),
            "variance": round(float(df[col].var()), 2),
            "min": to_python(df[col].min()),
            "max": to_python(df[col].max()),
            "skewness": round(float(df[col].skew()), 2),
            "kurtosis": round(float(df[col].kurt()), 2)
        }

        profile["summary_statistics"] = summary

    
    
    # Correlation Matrix


    correlation = (
        df[numeric_cols]
        .corr()
        .round(2)
        .fillna(0)
    )

    profile["correlation_matrix"] = correlation.to_dict()

    
    # Outlier Detection (IQR)


    outliers = {}

    for col in numeric_cols:

        q1 = df[col].quantile(0.25)

        q3 = df[col].quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr

        upper = q3 + 1.5 * iqr

        count = df[
            (df[col] < lower) |
            (df[col] > upper)
        ].shape[0]

        outliers[col] = int(count)

    profile["outliers"] = outliers
    profile["status"] = "success"

    return profile


if __name__ == "__main__":

    print("Profiler Agent Ready")