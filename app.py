# Salzburg
# PB 04/08/22

import dash

from dash import dcc,html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

import numpy as np
import json

import pandas as pd
import netCDF4
import xarray as xr
from collections import OrderedDict

import datetime
import time

#from itertools import product
#from plotly.subplots import make_subplots
#import plotly.offline as offline
#from ipywidgets import HBox, VBox, Button, widgets

#import warnings
#warnings.filterwarnings('ignore')

#-----------------------------------------------

# Initialize app

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.SPACELAB])
server = app.server
mapbox_access_token = 'pk.eyJ1IjoiYnVwZSIsImEiOiJjanc3ZnpmMDEwYm1vNDNsbW15bXh3Y2RlIn0.DFOGHx9u2JThJKBQo1zDMQ'
mapbox_style = "mapbox://styles/bupe/cjw7g6cax0hem1cqy9vc9vln4"
colorapp = {"background": "#ffffff", "text": "#082255", "text2": "#082255"}



table1 = OrderedDict(
    [
        ("GCM", ["MQ [m³/s]:", "Dauerlinie 5% [m³/s]:", "MNQ [m³/s]:"]),
        ("1990-2020", [0, 0, 0]),
        ("2020-2050", ["", "", ""]),
    ]
)
table1 = pd.DataFrame(table1)

downloadclick = [None]

# Jahresgang
def minmax(v1,v2,v3,v4):
    min1 = min(min(v1),min(v2))
    max1 = max(max(v3),max(v4))
    return min1,max1

def geo_id(dd, dd_array):
   """
     search for nearest decimal degree in an array of decimal degrees and return the index.
     np.argmin returns the indices of minium value along an axis.
     so subtract dd from all values in dd_array, take absolute value and find index of minium.
   """
   geo_idx = (np.abs(dd_array - dd)).argmin()
   return geo_idx

def createtext(ts11,ts12,mnq1,mnq2,trigger1,trigger2,trigger3,para,x1,y1):

    text1 = dbc.Container(
        [
            dcc.Markdown(". "),
            dcc.Markdown("Standort:    Lat: " + str(xydata[trigger1][6]) + " Lon: " + str(xydata[trigger1][7])),
            dcc.Markdown("Höhe:    " + str(xydata[trigger1][5])+" m"),
            dcc.Markdown(str(xydata[trigger1][9]) + " / " + str(xydata[trigger1][10])),
            #dcc.Markdown(str(x1) + " " + str(y1)),
        ],
        style={'fontSize': 15, 'textAlign': 'left'}
    )

    col1 = "GCM: " + GCMS[trigger3]
    col2 = '1990-2020'
    col3 = '2020-2050'
    table1.columns = [col1, col2, col3]
    table1.loc[0, col2] = "{:.2f}".format(para[0])
    table1.loc[1, col2] = "{:.2f}".format(para[4])
    table1.loc[2, col2] = "{:.2f}".format(para[2])

    if trigger2 < 2050:
        table1.loc[0, col3] = ""
        table1.loc[1, col3] = ""
        table1.loc[2, col3] = ""
    else:
        table1.loc[0, col3] = "{:.2f}".format(para[1])
        table1.loc[1, col3] = "{:.2f}".format(para[5])
        table1.loc[2, col3] = "{:.2f}".format(para[3])

    table = dash_table.DataTable(
        data=table1.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in table1.columns],
        page_size=3,
        style_cell = {'fontSize': 15},

        style_cell_conditional=[
            {'if': {'column_id': col1},
             'textAlign': 'left'},
        ],
        tooltip_conditional=[
            {
                'if': {
                    'column_id': col1,
                    'row_index': 0
                },
                'type': 'markdown',
                'value': 'MQ: Durchschnitt der Zeitreihe für den angegebenen Zeitraum.'
            },
            {
                'if': {
                    'column_id': col1,
                    'row_index': 1
                },
                'type': 'markdown',
                'value': 'Dauerlinie 5%: Dauerlinie als Mittel aller Jahresdauerlinien. 5% = 18 Tage, an denen der Abfluss unterschritten wird.',
            },
            {
                'if': {
                    'column_id': col1,
                    'row_index': 2
                },
                'type': 'markdown',
                'value': 'MNQ: Mittlerer Niedrigwasserabfluss = Niedrigster Abfluss jeden Jahres, gemittelt über alle Jahre.'
            }
        ],
        css=[{
            'selector': '.dash-table-tooltip',
            'rule':  'font-size: 12px; background-color: grey; color: white; line-height: 12px'
        }],
        style_as_list_view=True,
        tooltip_delay=1,
        tooltip_duration=None,
    )


    #'fontSize': 12, 'font-family':'sans-serif', 'line-height': 15
    #dcc.Markdown("  Ø    Tage Dauerlinie 5%: {:5.0f} Tage zu: {:5.0f} Tage".format(para[6], para[7])),
    #dcc.Markdown("  Max. Tage Dauerlinie 5%: {:5.0f} Tage zu: {:5.0f} Tage".format(para[8], para[9])),

    return text1,table
