import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import ruptures as rpt
import plotly.express as px
import plotly.graph_objects as go
import datetime
from datetime import  date
import uuid
import random
FA = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    }, dbc.themes.BOOTSTRAP,
    {
        "href": "https://use.fontawesome.com/releases/v5.12.1/css/all.css?",
        "rel": "stylesheet",
    },

]
# import data 
covid_data = pd.read_csv('covid_preds.csv')
subway_data = pd.read_csv('subway_preds.csv')

# round figures
covid_data["Abs 7 day Difference"] = covid_data["Abs 7 day Difference"].round(2)
subway_data["Abs 7 day Difference"] = subway_data["Abs 7 day Difference"].round(2)
covid_data["Abs 14 day Difference"] = covid_data["Abs 14 day Difference"].round(2)
subway_data["Abs 14 day Difference"] = subway_data["Abs 14 day Difference"].round(2)

# Convert dates to datetime format
covid_data["Date"] = pd.to_datetime(covid_data["Date"])
subway_data["Date"] = pd.to_datetime((subway_data["Date"]))

# Converting String dates to datetime format
jhu_df = pd.read_csv('jhu_events.csv')
ds = jhu_df["Date"]
nds = []
for d in ds:
    d = d.replace(',', '')
    #d = datetime.datetime.strptime(d, '%b %d %Y').strftime('%Y-%m-%d')
    nds.append(d)
jhu_df["Date"] = nds
jhu_df = jhu_df[["Date", "Event Descriptions"]]
jhu_df["Date"] = pd.to_datetime(jhu_df["Date"])
jhu_df = jhu_df.loc[jhu_df["Date"] < "2021-03-01"]
#print(nds)
#print(jhu_df.loc[(jhu_df["Date"] =="2020-09-03")].sort_values(by="Date"))

# condense all events on the same day to 1 cell
event_data = jhu_df.groupby('Date')["Event Descriptions"].apply('----> \n'.join).reset_index()
event_data.to_csv("all_events.csv", index= False)

covid_data = covid_data.merge(event_data, left_on="Date", right_on="Date", how="left")
covid_data["Event Descriptions"].fillna(method="ffill", inplace=True)

subway_data = subway_data.merge(event_data, left_on="Date", right_on="Date", how="left")
subway_data["Event Descriptions"].fillna(method="ffill", inplace=True)



ev_covid_fig = go.Figure(data=go.Scatter(x=covid_data["Date"], y=covid_data["MA Cases"], mode="lines",
                                         name="Moving Average of COVID-19 Cases"))
ev_covid_fig.add_trace(go.Scatter(x=covid_data["Date"], y=covid_data["7 days Ahead Forecasted Values"], mode="lines",
                                  name="LSTM 7 Prediction"))

ev_covid_fig.update_layout(
    xaxis_tickformat='%B <br>%Y',
legend = dict(
    yanchor="top",
    y=0.99,
    xanchor="right",
    x=0.69
)
)
ev_covid_fig.update_layout(
    {'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)', })


ev_subway_fig = go.Figure(data=go.Scatter(x=subway_data["Date"], y=subway_data["MA Entries"], mode="lines",
                                          name="Moving Average of Subway Entries"))
ev_subway_fig.add_trace(go.Scatter(x=subway_data["Date"], y=subway_data["7 days Ahead Forecasted Values"], mode="lines",
                                   name="LSTM 7 Prediction"))
ev_subway_fig.update_layout(
    xaxis_tickformat='%B <br>%Y',
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99
    ))

ev_subway_fig.update_layout(
    {'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)', })


rt_covid_df = pd.read_csv('rt_covid.csv')

rt_subway_df = pd.read_csv('rt_subway.csv')

rt_covid_fig = go.Figure(data=go.Scatter(x=rt_covid_df["date_of_interest"], y=rt_covid_df["MA Cases"], mode="lines",
                                         name="Moving Average of COVID-19 Cases"))
rt_covid_fig.add_trace((go.Scatter(x= rt_covid_df["date_of_interest"], y= rt_covid_df["CASE_COUNT"], mode="lines", name="COVID-19 Cases in New York City")))
#rt_covid_fig.update_xaxes(showgrid=False)
#rt_covid_fig.update_yaxes(showgrid=False)
rt_covid_fig.update_layout(template= "plotly_dark")

rt_covid_fig.update_layout(
    {'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)', })

