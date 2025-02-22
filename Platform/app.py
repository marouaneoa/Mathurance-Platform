import dash
import dash_bootstrap_components as dbc
from layout import layout
from callbacks import register_callbacks
# import ollama_model
import ollama
# Initialize the Dash app
external_stylesheets = [dbc.themes.BOOTSTRAP, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Mathurance Dashboard"

# Set the app layout
app.layout = layout

# Initialize the model
model = ollama.Client()

# Register callbacks with the model
register_callbacks(app, model)  # Pass the model as an argument

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)