#------------------------------------------------------

def updatefig(fig,figdat, figindex, mini, maxi, title):
    with fig.batch_update():
        fig.data[0].x = figdat.data[0].x
        fig.data[1].x = figdat.data[1].x
        fig.data[2].x = figdat.data[2].x
        fig.data[3].x = figdat.data[3].x

        fig.data[0].y = figdat.data[0].y
        fig.data[1].y = figdat.data[1].y
        fig.data[2].y = figdat.data[2].y
        fig.data[3].y = figdat.data[3].y

        fig.data[0].name = figdat.data[0].name
        fig.data[1].name = figdat.data[1].name
        fig.data[2].name = figdat.data[2].name
        fig.data[3].name = figdat.data[3].name

        fig.data[0].line = figdat.data[0].line
        fig.data[1].line = figdat.data[1].line
        fig.data[2].line = figdat.data[2].line
        fig.data[3].line = figdat.data[3].line

        fig.data[0].visible = figdat.data[0].visible
        fig.data[1].visible = figdat.data[1].visible
        fig.data[2].visible = figdat.data[2].visible
        fig.data[3].visible = figdat.data[3].visible

        fig.data[1].fill = figdat.data[1].fill
        fig.data[1].fillcolor = figdat.data[1].fillcolor
        fig.data[3].fill = figdat.data[3].fill
        fig.data[3].fillcolor = figdat.data[3].fillcolor

        fig.update_yaxes(range=[mini, maxi])
        fig.update_layout(showlegend=True)

        #if figindex == 2:
        #    fig.add_vline(x=2.5, line_width=3, line_dash="dash", line_color="blue")
        #    fig.add_vline(x=347, y0=0, y1=maxi, line_width=3, line_dash="dash", line_color="blue")
        #   fig.add_vline(x=14, line_width=3, line_dash="dash", line_color="blue")
        #else:
        #fig.layout.shapes = ()

        fig.layout.title = title
        fig.layout.xaxis.title = figdat.layout.xaxis.title

    if figindex == 2:
        fig.add_vline(x=347, line_width=3, line_dash="dash", line_color="blue")
    else:
        fig.layout.shapes = ()

    return fig

#--------------------------------------

