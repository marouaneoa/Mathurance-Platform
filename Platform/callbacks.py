from dash import Input, Output, State
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import parse_contents, create_triangle, compute_chain_ladder_factors, project_triangle
from layout import home_layout, about_layout, scenario_analysis_layout, upload_section, chatbot_layout
from dash import html, dcc
import dash
from dash.exceptions import PreventUpdate

def register_callbacks(app, model):
    @app.callback(
        [Output("output-data-upload", "children"),
         Output("heatmap-triangle", "figure"),
         Output("bar-factors", "figure"),
         Output("line-projection", "figure"),
         Output("heatmap-triangle", "style"),
         Output("bar-factors", "style"),
         Output("line-projection", "style"),
         Output("chatbot-container", "style"),  # Control chatbot visibility
         Output("chat-history", "children"),  # Update chat history
         Output("user-input", "value"),  # Clear input box
         Output("dynamic-upload-section", "children")],  # Control upload/loading message section
        [Input("upload-data", "contents"),  # Triggered by file upload
         Input("send-button", "n_clicks")],  # Triggered by user input
        [State("upload-data", "filename"),
         State("user-input", "value"),
         State("chat-history", "children")]
    )
    def update_app(contents, n_clicks, filename, user_input, chat_history):
        ctx = dash.callback_context  # Determine which input triggered the callback

        if not ctx.triggered:
            raise PreventUpdate  # No input triggered the callback

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_id == "upload-data":
            if contents is None:
                # No file uploaded yet
                return (
                    ["Please upload a CSV file.", {}, {}, {}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, [], "", upload_section]
                )
            
            # Show the loading message
            loading_message_div = html.Div(
                children=[
                    html.P(
                        "Please wait, your data is being preprocessed...",
                        style={"color": "#1675e0", "fontSize": "18px", "textAlign": "center", "margin": "20px"}
                    )
                ]
            )

            # Parse the uploaded file
            df = parse_contents(contents, filename)
            if df is None or df.empty:
                # Error processing file
                return (
                    ["Error processing file or file is empty.", {}, {}, {}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, [], "", upload_section]
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
                html.H5(f"File {filename} successfully uploaded and processed.", style={"color": "#1675e0", "marginBottom": "20px"}),
                html.H6("Data Preview:", style={"color": "#333333", "marginBottom": "10px"}),
                dash.dash_table.DataTable(
                    data=df.head(10).to_dict("records"),
                    columns=[{"name": i, "id": i} for i in df.columns],
                    page_size=10,
                    style_table={
                        "border": "1px solid #ddd",  # Add border to the table
                        "borderRadius": "5px",  # Rounded corners
                        "overflowX": "auto",  # Enable horizontal scrolling if needed
                    },
                    style_header={
                        "backgroundColor": "#1675e0",  # Header background color
                        "color": "white",  # Header text color
                        "fontWeight": "bold",  # Bold header text
                        "textAlign": "center",  # Center-align header text
                    },
                    style_cell={
                        "textAlign": "left",  # Align cell text to the left
                        "padding": "10px",  # Add padding to cells
                        "border": "1px solid #ddd",  # Add borders to cells
                    },
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},  # Alternate row colors
                            "backgroundColor": "#f9f9f9",  # Light gray for odd rows
                        }
                    ],
                )
            ])
            
            # Generate an interpretation of the plots using Gemini
            interpretation_prompt = f"""
            You are an expert in actuarial science and data visualization. Interpret the following plots:
            1. Heatmap: {heatmap_fig.layout.title.text}
            2. Bar Chart: {bar_fig.layout.title.text}
            3. Line Plot: {line_fig.layout.title.text}

            Provide a detailed analysis of the trends, patterns, and insights from these plots.
            """
            try:
                interpretation = model.generate_content(interpretation_prompt)
                interpretation_message = html.Div(
                    dcc.Markdown(f"**Bot:**\n\n{interpretation.text}"),  # Use Markdown for formatting
                    style={"textAlign": "left", "marginBottom": "10px"}
                )
            except Exception as e:
                interpretation_message = html.Div(
                    html.P(f"In order to keep the data private, local LLM will be integrated and used to interpret data and help in decision making", style={"color": "green"}),
                    style={"textAlign": "left", "marginBottom": "10px"}
                )
            
            # Show plots, table, and chatbot after successful upload
            return (
                children,  # Table and message
                heatmap_fig,  # Heatmap figure
                bar_fig,  # Bar chart figure
                line_fig,  # Line plot figure
                {"display": "block"},  # Show heatmap
                {"display": "block"},  # Show bar chart
                {"display": "block"},  # Show line plot
                {"display": "block"},  # Show chatbot
                [interpretation_message],  # Add interpretation to chat history
                "",  # Clear input box
                html.Div()  # Hide the upload button by returning an empty Div
            )

        elif triggered_id == "send-button":
            # User input triggered the callback
            if n_clicks is None or not user_input:
                raise PreventUpdate  # Do nothing if no input

            # Add user message to chat history
            user_message = html.Div(
                html.P(f"**You:** {user_input}", style={"color": "#1675e0", "fontWeight": "bold"}),
                style={"textAlign": "right", "marginBottom": "10px"}
            )
            chat_history = chat_history + [user_message] if chat_history else [user_message]

            # Get chatbot response using Gemini API
            try:
                response = model.generate_content(user_input)
                bot_message = html.Div(
                    dcc.Markdown(f"**Bot:**\n\n{response.text}"),  # Use Markdown for formatting
                    style={"textAlign": "left", "marginBottom": "10px"}
                )
                chat_history.append(bot_message)
            except Exception as e:
                error_message = html.Div(
                    html.P(f"Bot: Error processing your request. Please try again.", style={"color": "red"}),
                    style={"textAlign": "left", "marginBottom": "10px"}
                )
                chat_history.append(error_message)

            return (
                dash.no_update,  # No change to output-data-upload
                dash.no_update,  # No change to heatmap-triangle
                dash.no_update,  # No change to bar-factors
                dash.no_update,  # No change to line-projection
                dash.no_update,  # No change to heatmap-triangle style
                dash.no_update,  # No change to bar-factors style
                dash.no_update,  # No change to line-projection style
                dash.no_update,  # No change to chatbot-container style
                chat_history,  # Update chat history
                "",  # Clear input box
                dash.no_update  # No change to upload/loading message section
            )

        else:
            raise PreventUpdate  # Unknown trigger

    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')]
    )
    def display_page(pathname):
        if pathname == '/about':
            return about_layout
        elif pathname == '/scenario-analysis':
            return scenario_analysis_layout
        elif pathname == '/chatbot':
            return chatbot_layout
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