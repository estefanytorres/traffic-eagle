import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import time


# Initialize app
app = dash.Dash(__name__,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}],
                external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Traffic Eagle"
server = app.server


# Load Data
df = pd.read_csv("data/accidents_by_state.csv")

# Layout
app.layout = html.Div(
    id="root",
    children=[
        dbc.Navbar(
            id="header",
            light=True,
            children=[
                html.A(
                    href="#",
                    children=[
                        dbc.Row(
                            align="center",
                            no_gutters=True,
                            children=[
                                dbc.Col(html.Img(src="/assets/img/logo.png", height="30px")),
                                dbc.Col(dbc.NavbarBrand("Traffic Eagle", className="ml-2")),
                            ],
                        ),
                    ]
                ),
            ],
        ),
        html.Div(
            id="body",
            children=[
                html.Div(
                    id="map",
                    className="block",
                    children=[
                        html.Div(
                            className="block-container",
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
                            ]
                        )
                    ],
                ),
                html.Div(
                    id="analysis",
                    className="block",
                    children=[
                        html.Div(
                            className="block-container",
                            children=[
                                html.H4("Analysis"),
                            ]
                        )
                    ]
                )
            ]
        ),
        html.Footer(
            html.P(["Source code at ", html.A("Github", href="https://github.com/estefanytorres/traffic-eagle")])
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
        geo_scope='usa',
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