def createscatter(tss,admin1,admin2,adavg1,adavg2,daumin1,daumin2,dauavg1,dauavg2,slider,index,GCMindex,figindex,para,xx1,yy1):

    dates[2] = dates[2].replace(year = int(slider)-30)
    dates[3] = dates[3].replace(year = int(slider)-1)

    ts11 = tss[dates[0]:dates[1]]
    ts12 = tss[dates[2]:dates[3]]

    mini2, maxi2 = minmax(admin1, admin2, adavg1, adavg2)
    maxi1 = tss.max()
    mini1 = tss.min()

    peri = periode[(slider - 2020) // 30]

    mnq1 = ts11.groupby(ts11.index.year).min().mean()
    mnq2 = ts12.groupby(ts12.index.year).min().mean()




    # reverse dauerlinei : dau1_mean[::-1]
    if figindex == 0:
        data2a = go.Scatter(y=ts11.values, x=ts11.index, mode='lines', name=GCMS[GCMindex] + ' 1990-2020', visible=True,
                            line=dict(color='blue', width=2))
        data2b = go.Scatter(y=ts12.values, x=ts11.index, mode='lines', name=GCMS[GCMindex] + peri, visible=True,
                            fill='tonexty', fillcolor="rgba(31,120,180,0.0)", line=dict(color='red', width=1))
        data2c = go.Scatter(y=ts11.values, x=ts11.index, mode='lines', name='--', visible=False, line=dict(width=0))
        data2d = go.Scatter(y=ts11.values, x=ts11.index, mode='lines', name='--', visible=False,
                            fill='tonexty', fillcolor="rgba(255,31,0,0.2)", line=dict(width=0))
        layout2 = dict(xaxis_title='Tage', yaxis_title='Abfluss [m<sup>3</sup>/s]')
        data2 = go.Figure(data=[data2c, data2d, data2a, data2b], layout=layout2)
        fig = go.Figure(data=[data2c, data2d, data2a, data2b], layout=layout2)

    if figindex == 1:

        #xx = np.arange(1, 366, 2)
        xx = pd.DatetimeIndex(np.arange('2004-01', '2005-01',2, dtype='datetime64[D]'))
        y1 = adavg1
        y2 = admin1
        if dates[1] == dates[3]:
            y3 = adavg1
            y4 = admin1
        else:
            y3 = adavg2
            y4 = admin2

        data3a = go.Scatter(y=y1, x=xx, mode='lines', name=GCMS[trigger[3]] + ' AVG 1990-2020',
                            line=dict(color='blue', width=2))
        data3b = go.Scatter(y=y2, x=xx, mode='lines', name=GCMS[trigger[3]] + ' MIN 1990-2020',
                            line=dict(color='blue', width=1),
                            visible=True, fill='tonexty', fillcolor="rgba(31,120,180,0.2)")
        data3c = go.Scatter(y=y3, x=xx, mode='lines', name=GCMS[trigger[3]] + ' AVG' + peri, visible=True,
                            line=dict(color='red', width=2))
        data3d = go.Scatter(y=y4, x=xx, mode='lines', name=GCMS[trigger[3]] + ' MIN' + peri,
                            line=dict(color='red', width=1),
                            visible=True, fill='tonexty', fillcolor="rgba(255,31,0,0.2)")

        layout3 = dict(xaxis_title='Tage', yaxis_title='Abfluss [m<sup>3</sup>/s]',xaxis_tickformat = '%e. %b')
        data3 = go.Figure(data=[data3c, data3d, data3a, data3b], layout=layout3)
        fig = go.Figure(data=[data3c, data3d, data3a, data3b], layout=layout3)

    if figindex == 2:
        xx = np.arange(1, 366, 2)
        y1 = dauavg1
        y2 = daumin1
        if dates[1] == dates[3]:
            y3 = dauavg1
            y4 = daumin1
        else:
            y3 = dauavg2
            y4 = daumin2

        data5a = go.Scatter(y=y1[::-1], x=xx, mode='lines', name=GCMS[GCMindex] + ' AVG 1990-2020', visible=True,
                            line=dict(color='blue', width=2))
        data5b = go.Scatter(y=y2[::-1], x=xx, mode='lines', name=GCMS[GCMindex] + ' MIN 1990-2020', visible=True,
                            line=dict(color='blue', width=1),
                            fill='tonexty', fillcolor="rgba(31,120,180,0.2)")

        data5c = go.Scatter(y=y3[::-1], x=xx, mode='lines', name=GCMS[GCMindex] + " AVG" + peri, visible=True,
                            line=dict(color='red', width=2))
        data5d = go.Scatter(y=y4[::-1], x=xx, mode='lines', name=GCMS[GCMindex] + " MIN" + peri, visible=True,
                            line=dict(color='red', width=1),
                            fill='tonexty', fillcolor="rgba(255,31,0,0.2)")

        layout5 = dict(xaxis_title='Überschreitungstage Tage', yaxis_title='Abfluss [m<sup>3</sup>/s]')
        data5 = go.Figure(data=[data5c, data5d, data5a, data5b], layout=layout5)
        fig = go.Figure(data=[data5c, data5d, data5a, data5b], layout=layout5)


    #fig = go.Figure(data=[data2a, data2b, data2c, data2d], layout=layout2)

    text1 =  "Lat: "+ str(xydata[index][6]) + " Lon: " + str(xydata[index][7])
    if slider == 2020:
        text1 += " Zeitraum: 1990-2020"
    else:
        text1 += " Zeitraum: 1990-2020 zu " + peri
    if figindex == 0:
        title = "<b>Zeitreihe: </b>"+ text1
        #title =str(mini1)+ " " + str(maxi1)
        updatefig(fig,data2, figindex, mini1, maxi1,title)
    if figindex == 1:
        title = "<b>Jahresgang: </b>" + text1
        updatefig(fig, data3, figindex, mini2, maxi2, title)
        #updatefig(data3,mini2,maxi2,title)
    if figindex == 2:
        title = "<b>Dauerlinie: </b>"+text1
        updatefig(fig, data5, figindex, 0, y1.data[182], title)
    #updatefig(data5,0,dau1_mean[360].max(),title)



    """
    fig.data[0].visible = True
    fig.data[1].visible = True
    fig.data[2].visible = False
    fig.data[3].visible = False
    """
    fig.update_layout(
        plot_bgcolor=colorapp["background"],
        paper_bgcolor=colorapp["background"],
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.3,
            xanchor="left",
            x=0.0
        )
    )

    text1,text2 = createtext(ts11, ts12,mnq1,mnq2, index, slider, GCMindex,para,xx1,yy1)

    return fig,text1,text2


