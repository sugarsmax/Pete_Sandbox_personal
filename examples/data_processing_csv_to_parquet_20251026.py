"""
CSV to Parquet Conversion Example

Demonstrates efficient data loading, transformation, and conversion to Parquet format.
Parquet is compressed and columnar, ideal for analytics workflows.
"""

import pandas as pd
import pyarrow.parquet as pq
import os

# Example: Load CSV and convert to Parquet
def csv_to_parquet(csv_path: str, output_path: str, sample_size: int = 1000):
    """
    Convert CSV file to Parquet format with type optimization.
    
    Args:
        csv_path: Path to input CSV file
        output_path: Path to output Parquet file
        sample_size: Number of rows to read (None for all)
    """
    # Load CSV (infer types automatically)
    df = pd.read_csv(csv_path, nrows=sample_size)
    
    # Optional: Optimize data types to reduce file size
    df = optimize_dtypes(df)
    
    # Write to Parquet with compression
    df.to_parquet(output_path, compression='snappy', index=False)
    
    print(f"✓ Converted {len(df)} rows to {output_path}")
    print(f"  Original CSV size: {os.path.getsize(csv_path) / 1024:.1f} KB")
    print(f"  Parquet size: {os.path.getsize(output_path) / 1024:.1f} KB")


def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize DataFrame data types to reduce memory usage.
    
    Converts:
    - object strings to category when appropriate
    - float64 to float32 where precision allows
    - int64 to smaller int types
    """
    for col in df.columns:
        col_type = df[col].dtype
        
        # String columns → category (if <50% unique values)
        if col_type == 'object':
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio < 0.5:
                df[col] = df[col].astype('category')
        
        # Numeric optimization
        elif col_type == 'int64':
            max_val = df[col].max()
            if max_val < 32767:
                df[col] = df[col].astype('int16')
            elif max_val < 2147483647:
                df[col] = df[col].astype('int32')
        
        elif col_type == 'float64':
            df[col] = df[col].astype('float32')
    
    return df


# Usage example
if __name__ == "__main__":
    # csv_to_parquet(
    #     csv_path="data/sample.csv",
    #     output_path="data/sample.parquet",
    #     sample_size=10000
    # )
    pass