rt_subway_fig = go.Figure(data=go.Scatter(x=rt_subway_df["Date"], y=rt_subway_df["MA Entries"], mode="lines",
                                         name="Moving Average of COVID-19 Cases"),)
#rt_subway_fig.update_xaxes(showgrid=False)
#rt_subway_fig.update_yaxes(showgrid=False)
rt_subway_fig.update_layout(template= "plotly_dark")

rt_subway_fig.add_trace(go.Scatter(x=rt_subway_df["Date"], y=rt_subway_df["Subways: Total Estimated Ridership"], mode="lines",
                                   name="Subway Usage Numbers in New York City"))
rt_subway_fig.update_layout(
    {'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)', }
)


app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                dcc.Location(id="url", refresh=False),
                html.Div(id='page-content')
            ]
        ),
    ]
)
LOGO = "../../assets/icon.ico"

search_bar = dbc.Row(
    [
        #dbc.Col(dbc.Input(type="search", placeholder="Search")),
        dbc.Col(
            dbc.NavItem(dbc.NavLink('Home', href="/")),
        ),
    ],
    no_gutters=True,
    #className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

# make a reuseable navitem for the different examples
nav_item = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("Event Impact", href="/events"), ),
        dbc.NavItem(dbc.NavLink("Change Point Detection", href="/changepoints"), ),
        dbc.NavItem(dbc.NavLink("Daily Data", href="/daily-data"), ),
        dbc.NavItem(dbc.NavLink("Team", href="/team"), )
    ],
    horizontal= "end"


)
# make a reuseable dropdown for the different examples
dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Event Impact Tool"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Change Point Detection Tool"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Daily Data"),
    ],
    nav=True,
    in_navbar=True,
    label="Tools",
)



navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=LOGO, height="30px")),
                        dbc.Col(dbc.NavbarBrand("COVID-19 & Subway Usage Event Impact", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="/",
                style={"textDecoration": "none"},
            ),
                dbc.Nav(
                    [nav_item, ],
                    #className="ms-auto",
                    navbar=True,
                    horizontal= "end"

                ),

        ],
    ),
    color="black",
    dark=True,
    #className="mb-5",
)

'''dbc.NavbarSimple(
    children=[
        #dbc.NavItem(dbc.NavLink('Home', href="/")),
        dbc.NavItem(dbc.NavLink("Events", href="/events", className="nav-pills")),
        dbc.NavItem(dbc.NavLink("Change Points", href="/changepoints")),
        dbc.NavItem(dbc.NavLink("Daily Data", href="/daily-data")),
        dbc.NavItem(dbc.NavLink("Team", href="/daily-data"))
    ],
    brand="Event Impact",
    brand_href="/",
    color="black",
    dark=True,
    fixed="top"
)'''
arrows = html.Div(
                  children=[

                  ],
            )
scroll = html.Div(className="scrolldown",
           children=html.Div(className="chevrons",
                  children=[html.Div(className="chevrondown"),
                            html.Div(className="chervondown")]))
title = html.Div(
            children=[
                #html.P(children="📊", className="header-emoji"),
                html.H1(
                    children="Impact of Public Policies and Events on COVID-19 Cases & Subway Usage in NYC", className="header-title"
                ),
                scroll

                #html.Div(className="chevron", key="str(random.randint(a, b))"),
                #html.Div(className="chevron", key="str(random.randint(a, b))"),
            ],
            className="header",
        )
team_title = html.Div(
            children=[
                #html.P(children="📊", className="header-emoji"),
                html.H1(
                    children="Team", className="header-title"
                ),
                scroll

                #html.Div(className="chevron", key="str(random.randint(a, b))"),
                #html.Div(className="chevron", key="str(random.randint(a, b))"),
            ],
            className="header",
        )