# -------------------------------------------------
xyfile = "xydis_1km_geo.json"
xytestfile = "xydis2.txt"

GCMS = ["MOHC85","IPSL85","ICHEC85","ICHEC45"]
GCMindex1 = [0]

figtype = ["Zeitreihe","Jahresgang","Dauerlinie"]
#periode = [" 1990-2020"," 2020-2050"," 2050-2080"]
periode = [" 1990-2020"," 2020-2050"]

with open(xyfile) as f:
    xyshape = json.load(f)
# xydata = np.loadtxt(xytestfile, delimiter = ",",skiprows=1)
xydata = np.array(pd.read_csv(xytestfile, sep=',',encoding='latin1'))
xydata[:, 0:7] = xydata[:, 0:7].astype(float)
xyindex = xydata[:, 0].astype(int)
q = xydata[:, 4]
hovertext = '<b>mittlerer Durchfluss Q</b><br>ØQ: %{customdata[4]:.2f} m<sup>3</sup>/s<br>Lat: %{customdata[6]:.2f} Lon: %{customdata[7]:.2f} Höhe: %{customdata[5]:.0f}'
hovertext += '<extra>PG: %{customdata[9]}<br>PB: %{customdata[10]}</extra>'

#--------------------------------------------------------
color1=[[0.0, "rgba(255,255,255,0.1)"],
        [0.005,"rgba(31,120,180,0.8)"],
        [1.0, "rgba(178,223,138,0.8)"]]


start1date = datetime.datetime.strptime("01/01/1990", "%d/%m/%Y")
end1date = datetime.datetime.strptime("01/01/2020", "%d/%m/%Y") -datetime.timedelta(days=1)
start2date = datetime.datetime.strptime("01/01/2020", "%d/%m/%Y")
end2date = datetime.datetime.strptime("01/01/2050", "%d/%m/%Y") -datetime.timedelta(days=1)

