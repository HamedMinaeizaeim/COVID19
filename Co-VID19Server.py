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


def readCSV():
    FilePath = r"InputData.csv"
    return pd.read_csv(FilePath, engine='python')


def filterDay(Df, FilterDay):
    return Df[Df['Day'] <= FilterDay]


def filterandGreoup(Df, FilterDay):
    Df = Df[Df['Day'] <= FilterDay]
    Df=Df.sort_values(by=['Day'],ascending=False )
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
    Date = (AnalysedDF['Report Date'].tolist())
    return ['Number Of cases in ' + str(City[index]) + ' DHB at '+str(Date[index])+'  is ' + str(x) for index, x in enumerate(textnumber)]


def reformatTextnumber(AnalysedDF):
    textnumber = (AnalysedDF['DHB2015_Name'].tolist())
    return [str(x) for x in textnumber]


def checkNumberSize(AnalysedDF):
    return AnalysedDF['DHB2015_Name'].tolist()


def convrtArray(OldArray):
    if len(OldArray) > 1:
        if max(OldArray)>min(OldArray):
            x = np.array([min(OldArray),min(OldArray)+((max(OldArray)-min(OldArray)))/3.0 ,
                          min(OldArray)+2*((max(OldArray)-min(OldArray)))/3.0, max(OldArray)])

            y = np.array([1, 2.5, 3.5, 5.5])
            f = interp1d(x, y, kind='cubic')
        else:
            x = np.array([min(OldArray), min(OldArray) + ((max(OldArray) - min(OldArray))) / 3.0,
                          min(OldArray) + 2 * ((max(OldArray) - min(OldArray))) / 3.0, max(OldArray)])

            y = np.array([1, 1, 1, 1])
            f = interp1d(x, y, kind='linear')

    else:
        x = np.array([min(OldArray), max(OldArray)])
        y = x
        f = interp1d(x, y)

    return f(OldArray)

Summary=pd.read_csv('Summary.csv', engine='python')

Df = readCSV()
AnalysedDF = filterandGreoup(Df, Df['Day'].max())
Numbersize = checkNumberSize(AnalysedDF)
b = convrtArray(Numbersize)

#
DfAnalysed2 = Df.groupby('Report Date').agg({'DHB2015_Name': 'count'})
DfAnalysed2['DateColumn'] = DfAnalysed2.index
DfAnalysed2['DateColumn'] = pd.to_datetime(DfAnalysed2['DateColumn'], format='%d/%m/%Y')
DfAnalysed2 = DfAnalysed2.sort_values(by=['DateColumn'], ascending=False)
indexAll = DfAnalysed2.index.tolist()


# Sort value for DHB
Df=filterDay(Df,Df['Day'].max())
DfAnalysed3 = Df.groupby('DHB').agg({'DHB2015_Name': 'count'})
DfAnalysed3['DHB'] = DfAnalysed3.index
DfAnalysed3 = DfAnalysed3.sort_values(by=['DHB2015_Name'], ascending=True)
xDHB = DfAnalysed3['DHB2015_Name'].tolist()
yDHB = DfAnalysed3['DHB'].tolist()

traceDHB = go.Bar(x=xDHB, y=yDHB,
                orientation='h',
                text=yDHB,
                textposition='auto',
                marker=dict(
                    color='rgba(58,196,127, 0.8)',
                    line=dict(color='rgba(11, 39, 25, 1.0)', width=1)
                ))

#Per Age Group
Df=filterDay(Df,Df['Day'].max())
DfAnalysed4=Df[['Sex','Age group', 'DHB2015_Name' ]]
DfAnalysed4 = pd.pivot_table(DfAnalysed4, index='Sex', columns=['Age group'], values='DHB2015_Name', aggfunc='count')
DfAnalysed4 = DfAnalysed4.fillna(0)