tools = html.Div(
    html.Div(
        children=[
        html.Div(
            html.Div(
                html.Div(
                    children=[
                    html.H2("01"),
                    html.H3("Event Impact Tool"),
                    html.P("This tool shows you when the top 10 event impacts happened and how much the impact was. It also allows you to check for an event impact at any given date"),
                    html.A("Click Here for access", href="/events")
                ], className="content"),
                className="box"),
        className="card"),
        html.Div(
            html.Div(
                html.Div(
                    children=[
                        html.H2("02"),
                        html.H3("Change Point Detection Tool"),
                        html.P("This tool allows you to play around with the change point detection technique we used. You can use it to see when major change points happened. "),
                        html.A("Click Here for access", href="/changepoints")
                    ], className="content"),
                className="box"),
            className="card"),
            html.Div(
                html.Div(
                    html.Div(
                        children=[
                            html.H2("03"),
                            html.H3("Daily Data"),
                            html.P("The Daily data tool is updated everyday at 12 PST and allows users to see what the top 10 impacts were till date"),
                            html.A("Click Here for access", href="/daily-data")
                        ], className="content"),
                    className="box"),
                className="card"),
        ],
    className= "container2"
    )
)
info = html.Div(
    children=[
        html.Div(
        children=[
            html.H1("Overview", className="subheading"),
            html.P("We created a framework to measure the impact that events have had on COVID-19 cases and subway usage in New York City using data posted on the CDC and the MTA websites. We use a combination of change point detection and nueral networks to generate the impact. Change point detection tells us when there was a significant change in the data and the Nueral Network was trained to predict what both COVID-19 cases and subway usage numbers would have been like 7 days ahead had nothing changed.", className="descr"),
        ],
        className="card"),
        html.Div(
        children=[
            html.H1("Explore Our Work", className="subheading"),
            tools,
        ],

        className="card")])


event_title = html.Div(
            children=[
                #html.P(children="📊", className="header-emoji"),
                html.H1(
                    children="Event Impact Tool", className="header-title"
                ),
                html.P(
                    children=""
                             ""
                             "",
                    className="header-description",
                ),
                scroll

            ],
            className="header",
        )
cpd_title = html.Div(
            children=[
                #html.P(children="📊", className="header-emoji"),
                html.H1(
                    children="Change Point Detection Tool", className="header-title"
                ),
                html.P(
                    children=""
                             ""
                             "",
                    className="header-description",
                ),
                scroll
            ],
            className="header",
        )
real_time_title = html.Div(
            children=[
                #html.P(children="📊", className="header-emoji"),
                html.H1(
                    children="Daily Data", className="header-title"
                ),
                html.P(
                    children=""
                             ""
                             "",
                    className="header-description",
                ),
                scroll
            ],
            className="header",
        )
event_graphs = html.Div(
            children=[
                    html.Div("Event Impact Tool", className="subheading2"),
                    html.Div(className="container2",
                             children=[
                                 dbc.Button("Calculate Top 10 Most Impactful Events", id="calculate-btn", n_clicks=0, className="btn"),
                                 dbc.Button("Clear", id="clear-btn", n_clicks=0, className="btn")],),

                    dbc.Spinner(children=[html.Div("COVID-19 Cases in NYC", className="subheading2"),
                                          dcc.Graph(
                        id="events-covid-chart",
                        figure= ev_covid_fig,
                        config={"displayModeBar": False, "edits": {"legendPosition":False}},

                    ),], color="dark", fullscreen=False),



                    dbc.Spinner(children=[
                    html.Div("LSTM 7 Table", className= "table-name"),
                    dash_table.DataTable(
                        style_cell={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'fontSize': 14, 'font-family': 'sans-serif'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'Event Descriptions'},
                                'textAlign': 'left'
                            }
                        ],
                        id="covid-event-table",
                        columns=[],
                        data=[]
                    ),html.Div("LSTM 14 Table", className= "table-name"),
                                          dash_table.DataTable(
                        style_cell={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'fontSize': 14, 'font-family': 'sans-serif'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'Event Descriptions'},
                                'textAlign': 'left'
                            }
                        ],
                        id="covid-event-14table",
                        columns=[],
                        data=[]
                    ),],color="info", fullscreen=False),


                    html.Div("Subway Entries in NYC", className="subheading2"),
                    dbc.Spinner(children=[dcc.Graph(
                        id="events-subway-chart",
                        figure= ev_subway_fig,
                        config={"displayModeBar": False}
                    ),], color="dark", fullscreen= False, ),
                    dbc.Spinner(children=[
                    html.Div("LSTM 7 Table", className="table-name"),
                    dash_table.DataTable(
                        style_cell={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'fontSize': 14, 'font-family': 'sans-serif'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'Event Descriptions'},
                                'textAlign': 'left'
                            }
                        ],
                        id="subway-event-table",
                        columns=[],
                        data=[]
                    ),
                    html.Div("LSTM 14 Table", className="table-name"),
                    dash_table.DataTable(
                        style_cell={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'fontSize': 14, 'font-family': 'sans-serif'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'Event Descriptions'},
                                'textAlign': 'left'
                            }
                        ],
                        id="subway-event-14table",
                        columns=[],
                        data=[]
                    ),], color="info", fullscreen=False)
                    #table,
            ],
            className="graph-card",
        )
