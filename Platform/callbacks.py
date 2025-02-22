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
         Output("cumulative-claims", "figure"),  # New output
         Output("claims-distribution", "figure"),  # New output
         Output("reserve-summary", "children"),  # New output
         Output("upload-data", "style"),  # Hide upload section after upload
         Output("heatmap-triangle", "style"),  # Control heatmap visibility
         Output("bar-factors", "style"),  # Control bar chart visibility
         Output("line-projection", "style"),  # Control line plot visibility
         Output("cumulative-claims", "style"),  # New output
         Output("claims-distribution", "style"),  # New output
         Output("reserve-summary", "style")],  # New output
        [Input("upload-data", "contents")],  # Input for file upload
        [State("upload-data", "filename")]  # State for filename
    )
    def update_output(contents, filename):
        if contents is None:
            # No file uploaded yet
            return (
                ["Please upload a CSV file.", {}, {}, {}, {}, {}, {}, {"display": "block"}],  # Show upload button
                {"display": "none"},  # Hide heatmap
                {"display": "none"},  # Hide bar chart
                {"display": "none"},  # Hide line plot
                {"display": "none"},  # Hide cumulative claims plot
                {"display": "none"},  # Hide claims distribution plot
                {"display": "none"},  # Hide reserve summary
            )
        
        df = parse_contents(contents, filename)
        if df is None or df.empty:
            # Error processing file
            return (
                ["Error processing file or file is empty.", {}, {}, {}, {}, {}, {}, {"display": "block"}],  # Show upload button
                {"display": "none"},  # Hide heatmap
                {"display": "none"},  # Hide bar chart
                {"display": "none"},  # Hide line plot
                {"display": "none"},  # Hide cumulative claims plot
                {"display": "none"},  # Hide claims distribution plot
                {"display": "none"},  # Hide reserve summary
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
        
        # --- Plot 4: Cumulative Claims Over Time ---
        cumulative_fig = px.line(
            df.groupby('Date Survenance')['Règlement'].sum().cumsum().reset_index(),
            x='Date Survenance',
            y='Règlement',
            title="Cumulative Claims Over Time"
        )
        
        # --- Plot 5: Claims Distribution by Year ---
        claims_dist_fig = px.histogram(
            df,
            x='Accident Year',
            y='Règlement',
            histfunc='sum',
            title="Claims Distribution by Accident Year"
        )
        
        # --- Table: Reserve Summary ---
        reserve_summary = df.groupby('Accident Year')['Règlement'].sum().reset_index()
        reserve_summary['Projected Ultimate'] = [ultimate[i] for i in range(len(reserve_summary))]
        reserve_summary['Reserve'] = reserve_summary['Projected Ultimate'] - reserve_summary['Règlement']
        
        reserve_table = dash.dash_table.DataTable(
            data=reserve_summary.to_dict("records"),
            columns=[{"name": i, "id": i} for i in reserve_summary.columns],
            page_size=10,
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
            cumulative_fig,  # Cumulative claims figure
            claims_dist_fig,  # Claims distribution figure
            reserve_table,  # Reserve summary table
            {"display": "none"},  # Hide upload button
            {"display": "block"},  # Show heatmap
            {"display": "block"},  # Show bar chart
            {"display": "block"},  # Show line plot
            {"display": "block"},  # Show cumulative claims plot
            {"display": "block"},  # Show claims distribution plot
            {"display": "block"},  # Show reserve summary
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

    # New callback for model selection
    @app.callback(
        Output("selected-model-output", "children"),  # Placeholder for model selection output
        [Input("reserving-model-dropdown", "value")]
    )
    def update_model_selection(selected_model):
        # Log the selected model (for now)
        print(f"Selected Model: {selected_model}")
        return f"Selected Model: {selected_model}"
    
    @app.callback(
    Output("model-selection-row", "style"),  # Control visibility of the model selection row
    [Input("upload-data", "contents"),  # Triggered when data is uploaded
     Input("reserving-model-dropdown", "value")],  # Triggered when a model is selected
    [State("upload-data", "filename")]  # State for filename
    )
    def hide_model_selection(contents, selected_model, filename):
    # Hide the model selection row if data is uploaded and a model is selected
        if contents is not None and selected_model is not None:
            return {"display": "none"}  # Hide the row
        return {"display": "block"}  # Show the rowi
    
    