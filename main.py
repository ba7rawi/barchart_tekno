from dash import dcc, html
import dash
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd 
from plotly.subplots import make_subplots


df = pd.read_csv('EMSdataset.csv')
df_diff = df.drop(columns=['Date/time']).diff()
df_diff.insert(0, 'Date/time' ,df['Date/time'])
df_diff = df_diff.iloc[1:,:]
df = df_diff
df['Date/time'] = pd.to_datetime(df['Date/time'])
df['Date'] = pd.to_datetime(df['Date/time']).dt.date


fontawesome_stylesheet = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"

app = dash.Dash(
    __name__,
    suppress_callback_exceptions = True,
    external_stylesheets=[dbc.themes.BOOTSTRAP, fontawesome_stylesheet],
 
    )

app.layout = html.Div([
    dbc.Row([
        html.H1(id='heatmap_app', children=['App Title'], style={'textAlign':'center', 'marginBottom':'5vh'}),

    ]),
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Dropdown(id='slct_month', 
                            options=[
                                {'label': m , 'value':m} for m in df['Date/time'].dt.month_name().unique()
                                ],
                            value='June',
                            style={"textAlign": "center", 'border':'transparent'}, 
                            ),

            ], style={ 'marginBottom':'5vh', }),
        ], width=2),
        dbc.Col([
            html.Div([
            dcc.Dropdown(
                id='slct_type2',
                options =[
                    {'label':'Generators', 'value':'generators'},
                    {'label':'receivers', 'value':'receivers'},
                ],
                value='generators',
                style={"textAlign": "center", 'border':'transparent'}, 

                ),
            ],),
        ], width=2),

    ]),

    dbc.Row([
        html.Div([

            dbc.Col(
                dcc.Graph(id='heatmap', figure={}),
                xs=12, sm=12, md=12, lg=12, xl=12

            ),
        ]),
    ]),
], style={'margin':'5vh'})

@app.callback(
    Output('slct_column', 'options'),
    Output('slct_column', 'value'),
    Input('slct_type2', 'value'),

)
def gens_or_rec(slct):
    generators = [g for g in df.columns if g.startswith('Gen')]
    receivers = [r for r in df.columns if r.startswith('Rec')]
    ops = [{'label':i, 'value':i} for i in  eval(slct) ]
    return ops, eval(slct)[0]

@app.callback(
    Output(component_id='heatmap', component_property='figure'),
    Input(component_id='slct_month', component_property='value'),
    Input('slct_type2', 'value'),
)
def barchart2(slct_month, slct_type):
    generators = [g for g in df.columns if g.startswith('Gen')]
    receivers = [r for r in df.columns if r.startswith('Rec')]
    temp = df[eval(slct_type) + ['Date/time']].copy()
    # temp = df.copy()
    temp = temp[temp['Date/time'].dt.month_name() == slct_month]
    temp = temp.sum()
    temp =temp.sort_values(ascending=False)
    dft = temp
    trace1 = go.Bar(x = dft.index, y=dft.values.tolist(), text=dft.values.tolist())
    trace2 = go.Scatter(
        x=dft.index,
        y=dft.cumsum(),
        name='Cumulative Percentage',
        yaxis='y2')
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(trace1)
    fig.add_trace(trace2)
    fig.update_layout(
        title='Pareto Chart title for <b>' + str(slct_month) + '</b> ... units in kwh', 
        plot_bgcolor='rgba(0,0,0,0)', 
        xaxis=dict(showgrid=False),          
        yaxis=dict(showgrid=False),
        showlegend=False)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, threaded= True)