rt_graphs = html.Div(
    children=[
        html.Div("COVID-19 Cases in NYC", className="subheading2"),
        dcc.Graph(
            id="rt-covid-chart",
            figure=rt_covid_fig,
            config={"displayModeBar": False}
        ),
        html.Div("Subway Usage in NYC", className="subheading2"),
        dbc.Spinner(children =[dcc.Graph(
            id="rt-subway-chart",
            figure=rt_subway_fig,
            config={"displayModeBar": False}
        )], size="lg", color= "dark", type= "border", fullscreen= True)
    ]

)
#team = html.Div(
#        children=[
##            html.H1("Team", className="subheading"),
##           html.P("Amit Hiremath, Ziqian Dong & Roberto Rojas-Cessa", className="descr"),
#        ],
#        className="card",
#    )


upload=html.Div(
        children=[
dcc.Upload(
    id='upload-data',
    children=html.Div([
        'Drag and Drop or ',
        html.A('Select Files')
    ]),
    style={
        'width': '50%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin': '20px auto 0 auto',
    },
    # Allow multiple files to be uploaded
    multiple=True,
),
html.Div(id='output-data-upload'),
    ]
)

index_page = html.Div(
    children=[
        navbar,
        title,
        info,
    ]
    ,
)
events_page = html.Div(
    children=[
        navbar,
        event_title,
        html.Div(
            children=[
                html.Div(
                    children="How to use this tool",
                    className="subheading"
                ),
                html.P("This is the tool that we created to help measure the impacts of events on Both COVID-19 and Subway entries in New York City. Check for your event impacts by adding an event below.", className="descr2"),
            ],
            className="card",
        ),
        html.Div(
            children=[
                html.Div(
                    children="Add an Event",
                    className="subheading2"
                ),
                dcc.DatePickerSingle(
                    id="calendar-date-picker",
                    min_date_allowed=subway_data.Date.min().date(),
                    max_date_allowed=subway_data.Date.max().date(),
                    initial_visible_month=subway_data.Date.min().date(),
                    date=date(2020, 3, 3),
                    className = "calendar"
                ),
            ],
            className="card2",
        ),
        #upload,
        event_graphs
    ]
)
change_points_page = html.Div(
    children=[
        navbar,
        cpd_title,
        html.Div(
            children=[ html.Div("How to use this tool", className="subheading"),
                       html.Div("This tool was made to help our users visualize how change point detection works. We want oue users to understand where change points are detected.", className="descr2"),
                       html.Div("You may change the number of change being detected with the drop down menu to get a better understanding of how many when change points were detected.", className="descr2")


            ],
            className="card",
        ),

        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Number of change points for COVID-19", className="subheading2"),
                        dcc.Dropdown(
                            id="change-point-filter",
                            options=[
                                {"label": number, "value": number}
                                for number in range(1, 160)
                            ],
                            value=1,
                            clearable=False,
                            className="dropdown",
                        ),

                        html.Div(
                            children=[
                                html.Div(
                                    dbc.Spinner(children=[html.Div(children="COVID-19 Cases in NYC", className="subheading2"),dcc.Graph(
                                        id="covid-chart",
                                        config={"displayModeBar": False},
                                    ), ], color="dark", fullscreen=False),

                                    className="graph-card",
                                ),
                            ],
                        ),
                    ]
                ),
            ],
            className="card2",
        ),


        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Number of Change Points for Subway Usage", className="subheading2"),
                        dcc.Dropdown(
                            id="subway-change-point-filter",
                            options=[
                                {"label": number, "value": number}
                                for number in range(1, 160)
                            ],
                            value=1,
                            clearable=False,
                            className="dropdown",
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    dbc.Spinner(children=[html.Div(children="Subway Entries in NYC", className="subheading2"),dcc.Graph(
                                        id="subway-chart",
                                        config={"displayModeBar": False},
                                    )], color="dark", fullscreen=False),

                                    className="graph-card",
                                ),
                            ],
                        ),
                    ]
                ),
            ],
            className="card2",
        ),



    ]
)
real_time_data = html.Div(
    children=[
        navbar,
        real_time_title,
        html.Div(
            children=[
                html.Div(
                    children="Add an Event",
                    className="subheading"
                ),
                dcc.DatePickerSingle(
                    id="calendar-date-picker-rt",
                    min_date_allowed=subway_data.Date.min().date(),
                    max_date_allowed=subway_data.Date.max().date(),
                    initial_visible_month=subway_data.Date.min().date(),
                    date=date(2020, 3, 3),
                    className="calendar"
                ),
            ],
            className="card",
        ),
        rt_graphs
    ]
)


