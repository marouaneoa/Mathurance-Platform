import base64
import io
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------
# Data Preprocessing and Chain-Ladder Pipeline Functions
# -----------------------------------------------------------
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

# -----------------------------------------------------------
# Dash App Setup and Layout
# -----------------------------------------------------------
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Chain-Ladder Dashboard"

app.layout = dbc.Container([
    html.H1("Chain-Ladder Analysis Platform", className="my-4"),
    dcc.Upload(
        id="upload-data",
        children=html.Div([
            "Drag and Drop or ",
            html.A("Select a CSV File")
        ]),
        style={
            "width": "100%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "margin": "10px"
        },
        multiple=False
    ),
    html.Div(id="output-data-upload"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="heatmap-triangle"), md=6),
        dbc.Col(dcc.Graph(id="bar-factors"), md=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="line-projection"), md=12)
    ])
], fluid=True)

# -----------------------------------------------------------
# Dash Callback to Process the Uploaded File and Generate Plots
# -----------------------------------------------------------
@app.callback(
    [Output("output-data-upload", "children"),
     Output("heatmap-triangle", "figure"),
     Output("bar-factors", "figure"),
     Output("line-projection", "figure")],
    [Input("upload-data", "contents")],
    [State("upload-data", "filename")]
)
def update_output(contents, filename):
    if contents is None:
        return ["Please upload a CSV file.", {}, {}, {}]
    
    df = parse_contents(contents, filename)
    if df is None or df.empty:
        return ["Error processing file or file is empty.", {}, {}, {}]

    # Create the claims triangle (cumulative)
    triangle = create_triangle(df)
    
    # Compute Chain-Ladder factors
    factors = compute_chain_ladder_factors(triangle)
    
    # Project the ultimate claims using the Chain-Ladder method
    triangle_proj = project_triangle(triangle, factors)
    
    # --- Plot 1: Heatmap of the Claims Triangle ---
    heatmap_fig = px.imshow(
        triangle,
        text_auto=True,
        aspect="auto",
        labels=dict(x="Development Period", y="Accident Year", color="Cumulative Claims"),
        x=[f"Period {col}" for col in triangle.columns],
        y=triangle.index.astype(str)
    )
    heatmap_fig.update_layout(title="Claims Triangle (Cumulative)")
    
    # --- Plot 2: Bar Chart of Chain-Ladder Development Factors ---
    factor_keys = list(factors.keys())
    factor_values = [factors[k] for k in factor_keys]
    bar_fig = px.bar(
        x=[f"Period {k} to {k+1}" for k in factor_keys],
        y=factor_values,
        labels={"x": "Development Period", "y": "Factor"},
        text=np.round(factor_values, 2)
    )
    bar_fig.update_layout(title="Development Factors (Chain-Ladder)")
    
    # --- Plot 3: Line Plot for Actual vs. Projected Ultimate Claims ---
    accident_years = triangle.index.tolist()
    actual = []
    ultimate = []
    for year in accident_years:
        # Last known cumulative value from the original triangle
        row = triangle.loc[year].dropna()
        last_known_period = row.index.max() if not row.empty else None
        actual_val = row[last_known_period] if last_known_period is not None else np.nan
        # Ultimate claim from the projected triangle (last period column)
        ultimate_val = triangle_proj.loc[year, triangle_proj.columns.max()]
        actual.append(actual_val)
        ultimate.append(ultimate_val)
    
    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(
        x=accident_years, y=actual,
        mode="lines+markers",
        name="Last Known Cumulative Claims"
    ))
    line_fig.add_trace(go.Scatter(
        x=accident_years, y=ultimate,
        mode="lines+markers",
        name="Projected Ultimate Claims"
    ))
    line_fig.update_layout(
        title="Actual vs. Projected Ultimate Claims by Accident Year",
        xaxis_title="Accident Year",
        yaxis_title="Claims Amount"
    )
    
    children = html.Div([
        html.H5(f"File {filename} successfully uploaded and processed."),
        html.H6("Data Preview:"),
        dash.dash_table.DataTable(
            data=df.head(10).to_dict("records"),
            columns=[{"name": i, "id": i} for i in df.columns],
            page_size=10,
        )
    ])
    
    return children, heatmap_fig, bar_fig, line_fig

# -----------------------------------------------------------
# Run the Dash App
# -----------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
