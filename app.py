import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from pmdarima import auto_arima

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
                                html.H2("Total accidents per million population"),
                                dcc.Graph(id="state-choropleth", className="figure"),
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
                                        html.Label("Graph:"),
                                        dcc.Dropdown(
                                            id='analysis-option-graph',
                                            className='dropdown',
                                            options=[
                                                {'label': 'Data', 'value': 'D'},
                                                {'label': 'Trend', 'value': 'T'},
                                                {'label': 'Seasonality', 'value': 'S'},
                                                {'label': 'Prediction', 'value': 'P'},
                                            ],
                                            value='D',
                                            searchable=False,
                                            clearable=False
                                        ),
                                        html.Label("Period:"),
                                        dcc.Dropdown(
                                            id='analysis-option-period',
                                            className='dropdown',
                                            options=[
                                                {'label': 'Monthly', 'value': 'M'},
                                                {'label': 'Weekly', 'value': 'W'},
                                                {'label': 'Daily', 'value': 'D'}
                                            ],
                                            value='M',
                                            searchable=False,
                                            clearable=False
                                        ),
                                    ]
                                ),
                                dcc.Loading(
                                    children=[html.Div(id="analysis-content", className='figure')],
                                    type="circle",
                                )
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
     Input(component_id='analysis-option-period', component_property='value'),
     Input(component_id='analysis-option-graph', component_property='value'),
     ]
)
def update_state(year, map, period, graph):
    if map and period:
        state = map['points'][0]['location']
        # figure_data = df[(df.Year == year) & (df.State == state)]
        figure_data = df[(df.State == state)]
        figure_data = figure_data.groupby(figure_data.Date.dt.to_period(period)).sum().Count
        figure_data = figure_data.resample(period).asfreq().fillna(0)
        figure_data.index = figure_data.index.to_timestamp()
        if graph == 'P':
            model = auto_arima(figure_data, suppress_warnings=True)
            n = 10
            prediction_index = pd.date_range(figure_data.index[-1].date(), periods=n + 1,
                                             freq=figure_data.index[-1].freq)[1:]
            prediction = model.predict(n_periods=n)
            fig = {
                'data': [
                    {
                        'x': figure_data.index,
                        'y': figure_data.values,
                        'name': 'data'
                    },
                    {
                        'x': prediction_index,
                        'y': prediction,
                        'name': 'prediction'
                    }
                ],
                'layout': {
                    'showlegend': False
                }
            }

        else:
            if graph != 'D':
                decomposition = seasonal_decompose(figure_data)
                if graph == 'T':
                    figure_data = decomposition.trend
                elif graph == 'S':
                    figure_data = decomposition.seasonal
            fig = {
                'data': [{
                    'x': figure_data.index,
                    'y': figure_data.values
                }],
            }

        return [
            html.H3(state),
            dcc.Graph(className='figure', figure=fig)
        ]
    else:
        return "Select a state to analyze..."


if __name__ == '__main__':
    app.run_server(debug=True)