dates = [start1date,end1date,start2date,end2date]


#filename = "P:/watmodel/CWATM/modelruns/pinzgau_1km/output/MOHC85/discharge_daily_xy.nc"
# filename = "C:/work/waterbalance/global_json/salzburg/niedrig2.nc"
filename = "niedrig_MOHC85.nc"
file = xr.open_dataset(filename,decode_times=False)

reference_date = '1990-01-01'
d = pd.date_range(start=reference_date, periods=file.sizes['time'],freq='MS')
xloc = file['x'][:]
yloc = file['y'][:]

in_x = 4524500
in_y = 2689500
indexno = 400
x_id = geo_id(in_x, xloc)
y_id = geo_id(in_y, yloc)

discharge =[]

discharge.append(file["dis_month"][:,:,:])
#dis_month = [file["dis_month"][:,:,:]]
discharge.append(file["annual_min2020"][:,:,:])
discharge.append(file["annual_min2050"][:,:,:])
discharge.append(file["annual_mean2020"][:,:,:])
discharge.append(file["annual_mean2050"][:,:,:])
discharge.append(file["duration_min2020"][:,:,:])
discharge.append(file["duration_min2050"][:,:,:])
discharge.append( file["duration_mean2020"][:,:,:])
discharge.append(file["duration_mean2050"][:,:,:])
discharge.append(file["para"][:,:,:])

file.close()

#v= dis_month[0][:,y_id,x_id].data
v = discharge[0][:,y_id,x_id].data
ts1 = pd.Series(v, index=d)
ts11 = ts1[dates[0]:dates[1]]
ts12 = ts1[dates[2]:dates[3]]



no = 2006 # close to Mittersill
trigger = [0,no,2010,0]

data2a = go.Scatter(y=ts11.values,x=ts11.index,mode='lines', name='MOHC 1990-2010',  visible= True, line = dict(color='blue', width=2))
data2b = go.Scatter(y=ts12.values,x=ts11.index,mode='lines', name='MOHC 1990-2010',  visible= True, line = dict(color='red', width=1))
data2c = go.Scatter(y=ts11.values,x=ts11.index,mode='lines', name='--', visible= False,line = dict(width=0))
data2d = go.Scatter(y=ts11.values,x=ts11.index,mode='lines', name='--', visible= False,line = dict(width=0))

layout2 = dict(title='Zeitreihe', xaxis_title = 'Tage', yaxis_title = 'Abfluss [m<sup>3</sup>/s]')

#textinfo = createtext(ts11, ts12,no,0)
textinfo = "bla"
# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------

nav_item = dbc.NavItem(dbc.NavLink("Link", href="#"))

logo = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                children=[
                    dbc.Row(
                        [
                            dbc.Col(html.Img(id="logo", src=app.get_asset_url("iiasa_logo.png"), height="60"),md=8),
                            dbc.Col(html.Hr(),md=2),
                            dbc.Col(dbc.NavbarBrand("WaterstressAT Pinzgau Dashboard", className="ml-1"),md=2),
                        ],
                        align="center"
                    ),
                ],
                href="https://iiasa.ac.at/projects/WaterStressAT",
            ),

            dbc.NavbarToggler(id="navbar-toggler1"),
            dbc.Collapse(
                #dbc.Nav(
                #    [nav_item, dropdown], className="ml-auto", navbar=True
                #),
                id="navbar-collapse2",
                navbar=True,
            ),
        ]
    ),
    #color="primary",
    color="primary",
    dark=True,
    className="mb-5",
    #fixed = "top",
    #sticky = "top",
)

