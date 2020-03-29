import dash
import dash_core_components as dcc
import dash_html_components as html
# import plotly.plotly as py
import plotly.graph_objs as go
import os
import pandas as pd
import plotly.graph_objs as go
from scipy.interpolate import interp1d
import numpy as np
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
server = app.server

NumberOfInfected_text = '''   

                    28                 '''
NumberOfHospitalised_text = '''   

                    2                '''


def readCSV():
    FilePath = r"InputData.csv"
    return pd.read_csv(FilePath)


def filterandGreoup(Df, FilterDay):
    Df = Df[Df['Day'] <= FilterDay]
    AnalysedDF = Df.groupby('DHB').agg({'Report Date': lambda x: x.iloc[0],
                                        'DHB2015_Name': 'count',
                                        'LON': lambda x: x.iloc[0],
                                        'LAT': lambda x: x.iloc[0]})

    AnalysedDF['DHB'] = AnalysedDF.index
    return AnalysedDF


def reformatlon(AnalysedDF):
    lon = (AnalysedDF['LON'].tolist())
    return [str(x) for x in lon]


def reformatlat(AnalysedDF):
    lat = (AnalysedDF['LAT'].tolist())
    return [str(x) for x in lat]


def reformatTexthaouver(AnalysedDF):
    textnumber = (AnalysedDF['DHB2015_Name'].tolist())
    City = (AnalysedDF['DHB'].tolist())
    return ['Number Of cases in ' + str(City[index]) + ' is ' + str(x) for index, x in enumerate(textnumber)]


def reformatTextnumber(AnalysedDF):
    textnumber = (AnalysedDF['DHB2015_Name'].tolist())
    return [str(x) for x in textnumber]


def checkNumberSize(AnalysedDF):
    return AnalysedDF['DHB2015_Name'].tolist()


def convrtArray(OldArray):
    if len(OldArray) > 1:
        x = np.array([min(OldArray), max(OldArray) / 3.2, max(OldArray) / 2.1, max(OldArray)])
        y = np.array([1, 5, 8, 10])
        f = interp1d(x, y, kind='cubic')
    else:
        x = np.array([min(OldArray), max(OldArray)])
        y = x
        f = interp1d(x, y)

    return f(OldArray)


Df = readCSV()
AnalysedDF = filterandGreoup(Df, Df['Day'].max())
Numbersize = checkNumberSize(AnalysedDF)
b = convrtArray(Numbersize)

#
DfAnalysed2 = Df.groupby('Report Date').agg({'DHB2015_Name': 'count'})
DfAnalysed2['DateColumn'] = DfAnalysed2.index
print(DfAnalysed2)
DfAnalysed2['DateColumn'] = pd.to_datetime(DfAnalysed2['DateColumn'], format='%d/%m/%Y')
DfAnalysed2 = DfAnalysed2.sort_values(by=['DateColumn'], ascending=False)
indexAll = DfAnalysed2.index.tolist()

for index in indexAll:
    DF_Filter = DfAnalysed2[DfAnalysed2['DateColumn'] <= DfAnalysed2.loc[index, 'DateColumn']]
    DfAnalysed2.loc[index, 'DHB2015_Name'] = DF_Filter['DHB2015_Name'].sum()

x = DfAnalysed2['DHB2015_Name'].tolist()
print(x)

DfAnalysed2['DateColumn'] = DfAnalysed2['DateColumn'].dt.strftime('%d/%m')
y = DfAnalysed2['DateColumn'].tolist()
print(y)
trace1 = go.Bar(x=x, y=y,
                orientation='h',
                marker=dict(
                    color='rgba(0,0,139, 0.8)',
                    line=dict(color='rgba(255, 0, 0, 1.0)', width=1)
                ))

