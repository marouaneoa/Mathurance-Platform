from dash import Input, Output, State
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import parse_contents, create_triangle, compute_chain_ladder_factors, project_triangle
from layout import home_layout, about_layout, scenario_analysis_layout
from dash import html
import dash
import pandas as pd

def register_callbacks(app):
    # Callback to store uploaded data
    @app.callback(
        Output("stored-data", "data"),
        [Input("upload-data", "contents")],
        [State("upload-data", "filename")]
    )
    def store_uploaded_data(contents, filename):
        if contents is None:
            raise dash.exceptions.PreventUpdate
        df = parse_contents(contents, filename)
        return df.to_dict("records") if df is not None else None

    # Callback to update the home page outputs
    @app.callback(
        [Output("output-data-upload", "children"),
         Output("heatmap-triangle", "figure"),
         Output("bar-factors", "figure"),
         Output("line-projection", "figure"),
         Output("cumulative-claims", "figure"),
         Output("claims-distribution", "figure"),
         Output("reserve-summary", "children"),
         Output("upload-data", "style"),
         Output("heatmap-triangle", "style"),
         Output("bar-factors", "style"),
         Output("line-projection", "style"),
         Output("cumulative-claims", "style"),
         Output("claims-distribution", "style"),
         Output("reserve-summary", "style")],
        [Input("stored-data", "data")]
    )
    def update_home_page(stored_data):
        if stored_data is None:
            # No file uploaded yet
            return (
                ["Please upload a CSV file.", {}, {}, {}, {}, {}, {}, {"display": "block"}],
                {"display": "none"},  # Hide heatmap
                {"display": "none"},  # Hide bar chart
                {"display": "none"},  # Hide line plot
                {"display": "none"},  # Hide cumulative claims plot
                {"display": "none"},  # Hide claims distribution plot
                {"display": "none"},  # Hide reserve summary
            )

        df = pd.DataFrame(stored_data)
        if df.empty:
            # Error processing file
            return (
                ["Error processing file or file is empty.", {}, {}, {}, {}, {}, {}, {"display": "block"}],
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
            html.H5(f"File uploaded and processed."),
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

    # Callback to display the correct page
    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')]
    )
    def display_page(pathname):
        if pathname == '/scenario-analysis':
            return scenario_analysis_layout
        elif pathname == '/about':
            return about_layout
        else:
            return home_layout

    # Callback to toggle sidebar
    @app.callback(
        Output("sidebar", "is_open"),
        [Input("sidebar-toggle", "n_clicks")],
        [State("sidebar", "is_open")]
    )
    def toggle_sidebar(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    # Callback to update scenario analysis
    # Callback to update scenario analysis with additional features
    @app.callback(
    [Output("scenario-line-plot", "figure"),
     Output("scenario-summary-table", "children"),
     Output("inflation-trend-plot", "figure"),
     Output("claims-by-product-plot", "figure"),
     Output("claims-by-sub-branch-plot", "figure"),
     Output("claims-forecast-plot", "figure")],
    [Input("stored-data", "data"),
     Input("inflation-rate-2024", "value"),
     Input("inflation-rate-2025", "value"),
     Input("dev-factor-1-2", "value"),
     Input("dev-factor-2-3", "value")]
    )
    def update_scenario_analysis(stored_data, inflation_2024, inflation_2025, dev_factor_1_2, dev_factor_2_3):
        if stored_data is None:
            raise dash.exceptions.PreventUpdate

        df = pd.DataFrame(stored_data)

        # Example historical inflation data
        inflation_data = {
            "year": list(range(1998, 2024)),
            "inflation": [5.0, 2.6, 0.3, 4.2, 1.4, 4.3, 4.0, 1.4, 2.3, 3.7, 4.9, 5.7, 3.9, 4.5, 8.9, 3.3, 2.9, 4.8, 6.4, 5.7, 4.3, 2.0, 2.4, 7.2, 9.3]
        }
        inflation_df = pd.DataFrame(inflation_data)

        # Add user-defined inflation rates for 2024 and 2025
        inflation_df = inflation_df.append(
            {"year": 2024, "inflation": inflation_2024}, ignore_index=True
        )
        inflation_df = inflation_df.append(
            {"year": 2025, "inflation": inflation_2025}, ignore_index=True
        )

        # Adjust claims based on development factors and inflation
        df["adjusted_claims"] = df["Règlement"] * dev_factor_1_2 * dev_factor_2_3
        df["adjusted_claims"] *= (1 + inflation_df.set_index("year").loc[df["Accident Year"], "inflation"].values / 100)

        # Forecast claims for 2024 and 2025
        forecast_years = [2024, 2025]
        forecast_claims = [
            df["adjusted_claims"].iloc[-1] * (1 + inflation_df.set_index("year").loc[year, "inflation"] / 100)
            for year in forecast_years
        ]
        forecast_df = pd.DataFrame({
            "year": forecast_years,
            "claims": forecast_claims,
        })

        # Combine historical and forecasted claims
        combined_df = pd.concat([df, forecast_df])

        # --- Plot 1: Adjusted Claims Over Time ---
        line_fig = px.line(
            combined_df,
            x="year",
            y="adjusted_claims",
            labels={"x": "Year", "y": "Adjusted Claims"},
            title="Scenario Analysis: Adjusted Claims Over Time"
        )

        # --- Plot 2: Inflation Rate Trends ---
        inflation_fig = px.line(
            inflation_df,
            x="year",
            y="inflation",
            labels={"x": "Year", "y": "Inflation Rate (%)"},
            title="Inflation Rate Trends"
        )

        # --- Plot 3: Claims Distribution by Product ---
        claims_by_product = df.groupby("Désignation Produit")["Règlement"].sum().reset_index()
        claims_by_product_fig = px.bar(
            claims_by_product,
            x="Désignation Produit",
            y="Règlement",
            labels={"x": "Product", "y": "Total Claims"},
            title="Claims Distribution by Product"
        )

        # --- Plot 4: Claims Distribution by Sub-Branch ---
        claims_by_sub_branch = df.groupby("Sous-Branche")["Règlement"].sum().reset_index()
        claims_by_sub_branch_fig = px.bar(
            claims_by_sub_branch,
            x="Sous-Branche",
            y="Règlement",
            labels={"x": "Sub-Branch", "y": "Total Claims"},
            title="Claims Distribution by Sub-Branch"
        )

        # --- Plot 5: Claims Forecast by Development Period ---
        claims_forecast_fig = px.line(
            combined_df,
            x="year",
            y="adjusted_claims",
            labels={"x": "Year", "y": "Adjusted Claims"},
            title="Claims Forecast by Development Period"
        )

        # Create summary table
        summary_table = dash.dash_table.DataTable(
            data=combined_df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in combined_df.columns],
            page_size=10,
        )

        return (
            line_fig,  # Adjusted Claims Over Time
            summary_table,  # Summary Table
            inflation_fig,  # Inflation Rate Trends
            claims_by_product_fig,  # Claims Distribution by Product
            claims_by_sub_branch_fig,  # Claims Distribution by Sub-Branch
            claims_forecast_fig,  # Claims Forecast by Development Period
        )