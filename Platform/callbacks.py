from dash import Input, Output, State
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import parse_contents, create_triangle, compute_chain_ladder_factors, project_triangle
from layout import home_layout, about_layout
from dash import html
import dash

def register_callbacks(app):
    @app.callback(
        [Output("output-data-upload", "children"),
         Output("heatmap-triangle", "figure"),
         Output("bar-factors", "figure"),
         Output("line-projection", "figure"),
         Output("upload-data", "style"),  # Hide upload section after upload
         Output("heatmap-triangle", "style"),  # Control heatmap visibility
         Output("bar-factors", "style"),  # Control bar chart visibility
         Output("line-projection", "style")],  # Control line plot visibility
        [Input("upload-data", "contents")],  # Input for file upload
        [State("upload-data", "filename")]  # State for filename
    )
    def update_output(contents, filename):
        if contents is None:
            # No file uploaded yet
            return (
                ["Please upload a CSV file.", {}, {}, {}, {"display": "block"}],  # Show upload button
                {"display": "none"},  # Hide heatmap
                {"display": "none"},  # Hide bar chart
                {"display": "none"},  # Hide line plot
            )
        
        df = parse_contents(contents, filename)
        if df is None or df.empty:
            # Error processing file
            return (
                ["Error processing file or file is empty.", {}, {}, {}, {"display": "block"}],  # Show upload button
                {"display": "none"},  # Hide heatmap
                {"display": "none"},  # Hide bar chart
                {"display": "none"},  # Hide line plot
            )

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
        
        # Create the table and message
        children = html.Div([
            html.H5(f"File {filename} successfully uploaded and processed."),
            html.H6("Data Preview:"),
            dash.dash_table.DataTable(
                data=df.head(10).to_dict("records"),
                columns=[{"name": i, "id": i} for i in df.columns],
                page_size=10,
            )
        ])
        
        # Show plots and table after successful upload
        return (
            children,  # Table and message
            heatmap_fig,  # Heatmap figure
            bar_fig,  # Bar chart figure
            line_fig,  # Line plot figure
            {"display": "none"},  # Hide upload button
            {"display": "block"},  # Show heatmap
            {"display": "block"},  # Show bar chart
            {"display": "block"},  # Show line plot
        )

    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')]
    )
    def display_page(pathname):
        if pathname == '/about':
            return about_layout
        else:
            return home_layout

    @app.callback(
        Output("sidebar", "is_open"),
        [Input("sidebar-toggle", "n_clicks")],
        [State("sidebar", "is_open")]
    )
    def toggle_sidebar(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open