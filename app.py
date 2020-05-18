import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

# Initialize app
app = dash.Dash(__name__,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}],
                external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Traffic Eagle"
server = app.server


# Load Data
df = pd.read_csv("data/accidents_by_county.csv")
df.Date = pd.to_datetime(df.Date)
pop = pd.read_csv("data/population_by_county_2019.csv")

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
                                html.H2("Total accidents per state"),
                                dcc.Graph(id="state-choropleth", className='figure'),
                                dcc.Slider(
                                    id='year-slider',
                                    min=df['Year'].min(),
                                    max=df['Year'].max(),
                                    value=df['Year'].min(),
                                    marks={str(year): str(year) for year in df['Year'].unique()},
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
                                html.Div(
                                    id='analysis-option',
                                    children=[
                                        html.Label("Period:"),
                                        dcc.Dropdown(
                                            id='analysis-option-period',
                                            className='dropdown',
                                            options=[
                                                {'label': 'Daily', 'value': 'D'},
                                                {'label': 'Weekly', 'value': 'W'},
                                                {'label': 'Monthly', 'value': 'M'}
                                            ],
                                            value='D',
                                            searchable=False,
                                            clearable=False
                                        ),
                                    ]
                                ),
                                html.Div(id="analysis-content")
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

    figure_data = df[df.Year == year]
    figure_data = figure_data.groupby('State').sum().Count.reset_index()
    figure_pop = pop.groupby('State').sum().reset_index()
    figure_data = figure_data.merge(figure_pop)
    figure_data['Accidents'] = (figure_data.Count / figure_data.Population) * 1000000

    fig = go.Figure(data=go.Choropleth(
        locations=figure_data.State,
        z=figure_data.Accidents.astype(float),
        locationmode='USA-states',
        colorscale='Reds',
        # colorbar_title="Traffic Accidents per million habitants",
    ))
    fig.update_layout(
        geo_scope='usa',
    )
    return fig



@app.callback(
    Output(component_id='analysis-content', component_property='children'),
    [Input(component_id='year-slider', component_property='value'),
     Input(component_id='state-choropleth', component_property='clickData'),
     Input(component_id='analysis-option-period', component_property='value')
     ]
)
def update_state(year, map, period):
    if map and period:
        state = map['points'][0]['location']
        figure_data = df[(df.Year == year) & (df.State == state)]
        # figure_data = figure_data.groupby('Date').sum().Count
        figure_data = figure_data.groupby(figure_data.Date.dt.to_period(period)).sum().Count
        fig = {
            'data': [{
                'x': figure_data.index.to_timestamp(),
                'y': figure_data.values
            }],
            # 'layout': {
            #     'title': 'Dash Data Visualization'
            # }
        }
        return [
            html.H3(state),
            dcc.Graph(className='figure', figure=fig)
        ]
    else:
        return "Select a state to analyze..."


if __name__ == '__main__':
    app.run_server(debug=True)
