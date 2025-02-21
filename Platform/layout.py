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
                    style={"color": "black", "margin": "5px", "border-radius": "5px"}
                ),
                dbc.NavLink(
                    "About", 
                    href="/about", 
                    active="exact", 
                    style={"color": "black", "margin": "5px", "border-radius": "5px"}
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    id="sidebar",
    title="Chain-Ladder",
    is_open=False,
    placement="start",
)

# Home Page Layout
home_layout = dbc.Container([
    html.H1("Chain-Ladder Analysis Platform", className="my-4"),
    dcc.Upload(

    id="upload-data",
    children=html.Div([
        html.A("Select a File", style={"color": "white", "textDecoration": "underline"}),
        html.P("Drag and Drop or Click to Select a CSV File", style={"color": "white", "fontSize": "14px"}),
    ]),
    style={
        "width": "100%",
        "height": "60px",
        "lineHeight": "60px",
        "borderWidth": "1px",
        "borderStyle": "solid",  # Changed from dashed to solid
        "borderColor": "#007BFF",  # Blue border
        "borderRadius": "5px",
        "textAlign": "center",
        "margin": "10px",
        "backgroundColor": "#007BFF",  # Blue background
        "color": "white",  # White text
        "cursor": "pointer",  # Pointer cursor on hover
        "transition": "background-color 0.3s",  # Smooth transition for hover effect
    },
    # Add hover effect using CSS
    className="upload-button",
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

# About Page Layout
about_layout = dbc.Container([
    html.H1("About", className="my-4"),
    html.P("This is the about page for the Chain-Ladder Analysis Platform.")
], fluid=True)

# Main Layout
layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Button(
        html.I(className="fas fa-bars"),  # FontAwesome hamburger icon
        id="sidebar-toggle",
        color="black",
        className="m-3",
        style={"cursor": "pointer"}  # Optional: Add a pointer cursor
    ),
    sidebar,
    html.Div(id='page-content', style={"margin-left": "2rem", "padding": "2rem"})
])