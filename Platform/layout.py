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
                        "backgroundColor": "#6c757d",  # Gray background for buttons
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
                        "backgroundColor": "#6c757d",  # Gray background for buttons
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
    style={"backgroundColor": "#495057"},  # Dark gray background for sidebar
)

# Home Page Layout
home_layout = dbc.Container([
    html.H1("Welcome to the Mathurance Platform", className="my-4", style={"color": "white"}),
    html.P(
        "Your one-stop solution for advanced actuarial analysis and claims forecasting.",
        style={"color": "white", "fontSize": "18px", "marginBottom": "30px"}
    ),
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
                "borderColor": "#6c757d",  # Gray border
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
                "backgroundColor": "#6c757d",  # Gray background
                "color": "white",  # White text
                "cursor": "pointer",  # Pointer cursor on hover
                "transition": "background-color 0.3s",  # Smooth transition for hover effect
            },
        ),
        className="upload-button",
        multiple=False,
    ),
    html.Div(id="output-data-upload"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="heatmap-triangle"), md=6),
        dbc.Col(dcc.Graph(id="bar-factors"), md=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="line-projection"), md=12)
    ])
], fluid=True, style={"padding": "20px"})

# About Page Layout
about_layout = dbc.Container([
    html.H1("About Mathurance Platform", className="my-4", style={"color": "white"}),
    html.P(
        "The Mathurance Platform is designed to provide advanced actuarial tools for claims forecasting and analysis. "
        "Our platform leverages the Chain-Ladder method to help you make data-driven decisions with confidence.",
        style={"color": "white", "fontSize": "18px"}
    )
], fluid=True, style={"padding": "20px"})

# Main Layout
layout = html.Div(
    style={
        "backgroundColor": "#A9A9A9",  # Light gray background
        "minHeight": "100vh",  # Ensure the background covers the entire viewport height
    },
    children=[
        dcc.Location(id='url', refresh=False),
        dbc.Button(
            html.I(className="fas fa-bars"),  # FontAwesome hamburger icon
            id="sidebar-toggle",
            color="secondary",  # Gray button
            className="m-3",
            style={"cursor": "pointer"}  # Pointer cursor on hover
        ),
        sidebar,
        html.Div(id='page-content', style={"margin-left": "2rem", "padding": "2rem"}),
        # Add custom CSS for the upload button
        html.Div(style={"display": "none"}, id="custom-css"),  # Placeholder for custom CSS
        html.Div(
            """
            <style>
                .upload-button:hover {
                    background-color: #5a6268 !important;  /* Darker gray on hover */
                    border-color: #545b62 !important;  /* Darker border on hover */
                }
            </style>
            """,
            # dangerously_set_inner_html={}  # Inject custom CSS
        )
    ]
)