jumbotron = dbc.Container(
    [
        dcc.Markdown('''
                    ##### Info
                    
                    **Wasserstress durch Klimawandel: Herausforderung und Möglichkeiten in Österreich - WasserstressAT**
                    
                    Österreich is ein wasserreiches Land in dem nur 3% des verfügbaren Wassers genutzt wird.
                    Jedoch, zeitlich und lokal wird der Klimawandel den Druck auf die Resource Frischwasser,
                    aufgrund höherer Temperaturen, verminderter Abflüsse und erhöhtem Verbrauch, erhöhen. 
                    
                    * [WasserstressAT](https://iiasa.ac.at/projects/WaterStressAT) ist ein Projekt von: IIASA, Umweltbundesamt, ZAMG, Uni Graz.
                    
                    * Hydrologische Berechnungen basieren auf dem Model [**CWatM**](https://cwatm.iiasa.ac.at/)

                    * Dieses Werkzeug wird zwar mit der Unterstützung des Landes Salzburg entwickelt, es handelt sich um einen ersten Entwurf des Projektes 
                    und ist in keinem Fall ein offizielles Produkt einer österreichischen Behörde.
                '''),
        html.Hr(),
        dcc.Markdown('''
            von [IIASA BNL/WAT Security](https://iiasa.ac.at/programs/biodiversity-and-natural-resources-bnr/water-security/)''')
    ],
    style={'fontSize': 12, 'font-family':'sans-serif', 'line-height': 15}
    #"overflow-x": "scroll" "white-space": "pre"
    #html.H6("Wasserstress durch Klimawandel: Herausforderung und Möglichkeiten in Österreich WasserstressAT"),
)


drop1_dbc = dbc.Form([
                html.P(
                    id="drop1-text",
                    children="",
                ),
                dcc.Dropdown(
                    id = "drop1",
                    options = [
                        {"label": "GCM: MOHC85", "value": "MOHC85"},
                        {"label": "GCM: IPSL85", "value": "IPSL85"},
                        {"label": "GCM: ICHEC85", "value": "ICHEC85"},
                        #{"label": "GCM: ICHEC45", "value": "ICHEC45"},
                    ],
                    value='MOHC85',
                    searchable=False,
                    clearable=False
                ),
])

"""
app.layout = html.Div(
    className="container",
    children=[
        dcc.Graph(
            id="graph-4",
            figure=fig,
            clear_on_unhover=True),
        dcc.Tooltip(
            id="graph-tooltip-4",
            loading_text="LOADING",
            direction="bottom"),
    ],
)
"""

drop2_dbc = dbc.Form(
    className="drop_box1",
    children=[
        html.P(
            id="drop2-text",
            children="",
        ),
        dcc.Dropdown(
            id="drop2",
            options=[
                {"label": "Diagramm: Zeitreihe", "value": "Zeitreihe"},
                {"label": "Diagramm: Jahresgang", "value": "Jahresgang"},
                {"label": "Diagramm: Dauerlinie", "value": "Dauerlinie"},
            ],
            value='Zeitreihe',
            searchable=False,
            clearable=False
        ),
        dcc.Tooltip(
            id="drop2-tooltip",
            loading_text="blabla",
            direction="bottom"
        ),
    ],
)

