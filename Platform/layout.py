from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components import Offcanvas

# Sidebar Layout
sidebar = dbc.Offcanvas(
    [
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    "Home", 
                    href="/", 
                    active="exact", 
                    style={
                        "color": "white",  # White text
                        "margin": "5px", 
                        "borderRadius": "5px",
                        "backgroundColor": "#1357b3",  # Darker shade of base color
                    }
                ),
                dbc.NavLink(
                    "Scenario Analysis",  # New page
                    href="/scenario-analysis", 
                    active="exact", 
                    style={
                        "color": "white",  # White text
                        "margin": "5px", 
                        "borderRadius": "5px",
                        "backgroundColor": "#1357b3",  # Darker shade of base color
                    }
                ),
                dbc.NavLink(
                    "About", 
                    href="/about", 
                    active="exact", 
                    style={
                        "color": "white",  # White text
                        "margin": "5px", 
                        "borderRadius": "5px",
                        "backgroundColor": "#1357b3",  # Darker shade of base color
                    }
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    id="sidebar",
    title="Mathurance Platform",
    is_open=False,
    placement="start",
    style={"backgroundColor": "white"},  # Base color for sidebar
)

# Home Page Layout
home_layout = dbc.Container([
    html.H1("Welcome to the Mathurance Platform", className="my-4", style={"color": "#1675e0"}),
    html.P(
        "Your one-stop solution for advanced actuarial analysis and claims forecasting.",
        style={"color": "#333333", "fontSize": "18px", "marginBottom": "30px"}
    ),
    dbc.Row(
        [
            dbc.Col(
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(
                        [
                            html.A(
                                "Upload your sheet",
                                style={
                                    "color": "white",
                                    "textDecoration": "none",
                                    "cursor": "pointer",
                                },
                            ),
                        ],
                        style={
                            "width": "100%",
                            "height": "60px",
                            "lineHeight": "60px",
                            "borderWidth": "1px",
                            "borderStyle": "solid",
                            "borderColor": "#1675e0",  # Base color for border
                            "borderRadius": "5px",
                            "textAlign": "center",
                            "margin": "10px",
                            "backgroundColor": "#1675e0",  # Base color for button
                            "color": "white",  # White text
                            "cursor": "pointer",  # Pointer cursor on hover
                            "transition": "background-color 0.3s",  # Smooth transition for hover effect
                        },
                    ),
                    className="upload-button",
                    multiple=False,
                ),
                md=8,  # Adjust column width for the upload button
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="reserving-model-dropdown",
                    options=[
                        {"label": "Chain-Ladder", "value": "chain_ladder"},
                        {"label": "Bornhuetter-Ferguson", "value": "bornhuetter_ferguson"},
                        {"label": "Cape Cod", "value": "cape_cod"},
                    ],
                    value="chain_ladder",  # Default selection
                    clearable=False,
                    style={"width": "100%", "marginTop": "10px"},  # Style for the dropdown
                ),
                md=4,  # Adjust column width for the dropdown
            ),
        ],
        className="mb-4",  # Add margin below the row
    ),
    html.Div(id="output-data-upload"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="heatmap-triangle", style={"display": "none"}), md=6),  # Hidden initially
        dbc.Col(dcc.Graph(id="bar-factors", style={"display": "none"}), md=6),  # Hidden initially
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="line-projection", style={"display": "none"}), md=12)  # Hidden initially
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="cumulative-claims", style={"display": "none"}), md=6),  # New plot: Cumulative claims over time
        dbc.Col(dcc.Graph(id="claims-distribution", style={"display": "none"}), md=6),  # New plot: Claims distribution by year
    ]),
    dbc.Row([
        dbc.Col(html.Div(id="reserve-summary", style={"display": "none"}), md=12)  # New table: Reserve summary
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="risk-factor-product", style={"display": "none"}), md=6),  # New plot: Risk factor by product
        dbc.Col(dcc.Graph(id="risk-factor-sub-branch", style={"display": "none"}), md=6),  # New plot: Risk factor by sub-branch
    ]),
    dbc.Row([
        dbc.Col(
            html.Div(id="next-year-prediction", style={"display": "none"}),  # Hidden initially
            md=12,
        ),
    ]),
], fluid=True, style={"padding": "20px"})

# Scenario Analysis Page Layout
scenario_analysis_layout = dbc.Container([
    html.H1("Scenario Analysis", className="my-4", style={"color": "#1675e0"}),
    html.P(
        "Simulate different scenarios for claims forecasting by adjusting inflation rates and development factors.",
        style={"color": "#333333", "fontSize": "18px", "marginBottom": "30px"}
    ),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Adjust Inflation Rates", className="card-title"),
                    html.Label("Inflation Rate for 2024 (%)"),
                    dcc.Input(
                        id="inflation-rate-2024",
                        type="number",
                        value=5.0,  # Default value
                        min=0,
                        max=20,
                        step=0.1,
                    ),
                    html.Label("Inflation Rate for 2025 (%)"),
                    dcc.Input(
                        id="inflation-rate-2025",
                        type="number",
                        value=5.0,  # Default value
                        min=0,
                        max=20,
                        step=0.1,
                    ),
                ]),
            ),
            md=6,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Adjust Development Factors", className="card-title"),
                    html.Label("Development Factor for Period 1 to 2"),
                    dcc.Slider(
                        id="dev-factor-1-2",
                        min=1.0,
                        max=2.0,
                        step=0.1,
                        value=1.5,  # Default value
                        marks={i: str(i) for i in [1.0, 1.5, 2.0]},
                    ),
                    html.Label("Development Factor for Period 2 to 3"),
                    dcc.Slider(
                        id="dev-factor-2-3",
                        min=1.0,
                        max=2.0,
                        step=0.1,
                        value=1.3,  # Default value
                        marks={i: str(i) for i in [1.0, 1.5, 2.0]},
                    ),
                ]),
            ),
            md=6,
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="scenario-line-plot"),
            md=12,
        ),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div(id="scenario-summary-table"),
            md=12,
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="inflation-trend-plot"),
            md=6,
        ),
        dbc.Col(
            dcc.Graph(id="claims-by-product-plot"),
            md=6,
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="claims-by-sub-branch-plot"),
            md=6,
        ),
        dbc.Col(
            dcc.Graph(id="claims-forecast-plot"),
            md=6,
        ),
    ]),
], fluid=True, style={"padding": "20px"})

# About Page Layout
about_layout = dbc.Container([
    html.H1("About Mathurance Platform", className="my-4", style={"color": "#1675e0"}),
    html.P(
        "The Mathurance Platform is designed to provide advanced actuarial tools for claims forecasting and analysis. "
        "Our platform leverages the Chain-Ladder method to help you make data-driven decisions with confidence.",
        style={"color": "#333333", "fontSize": "18px"}
    )
], fluid=True, style={"padding": "20px"})

# Main Layout
layout = html.Div(
    style={
        "backgroundColor": "#f0f0f0",  # Light gray background for the app
        "minHeight": "100vh",  # Ensure the background covers the entire viewport height
    },
    children=[
        dcc.Location(id='url', refresh=False),
        dcc.Store(id="stored-data"),  # Store for uploaded data
        dcc.Store(id="stored-scenario-inputs"),  # Store for scenario analysis inputs
        dbc.Button(
            html.I(className="fas fa-bars"),  # FontAwesome hamburger icon
            id="sidebar-toggle",
            color="primary",  # Base color for button
            className="m-3",
            style={"cursor": "pointer"}  # Pointer cursor on hover
        ),
        sidebar,
        html.Div(id='page-content', style={"margin-left": "2rem", "padding": "2rem"}),
    ]
)