"""
Data Cleaning and Transformation Example

Demonstrates common data quality issues and how to fix them:
- Missing values
- Duplicates
- Type conversions
- Outlier detection
"""

import pandas as pd
import numpy as np


def clean_data(df: pd.DataFrame, drop_duplicates: bool = True) -> pd.DataFrame:
    """
    Comprehensive data cleaning pipeline.
    
    Args:
        df: Input DataFrame
        drop_duplicates: Whether to remove duplicate rows
        
    Returns:
        Cleaned DataFrame
    """
    df = df.copy()
    
    print(f"Starting with {len(df)} rows, {df.isnull().sum().sum()} nulls")
    
    # 1. Remove duplicates
    if drop_duplicates:
        df = df.drop_duplicates()
        print(f"After dedup: {len(df)} rows")
    
    # 2. Handle missing values
    df = handle_missing_values(df)
    
    # 3. Standardize columns
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    # 4. Convert data types
    df = convert_types(df)
    
    # 5. Remove/flag outliers
    df = flag_outliers(df)
    
    print(f"Final: {len(df)} rows")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values by column type."""
    for col in df.columns:
        missing_pct = df[col].isnull().sum() / len(df) * 100
        
        if missing_pct > 50:
            # Drop columns with >50% missing
            df = df.drop(columns=[col])
            print(f"  Dropped {col} ({missing_pct:.1f}% null)")
        
        elif missing_pct > 0:
            if df[col].dtype in ['float64', 'int64']:
                # Fill numeric with median
                df[col] = df[col].fillna(df[col].median())
            else:
                # Fill categorical with mode
                df[col] = df[col].fillna(df[col].mode()[0])
            print(f"  Filled {col} ({missing_pct:.1f}% null)")
    
    return df


def convert_types(df: pd.DataFrame) -> pd.DataFrame:
    """Attempt automatic type conversion."""
    for col in df.columns:
        # Try numeric
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass
            
            # Try datetime
            try:
                df[col] = pd.to_datetime(df[col])
            except (ValueError, TypeError):
                pass
    
    return df


def flag_outliers(df: pd.DataFrame, iqr_multiplier: float = 1.5) -> pd.DataFrame:
    """
    Flag outliers using IQR method.
    
    Add 'is_outlier' column; doesn't remove rows (preserve data for review).
    """
    df['is_outlier'] = False
    
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - iqr_multiplier * IQR
        upper_bound = Q3 + iqr_multiplier * IQR
        
        outliers = (df[col] < lower_bound) | (df[col] > upper_bound)
        df.loc[outliers, 'is_outlier'] = True
        
        print(f"  Flagged {outliers.sum()} outliers in {col}")
    
    return df


# Usage example
if __name__ == "__main__":
    # Example data with issues
    data = {
        'name': ['Alice', 'Bob', 'Alice', 'Charlie', None],
        'age': [25, None, 25, 150, 28],  # 150 is an outlier
        'salary': ['$50k', '$60k', '$50k', '$75k', '$80k'],
        'date': ['2025-01-01', '2025-01-02', '2025-01-01', '2025-01-03', '2025-01-04']
    }
    
    df = pd.DataFrame(data)
    print("Raw data:")
    print(df)
    print("\n" + "="*50 + "\n")
    
    df_clean = clean_data(df)
    print("\nCleaned data:")
    print(df_clean)
