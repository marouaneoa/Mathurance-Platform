import base64
import io
import pandas as pd
import numpy as np


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif filename.endswith(('.xls', '.xlsx', '.xlsm')):  # Added .xlsm support
            df = pd.read_excel(io.BytesIO(decoded))
        elif filename.endswith('.json'):
            df = pd.read_json(io.StringIO(decoded.decode('utf-8')))
        else:
            return None  # Unsupported file format
        
        # Clean up column names
        df.columns = [col.strip() for col in df.columns]

        # Convert settlement amounts to numeric
        df['Règlement'] = pd.to_numeric(df['Règlement'], errors='coerce')
        
        # Convert Date Survenance to datetime format
        df['Date Survenance'] = pd.to_datetime(df['Date Survenance'], errors='coerce')
        
        # Create a new column for Accident Year from the Date Survenance
        df['Accident Year'] = df['Date Survenance'].dt.year
        
        # Compute the development period as the difference between the settlement year (Exercice) and the accident year
        df['Development Period'] = df['Exercice'] - df['Accident Year']
        
        # Filter out any rows with negative development periods
        df = df[df['Development Period'] >= 0]

        return df
    
    except Exception as e:
        print("Error reading file:", e)
        return None

def create_triangle(df):
    """
    Create a cumulative claims triangle.
    Rows: Accident Year
    Columns: Development Period (in years)
    Values: Cumulative sum of the settlement amounts (Règlement)
    """
    # Aggregate the settlement amounts by accident year and development period
    triangle = (
        df.groupby(['Accident Year', 'Development Period'])['Règlement']
          .sum()
          .reset_index()
    )
    # Pivot the data so that rows are accident years and columns are development periods
    triangle_pivot = triangle.pivot(index='Accident Year', columns='Development Period', values='Règlement')
    triangle_pivot = triangle_pivot.sort_index().sort_index(axis=1)
    # Convert incremental values to cumulative amounts along the row
    triangle_cumulative = triangle_pivot.cumsum(axis=1)
    return triangle_cumulative

def compute_chain_ladder_factors(triangle):
    """
    Compute development factors for each development period.
    For each column (except the last), the factor is calculated as:
         factor = (sum of claims in next period) / (sum of claims in current period)
    If the next period column doesn't exist, the factor is set to NaN.
    """
    factors = {}
    columns = sorted(triangle.columns)
    for col in columns[:-1]:
        next_col = col + 1
        if next_col not in triangle.columns:
            factors[col] = np.nan
            continue
        valid = triangle[[col, next_col]].dropna()
        if not valid.empty and valid[col].sum() != 0:
            factor = valid[next_col].sum() / valid[col].sum()
            factors[col] = factor
        else:
            factors[col] = np.nan
    return factors

def project_triangle(triangle, factors):
    """
    Using the computed development factors, project the ultimate claims for each accident year.
    For accident years with missing future periods, the projection is done by multiplying the
    last known cumulative claim amount by the product of the remaining factors.
    """
    triangle_proj = triangle.copy()
    max_period = max(triangle.columns)  # highest development period present in the data
    for idx, row in triangle_proj.iterrows():
        # Identify the last development period with available data
        known_periods = row.dropna().index.tolist()
        if not known_periods:
            continue
        last_known = max(known_periods)
        last_val = row[last_known]
        # Project for remaining periods if any
        for dev in range(last_known + 1, max_period + 1):
            # Use the factor from the previous period; if missing, default to 1 (no change)
            factor = factors.get(dev - 1, 1)
            last_val *= factor
            triangle_proj.at[idx, dev] = last_val
    return triangle_proj