"""

drop2_dbc = dbc.Form([
                html.P(
                    id="drop2-text",
                    children="",
                ),
                dcc.Dropdown(
                    id = "drop2",
                    options = [
                        {"label": "Diagramm: Zeitreihe", "value": "Zeitreihe"},
                        {"label": "Diagramm: Jahresgang", "value": "Jahresgang"},
                        {"label": "Diagramm: Dauerlinie", "value": "Dauerlinie"},
                    ],
                    value='Zeitreihe',
                    searchable=False,
                    clearable=False
                ),
])
"""
slider_dbc = dbc.Form([
                html.P(
                    id="slider-text",
                    children="",
                    style={'clear': 'both'}
                ),
                dcc.Slider(
                    id="year-slider",
                    min=2020,
                    max=2050,
                    step = 30,
                    value=2020,

                    marks={
                        str(2020+year): {
                            "label": str(2020+year),
                            "style": {"color": "#082255"},
                        }
                        for year in  range(0, 31, 30)
                    },
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
])

map_dbc = dbc.Form([
        dcc.Graph(
            id="salzburg-choropleth",
            config={'displayModeBar': False},
            figure=dict(
                layout=dict(
                    mapbox=dict(),
                    plot_bgcolor=colorapp["background"],
                    paper_bgcolor=colorapp["background"],
                    autosize=False,
                    # showlegend=False,
                    #uirevision
                ),
            ),
        ),
])


scatter_dbc = dbc.Form([
        dcc.Markdown(""),
        html.Div(
            id="scatter1",
            children=[
                dcc.Graph(id='scatterplot1',
                          config={'displayModeBar': False},
                          style={'height': 400, 'width': 580}
                          #style={'height': 350}
                          )],
        ),
])


# LAYOUT

app.layout = dbc.Container([
        #dcc.Store(id='sunburstlevel'),

        html.Div([logo]),

        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(html.H5("Salzach und Saalach Einzugsgebiet")),
                        dbc.Row(html.Div([
                            html.Button("Download Beschreibung", id="btn_pdf"), dcc.Download(id="download-pdf"),
                            dcc.Tooltip(id="beschreibung-tooltip", loading_text ="blaaaTooltip text", background_color = "red", show= True, direction= "right"),
                        ])),
                    ],width=7),





                    #html.H5("Salzach und Saalach Einzugsgebiet"),width = 7),
                dbc.Col(
                    [
                        dbc.Row(drop1_dbc),
                        dbc.Row(drop2_dbc),
                        dbc.Row(slider_dbc)
                    ],width=3),
                dbc.Col(html.H5(" "),width = 2),
            ],
        ),

        dbc.Row(
            [
                dbc.Col(map_dbc),
                dbc.Col(scatter_dbc),
            ],
        ),

        dbc.Row(
            [
                dbc.Col(html.Div(id='my-output1')),
                dbc.Col(html.Div(id='x1')),
                dbc.Col(html.Div(id='my-output2')),
                #dbc.Col(html.Div(id='x2'))
                #dbc.Col(html.Div([html.Button("Download Daten für diese Zelle als csv", id="btn_data"), dcc.Download(id="download-data")])),

            ],
        ),


        html.H1(""),

    dbc.Row(
        [
            dbc.Col(html.Div([jumbotron], className="info")),
            dbc.Col(html.Div(id='info2')),
        ],
    ),





],
    #fluid = True,

)


ii =1

#----------------------------
# ScatterPLOT

# update scatterplot
@app.callback(
    Output('scatterplot1', 'figure'),
    Output(component_id='my-output1', component_property='children'),
    Output(component_id='my-output2', component_property='children'),
    [Input("salzburg-choropleth", "clickData"),
     Input('drop1', 'value'),
     Input('drop2', 'value'),
     Input('year-slider', 'value')])