teams = html.Div(children=[
    navbar,
    team_title,
    html.Div(className="container2",
             children=[html.Div(className="team-card",
             children=[
                 html.Div("Amit Hiremath", className="subheading"),
                 html.P("Research Assistant at NYIT",className="content"),
                 html.Img(src="https://media-exp1.licdn.com/dms/image/C5603AQGuQkOG3uCLZg/profile-displayphoto-shrink_200_200/0/1625175763328?e=1638403200&v=beta&t=Sf7srb1MB1fJb-TsVnxYzIsFZPgCqa6EHV5DSBLfXCY", alt= "avatar", className="circle-img"),
                 html.Div(className="container2",
                          children=[
                              dcc.Link(
                              html.Button(className="social-btn hvr-radial-in",
                                  children=html.I(className="fab fa-linkedin-in"),
                              ),href="https://www.linkedin.com/in/the-amit-hiremath/", target="_blank"),
                              dcc.Link(
                                  html.Button(className="social-btn hvr-radial-in",
                                              children=[html.I(className="far fa-envelope", )]
                                              ),
                                  href="mailto:avmh200611@gmail.com",
                                  target="_blank"
                              ),
                              dcc.Link(
                                  html.Button(className="social-btn hvr-radial-in",
                                              children=[html.I(className="fas fa-globe-americas"), ]
                                              ),
                                  href="https://amits-portfolio-site.herokuapp.com/introduction",
                                  target="_blank"
                              ),

                          ])
             ]),
    html.Div(className="team-card",
             children=[
                 html.Div("Ziqian Dong", className="subheading"),
                 html.P("Professor at NYIT", className="content"),
                 html.Img(src="https://www.nyit.edu/files/profiles/headshot/Ziqian.Dong.jpg", alt= "avatar", className="circle-img"),
                 html.Div(className="container2",
                          children=[
                              dcc.Link(
                                  html.Button(className="social-btn hvr-radial-in",
                                              children=html.I(className="fab fa-linkedin-in"),
                                              ),
                                href="https://www.linkedin.com/in/ziqian-cecilia-dong-abb4532/",
                                target="_blank"
                              ),
                              dcc.Link(
                                  html.Button(className="social-btn hvr-radial-in",
                                              children=[html.I(className="far fa-envelope", **{'aria-hidden': 'true'},
                                                               children=None), ]
                                              ),
                                  href="mailto:ziqian.dong@nyit.edu",
                                  target="_blank"
                              ),

                              dcc.Link(
                                  html.Button(className="social-btn hvr-radial-in",
                                              children=[
                                                  html.I(className="fas fa-globe-americas", **{'aria-hidden': 'true'},
                                                         children=None), ]
                                              ),
                                  href="https://www.nyit.edu/bio/Ziqian.Dong",
                                  target="_blank"
                              ),

                          ])
             ]),
    html.Div(className="team-card",
             children=[
                 html.Div("Roberto Cessa-Rojas", className="subheading"),
                 html.P("Professor at NJIT", className="content"),
                 html.Img(src="https://web.njit.edu/~rojasces/roberto_pic.jpg", alt= "avatar", className="circle-img"),
                 html.Div(className="container2",
                          children=[
                              dcc.Link(
                                  html.Button(className="social-btn hvr-radial-in",
                                              children=html.I(className="fab fa-linkedin-in text-red"),
                                              ),
                                  href="https://www.linkedin.com/in/roberto-rojas-cessa-90168910/",
                                  target="_blank"
                              ),

                              dcc.Link(
                                  html.Button(className="social-btn hvr-radial-in",
                                              children=[html.I(className="far fa-envelope"), ]
                                              ),
                                  href="mailto:roberto.rojas-cessa@njit.edu",
                                  target="_blank"
                              ),

                              dcc.Link(
                                  html.Button(className="social-btn hvr-radial-in",
                                              children=[html.I(className="fas fa-globe-americas"), ]
                                              ),
                                  href="https://web.njit.edu/~rojasces/",
                                  target="_blank"
                              ),

                          ])
             ]),

    ]),
    ]
)



