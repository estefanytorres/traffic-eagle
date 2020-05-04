import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

# Initialize app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}],)
server = app.server

# Load Data
df = pd.read_csv("data/accidents_by_state.csv")

# Layout
app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.Img(id="logo", src="https://i.pinimg.com/originals/0d/ce/de/0dcedef0ee93efd1be0e68872f95397c.png"),
                html.H1(children="Traffic Accidents in the U.S."),
            ],
        ),
        html.Div(
            id="heatmap-container",
            children=[
                html.H4("Total accidents per state"),
                dcc.Graph(id="state-choropleth"),
                dcc.Slider(
                    id='year-slider',
                    min=df['year'].min(),
                    max=df['year'].max(),
                    value=df['year'].min(),
                    marks={str(year): str(year) for year in df['year'].unique()},
                    step=None
                )
            ],
        )
    ]
)


@app.callback(
    Output(component_id='state-choropleth', component_property='figure'),
    [Input(component_id='year-slider', component_property='value')]
)
def update_map(year):

    temp_df = df[df['year'] == year]
    temp_df = temp_df.groupby('state').sum()['count'].reset_index()

    fig = go.Figure(data=go.Choropleth(
        locations=temp_df['state'],
        z=temp_df['count'].astype(float),
        locationmode='USA-states',
        colorscale='Reds',
        colorbar_title="Traffic Accidents",
    ))
    fig.update_layout(
        # title_text='US Traffic accidents',
        geo_scope='usa',
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
