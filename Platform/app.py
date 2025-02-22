import dash
import dash_bootstrap_components as dbc
from layout import layout
from callbacks import register_callbacks

# Initialize the Dash app
external_stylesheets = [dbc.themes.BOOTSTRAP, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Mathurance Dashboard"

# Set the app layout
app.layout = layout

# Register callbacks
register_callbacks(app)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)