mapbox_access_token = 'pk.eyJ1IjoiaGFtZWRtaW5hZWkiLCJhIjoiY2s3d3Bhemk0MDR3bDNrbG5wOHJqNmpjcSJ9.sTFiN0dxyLO7GgXJpqsoOQ'
if not mapbox_access_token:
    raise RuntimeError("Mapbox key not specified! Edit this file and add it.")

data = [
    go.Scattermapbox(
        lat=reformatlat(AnalysedDF),
        lon=reformatlon(AnalysedDF),
        mode='markers+text',
        opacity=0.3,
        showlegend=True,
        text=reformatTextnumber(AnalysedDF),
        # hoverinfo='none',
        hoverinfo='text',
        hovertext=reformatTexthaouver(AnalysedDF),

        marker=go.scattermapbox.Marker(

            size=b,
            sizemin=min(b) / 10,
            sizeref=min(b) / 10,
            color='rgb(239,0,0)'
        ),

    )
]

layout = go.Layout(
    autosize=True,
    # width=650,
    # height=450,
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0,
        pad=0
    ),
    hovermode='closest',
    mapbox=go.layout.Mapbox(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=-41.28,
            lon=174.77
        ),
        pitch=0,
        zoom=4.2
    ),
)

colors = {
    'background': '#000000',
    'text': '#bdbdbd',
    'Section': '#525252',
    'textColor1': '#e32e2e',
    'textColor2': '#fab91c',
    'textColor3': '#0545d8',
    'textColor4': '#ffffff'
}

app.layout = html.Div([
    html.Div(
        [
            html.H1(children='COVID19-New Zealand')

        ],
        style={'width': '96%', 'display': 'inline-block', 'border-style': 'solid ', 'textAlign': 'center',
               'padding': 10,
               'backgroundColor': colors['Section'], 'color': colors['text'], 'margin-top': 10, 'margin-bottom': 10,
               'margin-right': 10, 'margin-left': 10}
    )
    ,
    html.Br()
    ,
    html.Div([
        html.Div([
            html.Div(
                [
                    html.H3(children='Level 4')

                ],
                style={'width': '100%', 'display': 'inline-block', 'textAlign': 'center', 'padding': 0,
                       'border-style': 'solid ', 'vertical-align': 'top', 'backgroundColor': colors['Section'],
                       'color': colors['textColor1'], 'margin-top': 3, 'margin-bottom': 3}
            ),
            html.Div(
                [
                    html.H3(children='Number of confirmed cases'),
                    html.H2(children='20', style={'color': colors['textColor2']})
                ],
                style={'width': '100%', 'display': 'inline-block', 'textAlign': 'center', 'padding': 0,
                       'border-style': 'solid ', 'vertical-align': 'top', 'backgroundColor': colors['Section'],
                       'color': colors['text'], 'margin-top': 3, 'margin-bottom': 3}
            ),
            html.Div(
                [
                    html.H3(children='Number of recovered cases '),
                    html.H2(children='20', style={'color': colors['textColor3']})
                ],
                style={'width': '100%', 'display': 'inline-block', 'textAlign': 'center', 'padding': 0,
                       'border-style': 'solid ', 'vertical-align': 'top', 'backgroundColor': colors['Section'],
                       'color': colors['text'], 'margin-top': 3, 'margin-bottom': 3}
            )
            , html.Div(
                [html.H3(children='Number of community transmission cases '),
                 html.H2(children='2', style={'color': colors['textColor1']})
                 ],
                style={'width': '100%', 'display': 'inline-block', 'textAlign': 'center', 'padding': 0,
                       'border-style': ' solid ', 'vertical-align': 'bottom', 'backgroundColor': colors['Section'],
                       'color': colors['text'], 'margin-top': 3, 'margin-bottom': 3}
            ),
        ]
        ),
    ], style={'width': '18%', 'height': '100%', 'display': 'inline-block', 'padding': 10, 'border-style': 'solid ',
              'vertical-align': 'middle', 'margin-right': 10, 'margin-left': 10}
    )
    , html.Div([
        html.Div([
            dcc.Graph(
                id='Bubble-graph',
                figure={
                    'data': data,
                    '   layout': layout
                }
            )
            , ]
        )
    ], style={'width': '54%', 'display': 'inline-block', 'padding': 10, 'border-style': 'solid ',
              'vertical-align': 'middle', 'backgroundColor': colors['Section'],
              'color': colors['text'], 'textAlign': 'center'}
    )
    , html.Div([

        html.Div([
            dcc.Graph(
                id='example-graph',
                figure={
                    'data': [trace1],
                    'layout': {'title': {'text': 'Total Number of cases per day', 'font': {"size": 11}},
                               'plot_bgcolor': colors['Section'],
                               'paper_bgcolor': colors['Section'],
                               'font': {'color': colors['textColor4'],
                                        'color': colors['textColor4']}
                               }
                })
        ], style={'backgroundColor': colors['Section'],
                  'color': colors['text'], 'textAlign': 'center'}
            ,
        )
    ], style={'width': '18%', 'display': 'inline-block', 'padding': 10, 'border-style': 'solid ',
              'vertical-align': 'middle', 'textAlign': 'right', 'backgroundColor': colors['Section'],
              'color': colors['text'], 'textAlign': 'center', 'margin-right': 10, 'margin-left': 10}
    )
    ,

    html.Div([html.H3(children='Days after first case confirmed'),
              dcc.Slider(
                  id='Day-slider',
                  min=Df['Day'].min(),
                  max=Df['Day'].max(),
                  value=Df['Day'].max(),
                  marks={str(Day): str(Day) + ' day' for Day in Df['Day'].unique()},
                  step=None
              )
              ], style={'width': '96%', 'display': 'inline-block', 'padding': 10, 'border-style': 'solid ',
                        'vertical-align': 'middle', 'textAlign': 'right', 'backgroundColor': colors['textColor4'],
                        'color': colors['text'], 'textAlign': 'center', 'margin-right': 10, 'margin-left': 10,
                        'margin-top': 10, 'margin-bottom': 10}
             )
], style={'backgroundColor': colors['background'], 'color': colors['text']})