TraceMale = go.Bar(x=DfAnalysed4.columns.tolist(), y=DfAnalysed4.loc['Male',:], name='Male' )
TraceFemale = go.Bar(x=DfAnalysed4.columns.tolist(), y=DfAnalysed4.loc['Female',:],  name='FeMale')




for index in indexAll:
    DF_Filter = DfAnalysed2[DfAnalysed2['DateColumn'] <= DfAnalysed2.loc[index, 'DateColumn']]
    DfAnalysed2.loc[index, 'DHB2015_Name'] = DF_Filter['DHB2015_Name'].sum()

x = DfAnalysed2['DHB2015_Name'].tolist()


DfAnalysed2['DateColumn'] = DfAnalysed2['DateColumn'].dt.strftime('%d/%m')
y = DfAnalysed2['DateColumn'].tolist()


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
        opacity=0.6,
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
        zoom=4.2,

    ),
)

colors = {
    'background': '#000000',
    'text': '#bdbdbd',
    'Section': '#525252',
    'textColor1': '#e32e2e',
    'textColor2': '#fab91c',
    'textColor3': '#0545d8',
    'textColor4': '#ffffff',
    'White': '#ffffff'
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
                    html.H3(children='Number of confirmed and probable cases'),
                    html.H2(children=str(Summary.loc[0, 'Con']), style={'color': colors['textColor2']})
                ],
                style={'width': '100%', 'display': 'inline-block', 'textAlign': 'center', 'padding': 0,
                       'border-style': 'solid ', 'vertical-align': 'top', 'backgroundColor': colors['Section'],
                       'color': colors['text'], 'margin-top': 3, 'margin-bottom': 3}
            ),
            html.Div(
                [
                    html.H3(children='Number of recovered cases '),
                    html.H2(children=str(Summary.loc[0, 'Reco']), style={'color': colors['textColor3']})
                ],
                style={'width': '100%', 'display': 'inline-block', 'textAlign': 'center', 'padding': 0,
                       'border-style': 'solid ', 'vertical-align': 'top', 'backgroundColor': colors['Section'],
                       'color': colors['text'], 'margin-top': 3, 'margin-bottom': 3}
            )
            , html.Div(
                [html.H3(children='Number of cases in hospital'),
                 html.H2(children=str(Summary.loc[0, 'hos']), style={'color': colors['textColor1']})
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
                    'layout': layout
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
                    'layout': {'title': {'text': 'Total Number of cases', 'font': {"size": 11}},
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
                  marks={str(int(Day)): str(int(Day))+' day' for Day in Df['Day'].unique()},
                  step=None
              )
              ],  style = {'width': '96%','display': 'inline-block', 'padding': 10, 'border-style': 'solid ',
                               'vertical-align': 'middle', 'textAlign': 'right', 'backgroundColor': colors['White'],
                         'color': colors['background'],'textAlign': 'center', 'margin-right': 10, 'margin-left': 10,
                'margin-top': 10, 'margin-bottom': 10}
             ),
    html.Div([
             html.Div([
                 dcc.Graph(
                     id='DHB-graph',
                     figure={
                         'data': [traceDHB],
                         'layout': {'title': {'text': 'Total Number of cases per DHB', 'font': {"size": 11}},
                                    'plot_bgcolor': colors['Section'],
                                    'paper_bgcolor': colors['Section'],
                                    'font': {'color': colors['textColor4'], "size": 8 },


                                    }
                     })

             ], style={'width': '42%', 'display': 'inline-block', 'padding': 10, 'border-style': 'solid ',
              'vertical-align': 'middle', 'textAlign': 'right', 'backgroundColor': colors['Section'],
              'color': colors['text'], 'textAlign': 'center', 'margin-right': 10, 'margin-left': 10}
             ),
             html.Div([
                 dcc.Graph(
                     id='Sex-graph',
                     figure={
                         'data': [TraceMale, TraceFemale],
                         'layout': {'title': {'text': 'Total Number of cases per DHB', 'font': {"size": 11}},
                                    'plot_bgcolor': colors['Section'],
                                    'paper_bgcolor': colors['Section'],
                                    'font': {'color': colors['textColor4'], "size": 8},
                                    'barmode': 'stack'

                                    }
                     })


             ], style={'width': '42%', 'display': 'inline-block', 'padding': 10, 'border-style': 'solid ',
              'vertical-align': 'middle', 'textAlign': 'right', 'backgroundColor': colors['Section'],
              'color': colors['text'], 'textAlign': 'center', 'margin-right': 10, 'margin-left': 10}
             ),

    ], style={'width': '100%', 'display': 'inline-block', 'padding': 10, 'border-style': 'solid ',
              'vertical-align': 'middle', 'textAlign': 'right', 'backgroundColor': colors['Section'],
              'color': colors['text'], 'textAlign': 'center', 'margin-right': 10, 'margin-left': 10}
    )
    ], style={'backgroundColor': colors['background'], 'color': colors['text']}



    )