# events-page callbacks
@app.callback(
    [Output("events-covid-chart", "figure"), Output("events-subway-chart", "figure"),
     Output("covid-event-table", "columns"), Output("covid-event-table", "data"),
     Output("subway-event-table", "columns"), Output("subway-event-table", "data"),
    Output("covid-event-14table", "columns"), Output("covid-event-14table", "data"),
    Output("subway-event-14table", "columns"), Output("subway-event-14table", "data")],
    [
        Input("calculate-btn", "n_clicks"),
        Input("clear-btn", "n_clicks"),
        Input('calendar-date-picker', "date")
    ],
)
def on_click_calc(n_clicks, clear, date_val):
    ctx = dash.callback_context

    if not ctx.triggered:
        what_was_clicked = "nothing"
    else:
        what_was_clicked = ctx.triggered[0]['prop_id'].split('.')[0]

    no_cps = len(event_data["Date"].unique())

    ma_cases = covid_data["MA Cases"].values
    c_algo = rpt.Dynp(model="l2", jump=1).fit(ma_cases)
    ccps = c_algo.predict(160)
    covid_cps = covid_data.loc[covid_data.index.isin(ccps)]
    #covid_cps["Date"] = covid_cps['Date'].dt.strftime('%Y-%m-%d')
    covid_cps = covid_cps.groupby("Event Descriptions").nth(0).reset_index()

    ma_entries = subway_data["MA Entries"].values
    s_algo = rpt.Dynp(model="l2", jump=1).fit(ma_entries)
    scps = s_algo.predict(160)

    subway_cps = subway_data.loc[subway_data.index.isin(scps)]
    #subway_cps["Date"] = subway_cps['Date'].dt.strftime('%Y-%m-%d')
    subway_cps = subway_cps.groupby("Event Descriptions").nth(0).reset_index()


    if what_was_clicked == "calendar-date-picker":
        cov_graph = ev_covid_fig
        date_val = datetime.datetime.strptime(date_val, "%Y-%m-%d")
        x_dates = [date_val] #, date_val + datetime.timedelta(days=30)] #, date_val+ datetime.timedelta(days=2), date_val + datetime.timedelta(days=3)]
        impact = covid_cps.loc[covid_cps["Date"] <= date_val]
        impact = impact.sort_values(by= "Date")
        #print(impact[["Date", "7 day Difference", "MA Cases"]])
        impact = impact.tail(1)
        y_vals = impact["Abs 7 day Difference"]
        #width = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.4]
        cov_graph.add_trace(go.Bar(x=x_dates,y=y_vals, width= 1000 * 3600 * 24 *2, name="Added Event Impact"))

        sub_graph = ev_subway_fig
        sub_impact = subway_cps.loc[subway_cps["Date"] <= date_val]
        sub_impact = sub_impact.sort_values(by= "Date")
        sub_impact = sub_impact.tail(1)
        sub_y = sub_impact["Abs 7 day Difference"]
        sub_graph.add_trace(go.Bar(x= x_dates, y= sub_y, width= 1000*3600 *24 *2, name="Added Event Impact"))

        return cov_graph,sub_graph, [], [], [], [], [], [], [], []

    elif what_was_clicked == "calculate-btn" and (n_clicks >0):

        covid_cps7 = covid_cps.sort_values(by=["Abs 7 day Difference"], ascending=False).head(10)
        covid_cps14 = covid_cps.sort_values(by=["Abs 14 day Difference"], ascending=False).head(10)

        events_covid_chart_figure = ev_covid_fig

        events_covid_chart_figure.add_bar(x=covid_cps7["Date"].head(10),
                                          y=covid_cps7["Abs 7 day Difference"].head(10),
                                          name="Top 10 Event Impacts")

        subway_cps7 = subway_cps.sort_values(by=["Abs 7 day Difference"], ascending=False).head(10)
        subway_cps14 = subway_cps.sort_values(by=["Abs 14 day Difference"], ascending=False).head(10)

        events_subway_chart_figure = ev_subway_fig

        events_subway_chart_figure.add_bar(x= subway_cps7["Date"].head(10), y= subway_cps7["Abs 7 day Difference"].head(10),name="Event Impact")

        cols = ["Date", "Abs 7 day Difference", "Event Descriptions"]
        cols = [{"name": i, "id": i} for i in cols]

        cols14 = ["Date", "Abs 14 day Difference", "Event Descriptions"]
        cols14 = [{"name": i, "id": i} for i in cols14]

        sub_cols =["Date", "Abs 7 day Difference", "Event Descriptions"]
        sub_cols = [{"name": j, "id": j} for j in sub_cols]

        sub_cols14 = ["Date", "Abs 14 day Difference", "Event Descriptions"]
        sub_cols14 = [{"name": j, "id": j} for j in sub_cols14]

        c_data = covid_cps7[["Date", "Abs 7 day Difference", "Event Descriptions"]].to_dict('records')
        c_data14 = covid_cps14[["Date", "Abs 14 day Difference", "Event Descriptions"]].to_dict('records')

        s_data = subway_cps7[["Date", "Abs 7 day Difference", "Event Descriptions"]].to_dict('records')
        s_data14 = subway_cps14[["Date", "Abs 14 day Difference", "Event Descriptions"]].to_dict('records')

        covid_cps7[["Date", "Abs 7 day Difference", "Event Descriptions"]].to_csv('covidhead.csv')
        covid_cps14[["Date", "Abs 14 day Difference", "Event Descriptions"]].to_csv('covid14head.csv')
        subway_cps7[["Date", "Abs 7 day Difference", "Event Descriptions"]].to_csv('subwayhead.csv')
        subway_cps14[["Date", "Abs 14 day Difference", "Event Descriptions"]].to_csv('subway14head.csv')


        return events_covid_chart_figure, events_subway_chart_figure, cols, c_data, sub_cols, s_data, cols14, c_data14, sub_cols14, s_data14
    elif what_was_clicked == "clear-btn" and (clear > 0):
        clear_covid_fig = ev_covid_fig
        clear_subway_fig = ev_subway_fig
        clear_covid_fig.data = ev_covid_fig.data[0:2]
        clear_subway_fig.data = ev_subway_fig.data[0:2]

        return clear_covid_fig, clear_subway_fig, [], [], [], [], [], [], [], []
    else:
        raise dash.exceptions.PreventUpdate
    print(what_was_clicked)
    print(date_val)


