from dash import dcc, html
import dash
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd 

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
        html.H1(id='heatmap_app',  style={'textAlign':'center', 'marginBottom':'5vh'}),

    ]),
    dbc.Row([
        dbc.Col([
            html.Div([
            dcc.Dropdown(
                id='slct_type2',
                options =[
                    {'label':'Generators', 'value':'generators'},
                    {'label':'receivers', 'value':'receivers'},
                ],
                value='receivers',
                style={"textAlign": "center", 'border':'transparent'}, 

                ),
            ],),
        ], width=2),

    ]),
    dbc.Row([
        html.Div([
            dcc.Graph(id='stacked_barchart', figure={})
        ]),
    ]),
])

@app.callback(
    Output('stacked_barchart', 'figure'),
    Input('slct_type2', 'value'),
)
def stacked_barchart(slctd_val):
    generators = [g for g in df.columns if g.startswith('Gen')]
    receivers = [r for r in df.columns if r.startswith('Rec')]
    cols = eval(slctd_val)
    slct_month="June"
    temp = df.copy()
    temp['day'] = temp['Date/time'].dt.day_name()
    temp_m = temp[temp['Date/time'].dt.month_name() == slct_month]
    days = temp_m.day.unique()
    data = []

    data = []
    counter = 0
    total_vals = np.array([0.0,0.0,0.0,0.0,0.0,0.0,0.0])
    for col in cols:
        vals = temp_m.groupby(['day'])[col].sum()
        total_vals += np.array(vals)
        if counter+1 == len(cols):
            data.append(go.Bar(name=col, x=days, y=vals, text=[f'{round(i/2700)}%' for i in total_vals]))
        else:
            data.append(go.Bar(name=col, x=days, y=vals))
        counter +=1

    fig = go.Figure(data = data)
    fig.update_layout(barmode='stack')
    fig.update_yaxes(title="KwH")

    return fig



if __name__ == '__main__':
    app.run_server(debug=True, threaded= True)
