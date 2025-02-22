from dash import html, dcc
import dash_bootstrap_components as dbc

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
                    "Scenario Analysis", 
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
                    "Chatbot",  # New page
                    href="/chatbot", 
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

# Upload Section
upload_section = html.Div(
    id="upload-section",
    children=[
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
    ]
)

# Loading Message
loading_message = html.Div(
    id="loading-message",
    children=[
        html.P(
            "Please wait, your data is being preprocessed...",
            style={"color": "#1675e0", "fontSize": "18px", "textAlign": "center", "margin": "20px"}
        )
    ],
    style={"display": "none"}  # Initially hidden
)

# Loading Interval
loading_interval = dcc.Interval(
    id="loading-interval",
    interval=1000,  # Check every 1 second
    n_intervals=0,
    disabled=True  # Disabled by default
)

# Chatbot Layout
chatbot_layout = html.Div(
    id="chatbot-container",
    style={"display": "none"},  # Hidden initially
    children=[
        html.H3("Chatbot", className="my-4", style={"color": "#1675e0"}),
        html.Div(
            id="chat-history",
            style={
                "height": "300px",
                "overflowY": "scroll",
                "border": "1px solid #ddd",
                "padding": "10px",
                "marginBottom": "10px",
                "backgroundColor": "#f9f9f9",  # Light background for chat history
            },
        ),
        dbc.Input(id="user-input", placeholder="Ask me about the plots...", type="text", style={"marginBottom": "10px"}),
        dbc.Button("Send", id="send-button", color="primary"),
    ]
)

# Home Page Layout
home_layout = dbc.Container([
    html.H1("Welcome to the Mathurance Platform", className="my-4", style={"color": "#1675e0"}),
    html.P(
        "Your one-stop solution for advanced actuarial analysis and claims forecasting.",
        style={"color": "#333333", "fontSize": "18px", "marginBottom": "30px"}
    ),
    dcc.Store(id="loading-state", data=False),  # Store to track loading state
    html.Div(id="dynamic-upload-section", children=upload_section),  # Dynamic section for upload/loading message
    html.Div(id="output-data-upload"),
    loading_interval,  # Interval to control loading message
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
    chatbot_layout  # Add the chatbot to the home layout
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
            className="mb-4",  # Add margin-bottom to this column
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
            className="mb-4",  # Add margin-bottom to this column
        ),
    ], className="mb-4"),  # Add margin-bottom to the entire row
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="scenario-line-plot"),
            md=12,
            className="mb-4",  # Add margin-bottom to this column
        ),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div(id="scenario-summary-table"),
            md=12,
            className="mb-4",  # Add margin-bottom to this column
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="inflation-trend-plot"),
            md=6,
            className="mb-4",  # Add margin-bottom to this column
        ),
        dbc.Col(
            dcc.Graph(id="claims-by-product-plot"),
            md=6,
            className="mb-4",  # Add margin-bottom to this column
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="claims-by-sub-branch-plot"),
            md=6,
            className="mb-4",  # Add margin-bottom to this column
        ),
        dbc.Col(
            dcc.Graph(id="claims-forecast-plot"),
            md=6,
            className="mb-4",  # Add margin-bottom to this column
        ),
    ]),
], fluid=True, style={"padding": "20px"})

# Chatbot Page Layout
chatbot_layout = dbc.Container([
    html.H1("Chatbot", className="my-4", style={"color": "#1675e0"}),
    html.P(
        "Upload your data to start chatting with the chatbot.",
        style={"color": "#333333", "fontSize": "18px", "marginBottom": "30px"}
    ),
    # File upload section
    html.Div(id="dynamic-upload-section", children=upload_section),
    # Chat interface (hidden initially)
    html.Div(
        id="chat-interface",
        style={"display": "none"},  # Hidden initially
        children=[
            html.Div(
                id="chat-history",
                style={
                    "height": "300px",
                    "overflowY": "scroll",
                    "border": "1px solid #ddd",
                    "padding": "10px",
                    "marginBottom": "10px",
                    "backgroundColor": "#f9f9f9",  # Light background for chat history
                },
            ),
            dbc.Input(id="user-input", placeholder="Ask me about the data...", type="text", style={"marginBottom": "10px"}),
            dbc.Button("Send", id="send-button", color="primary"),
        ]
    ),
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