# change-points-page callbacks
@app.callback(
    Output("covid-chart", "figure"),
    [
        Input("change-point-filter", "value")
    ],
)
def update_covid(no_cp):
    ma_cases = covid_data["MA Cases"].values
    algo = rpt.Dynp(model="l2", jump= 1).fit(ma_cases)
    cps = algo.predict(no_cp)
    dates = covid_data["Date"].loc[covid_data.index.isin(cps)]
    covid_chart_figure = px.line(
        covid_data, x="Date", y= ["MA Cases", "7 days Ahead Forecasted Values"],
    )
    for date in dates:
        covid_chart_figure.add_vline(x = date, line_width = 1, line_color = "green")
    covid_chart_figure.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)',})
    return covid_chart_figure

@app.callback(
    Output("subway-chart", "figure"),
    [
        Input("subway-change-point-filter", "value")
    ],
)
def update_subway(no_cp):
    ma_entries = subway_data["MA Entries"].values
    algo = rpt.Dynp(model="l2", jump= 1).fit(ma_entries)
    cps = algo.predict(no_cp)
    dates = subway_data["Date"].loc[subway_data.index.isin(cps)]
    subway_chart_figure = px.line(
        subway_data, x="Date", y = ["MA Entries", "7 days Ahead Forecasted Values"],
    )
    for date in dates:
        subway_chart_figure.add_vline(x = date, line_width = 1, line_color = "green")
    subway_chart_figure.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)',})
    return subway_chart_figure

@app.callback(Output('page-content', 'children'),
              [Input('url','pathname')])
def display_page(pathname):
    if pathname == "/events":
        return events_page
    elif pathname == "/changepoints":
        return change_points_page
    elif pathname == "/daily-data":
        return real_time_data
    elif pathname =="/team":
        return teams
    else:
        return index_page

if __name__ == '__main__':
    app.run_server(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