def update_scatter1(input_value,d1value,d2value,slider):

    # dropbox GCM
    GCMindex = GCMS.index(d1value)
    figindex = figtype.index(d2value)

    # laod new GCM
    if GCMindex != GCMindex1[0]:
        GCMindex1[0] = GCMindex
        filename = "niedrig_" + GCMS[GCMindex] + ".nc"
        file = xr.open_dataset(filename, decode_times=False)

        #dis_month = [file["dis_month"][:, :, :]]
        discharge[0] = file["dis_month"][:, :, :]
        discharge[1] = file["annual_min2020"][:, :, :]
        discharge[2] = file["annual_min2050"][:, :, :]
        discharge[3] = file["annual_mean2020"][:, :, :]
        discharge[4] = file["annual_mean2050"][:, :, :]
        discharge[5] = file["duration_min2020"][:, :, :]
        discharge[6] = file["duration_min2050"][:, :, :]
        discharge[7] = file["duration_mean2020"][:, :, :]
        discharge[8] = file["duration_mean2050"][:, :, :]
        discharge[9] = file["para"][:, :, :]
        file.close()


    if input_value is None:
        index = 2006
    else:
        index = input_value['points'][0]['pointIndex']

    loc = xydata[index][1]
    y1 = int(105 - (loc // 109))
    x1 = int(loc % 109)

    #----------------------------
    #yy = dis_month[0][:, y1, x1].data
    yy = discharge[0][:, y1, x1].data
    tss = pd.Series(yy, index=d)

    admin1 = discharge[1][:, y1, x1]
    admin2 = discharge[2][:, y1, x1]
    adavg1 = discharge[3][:, y1, x1]
    adavg2 = discharge[4][:, y1, x1]

    daumin1 = discharge[5][:, y1, x1]
    daumin2 = discharge[6][:, y1, x1]
    dauavg1 = discharge[7][:, y1, x1]
    dauavg2 = discharge[8][:, y1, x1]
    para = discharge[9][:, y1, x1]


    fig,text1,text2 = createscatter(tss,admin1,admin2,adavg1,adavg2,daumin1,daumin2,dauavg1,dauavg2, slider,index,GCMindex,figindex,para,x1,y1)

    return fig,text1,text2


# -------------------------------------------------
# map Salzburg map
@app.callback(
    Output("salzburg-choropleth", "figure"),
    [Input("year-slider", "value")],
    [State("salzburg-choropleth", "figure")],
)
def display_map(year, figure):

    # https://plotly.com/python/builtin-colorscales/
    # fig = go.Figure(go.Choroplethmapbox(name="Global Basins", geojson=global_basins, locations=globalinfo.index, z=zzz,
    # portland balance
    fig = go.Figure(go.Choroplethmapbox(name ="WasserstressAT",geojson=xyshape, locations=xyindex,z=q,customdata= xydata,
                            colorscale=color1, zmin=0, zmax=max(q),marker_line_color="grey", marker_line_width=0.2,
                            hovertemplate=hovertext))

    fig.update_layout(mapbox_accesstoken=mapbox_access_token,
                   mapbox_style= "mapbox://styles/bupe/cjw7g6cax0hem1cqy9vc9vln4",
                   mapbox_center={"lat": 47.5, "lon": 12.7},
                   mapbox_pitch=0, mapbox_zoom=7.7,
                   margin={"r": 0, "t": 0, "l": 0, "b": 0},
                   height= 400,
                   autosize=False,
                   uirevision=True,
                   dragmode=False,
                   )
    return fig

#----------------------------------
@app.callback(
    Output("download-pdf", "data"),
    Input("btn_pdf", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_file(
        "./assets/waterstressat_pinzgau2.pdf"
    )
# ------------------------------------
"""
@app.callback(
    Output("download-data", "data"),
    Input("btn_data", "n_clicks"),
    Input("salzburg-choropleth", "clickData"),
    Input('drop1', 'value'),
    prevent_initial_call=True,
)
def func(n_clicks,input_value,d1value):



    if str(n_clicks) == str(downloadclick[0]):
        return
    else:
        downloadclick[0] = str(n_clicks)

        if input_value is None:
            index = 2006
        else:
            index = input_value['points'][0]['pointIndex']
        latlon = "_lat" + str(xydata[index][6]) + "_lon" + str(xydata[index][7])
        GCMindex = GCMS.index(d1value)
        name = "waterstressAT_data_" + GCMS[GCMindex] + latlon + "_" + str(downloadclick[0]) + str(n_clicks)+ ".csv"


        dftest = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 1, 5, 6], "c": ["x", "x", "y", "y"]})

        
        #discharge[0] = file["dis_month"][:, :, :]
        
        #return dcc.send_data_frame(dftest.to_csv, name)
        text = "blbalabla\n1,2,3,4\n5,6,7,8\n"
        return dict(content= text, filename=name)
"""
# ---------------------------------------------------

if __name__ == "__main__":
    app.run_server(debug=True)