@app.callback(
    Output('Bubble-graph', 'figure'),
    [Input('Day-slider', 'value')])
def update_figure(Day):
    print(Day)
    AnalysedDF = filterandGreoup(Df, Day)
    Numbersize = checkNumberSize(AnalysedDF)
    if len(Numbersize) == 1:
        b = Numbersize * 50
    else:
        b = convrtArray(Numbersize)

    if len(b) > 1:
        data = [
            go.Scattermapbox(
                lat=reformatlat(AnalysedDF),
                lon=reformatlon(AnalysedDF),
                mode='markers+text',
                opacity=0.5,
                showlegend=False,
                text=reformatTextnumber(AnalysedDF),
                hoverinfo='text',
                hovertext=reformatTexthaouver(AnalysedDF),

                marker=go.scattermapbox.Marker(

                    size=b,
                    sizemin=min(b) / 10,
                    sizeref=min(b) / 10,
                    color='rgb(239,0,0)'
                ),

            )
        ]
    else:
        data = [
            go.Scattermapbox(
                lat=reformatlat(AnalysedDF),
                lon=reformatlon(AnalysedDF),
                mode='markers+text',
                opacity=0.5,
                showlegend=True,
                text=reformatTextnumber(AnalysedDF),
                # hoverinfo='none',
                hovertext=reformatTextnumber(AnalysedDF),

                marker=go.scattermapbox.Marker(
                    size=b,
                    color='rgb(239,0,0)'
                ),

            )
        ]

    return {
        'data': data,
        'layout': layout
    }


# app.css.append_css({
#    r"C:\Users\HamedM.MANAIA.000\PycharmProjects\COVID2019\Text.css"
# })

if __name__ == '__main__':
    app.run_server(debug=True)