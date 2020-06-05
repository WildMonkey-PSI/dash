import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import dash_table
import plotly.express as px
import numpy as np
from datetime import datetime

data_csv = pd.read_csv('https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_confirmed_global.csv&filename=time_series_covid19_confirmed_global.csv')

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

def select_country(name):
    country_data = data_csv.loc[data_csv['Country/Region'] == name]
    country = country_data.melt(id_vars=['Country/Region'])
    country = country[3::]
    return country
def count_x (plot_data):
    dates = []
    for x in plot_data.variable:
        split = (x.split("/"))
        dd = datetime(int("20"+split[2]),int(split[0]),int(split[1]))
        dates.append(dd)    
    return dates

def count_y (plot_data):
    y = []
    for x in plot_data.value:  
        y.append(x)    
    return y

def count_perDay(plot_y):
    amount = []
    for x in range(len(plot_y)):
        if(x == 0):
            amount.append(plot_y[x])
        else:
            amount.append(plot_y[x] - plot_y[x-1])
    return amount

def set_selectors(data_csv):
    countries_all = []
    for x in data_csv['Country/Region']:
        countries_all.append(x)
    countries_all = list(dict.fromkeys(countries_all)) 
    countries = []
    for x in countries_all:
        countries.append({'label': x, 'value': x})
    return countries

def total_rank(data_csv):
    sum = {}
    for x in range(len(data_csv)):
        total = data_csv.iloc[x,-1].tolist()
        country = data_csv.iloc[x,1]
        sum[country] = total
        
    sum = sorted(sum.items(), key=lambda x: x[1], reverse=True)
    sum = np.array(sum)
    return sum


country = 'Poland'
plot_data = select_country(country)
plot_x = count_x(plot_data)
plot_y = count_y(plot_data)
case_perDay = count_perDay(plot_y)
total_rank = total_rank(data_csv)

df = px.data.tips()
fig = px.bar(df, x="sex", y="total_bill", color='time') 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H4(children='COVID 2020'),
    dash_table.DataTable(
    data=data_csv.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in data_csv.columns],
    fixed_columns={'headers': True, 'data': 2},
    style_table={'minWidth': '100%','height': '300px', 'overflowY': 'auto'}
    ),
    
    dcc.Graph(
        id='example-graphhe',
        figure={
            'data': [
                {'x': total_rank[:,0], 'y': total_rank[:,1], 'type': 'bar', 'name': 'SF'},
            ],
            'layout': {
                'title': 'Cases Rank by Countries',
                'yaxis': {
                    'categoryorder': 'array',
                    'categoryarray': [x for _, x in sorted(zip(total_rank[:,0], total_rank[:,1]))]
                    
                    }
            },
            
        }
    ),
    html.H4('Select Country'),
    dcc.Dropdown(
        id='dropp',
        options=set_selectors(data_csv),
        value=country,
        
    ),
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': plot_x, 'y': plot_y, 'type': 'bar', 'name': 'SF'},
            ],
            'layout': {
                'title': 'Total ' + country
            }
        }
    ),
    dcc.Graph(
        id='example-graphh',
        figure={
            'data': [
                {'x': plot_x, 'y': case_perDay, 'type': 'bar', 'name': 'SF'},
            ],
            'layout': {
                'title': 'Increase per day for ' +country
            }
        }
    ),
    dcc.Graph(
        id='example-graphhh',
        figure=fig
    ),
    
    html.Div(id='dd-output-container'),
    
])
    
@app.callback(
    [dash.dependencies.Output('example-graph', 'figure'),
    dash.dependencies.Output('example-graphh', 'figure')],
    [dash.dependencies.Input('dropp', 'value')])
def update_output(value):
    country = str(value).strip("['']")
    plot_data = select_country(country)
    plot_x = count_x(plot_data)
    plot_y = count_y(plot_data)
    case_perDay = count_perDay(plot_y)
    figure={
            'data': [
                {'x': plot_x, 'y': plot_y, 'type': 'bar', 'name': 'SF'},
            ],
            'layout': {
                'title': 'Total ' + country
            }
        }
    figure1={
            'data': [
                {'x': plot_x, 'y': case_perDay, 'type': 'bar', 'name': 'SF'},
            ],
            'layout': {
                'title': 'Increase per day for ' + country
            }
        }
    return figure,figure1

if __name__ == '__main__':
    app.run_server(debug=True)