@app.callback(
    Output('Sex-graph', 'figure'),
    [Input('Day-slider', 'value')])
def update_figure(Day):
    Df = readCSV()
    Df = filterDay(Df, Day)
    DfAnalysed4 = Df[['Sex', 'Age group', 'DHB2015_Name']]
    DfAnalysed4 = pd.pivot_table(DfAnalysed4, index='Sex', columns=['Age group'], values='DHB2015_Name',
                                 aggfunc='count')
    DfAnalysed4 = DfAnalysed4.fillna(0)

    TraceMale = go.Bar(x=DfAnalysed4.columns.tolist(), y=DfAnalysed4.loc['Male', :], name='Male')
    TraceFemale = go.Bar(x=DfAnalysed4.columns.tolist(), y=DfAnalysed4.loc['Female', :], name='FeMale')
    figure = {
        'data': [TraceMale, TraceFemale],
        'layout': {'title': {'text': 'Total Number of cases per DHB', 'font': {"size": 11}},
                   'plot_bgcolor': colors['Section'],
                   'paper_bgcolor': colors['Section'],
                   'font': {'color': colors['textColor4'], "size": 8},
                   'barmode': 'stack'

                   }
             }
    return  figure


@app.callback(
    Output('DHB-graph', 'figure'),
    [Input('Day-slider', 'value')])
def update_figure(Day):
    Df = readCSV()
    Df = filterDay(Df, Day)
    DfAnalysed3 = Df.groupby('DHB').agg({'DHB2015_Name': 'count'})
    DfAnalysed3['DHB'] = DfAnalysed3.index
    DfAnalysed3 = DfAnalysed3.sort_values(by=['DHB2015_Name'], ascending=True)
    xDHB = DfAnalysed3['DHB2015_Name'].tolist()
    yDHB = DfAnalysed3['DHB'].tolist()

    traceDHB = go.Bar(x=xDHB, y=yDHB,
                    orientation='h',
                    text=yDHB,
                    textposition='auto',
                    marker=dict(
                        color='rgba(58,196,127, 0.8)',
                        line=dict(color='rgba(11, 39, 25, 1.0)', width=1)
                    ))

    figure = {
        'data': [traceDHB],
        'layout': {'title': {'text': 'Total Number of cases per DHB', 'font': {"size": 11}},
                   'plot_bgcolor': colors['Section'],
                   'paper_bgcolor': colors['Section'],
                   'font': {'color': colors['textColor4'], "size": 8},

                   }
    }
    return figure



@app.callback(
    Output('Bubble-graph', 'figure'),
    [Input('Day-slider', 'value')])
def update_figure(Day):
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

    figure = {
        'data': data,
        'layout': layout
    }
    return  figure


# app.css.append_css({
#    r"C:\Users\HamedM.MANAIA.000\PycharmProjects\COVID2019\Text.css"
# })

if __name__ == '__main__':
    app.run_server(debug=True)