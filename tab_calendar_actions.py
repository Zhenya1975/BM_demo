import datetime

from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import initial_values

regions = initial_values.region_checklist_data()[0]
regions_list = initial_values.region_checklist_data()[1]
managers = initial_values.managers_checklist_data()

def calendar_actions():
    calendar_actions_tab_block = dcc.Tab(
        label='Отчет по встречам',
        value='tab_calendar_actions',
        className='custom-tab',
        selected_className='custom-tab--selected',
        children=[
            dbc.Row([
                dbc.Col(width=3,
                        children=[
                            html.Div(style={'paddingLeft': '30px', 'paddingRight': '20px',
                                            'marginTop': '10px', 'color': 'white'},
                                     children=[

                                         # html.B('Регионы'),
                                         #html.Div(id = 'region_selector'),

                                         html.Div(style={'marginLeft': '3px'},
                                                  children=[

                                                      html.P(),
                                                      html.Div(id='result_div_checklist',
                                                               children=[
                                                                   html.P(),
                                                                   dbc.Button("Выбрать все", size="sm",
                                                                              id="select_all_regions_button_tab_calendar_actions",
                                                                              style={'marginBottom': '3px',
                                                                                     'marginTop': '3px',
                                                                                     'backgroundColor': '#232632'}),
                                                                   dbc.Button("Снять выбор", color="secondary",
                                                                              size="sm",
                                                                              style={'marginBottom': '3px',
                                                                                     'marginTop': '3px',
                                                                                     'backgroundColor': '#232632'},
                                                                              id="release_all_regions_button_tab_calendar_actions"),
                                                                   html.P(),
                                                                   dcc.Checklist(
                                                                       id='region_selector_checklist_calendar_actions_tab',
                                                                       #options=regions,
                                                                       #value=regions_list,
                                                                       labelStyle=dict(display='block')),
                                                                   html.Hr(className="hr"),


                                                               ],
                                                               ),
                                                      html.Div(
                                                          id='managers_check-list_div',
                                                          children=[
                                                              # блок чек-боксов с Менеджерами
                                                              html.P(),
                                                              dbc.Button("Выбрать все", size="sm",
                                                                         id="select_all_managers_button_tab_calendar_actions",
                                                                         style={'marginBottom': '3px',
                                                                                'marginTop': '3px',
                                                                                'backgroundColor': '#232632'}),
                                                              dbc.Button("Снять выбор", color="secondary",
                                                                         size="sm",
                                                                         style={'marginBottom': '3px',
                                                                                'marginTop': '3px',
                                                                                'backgroundColor': '#232632'},
                                                                         id="release_all_managers_button_tab_calendar_actions"),
                                                              html.P(),
                                                              dcc.Checklist(
                                                                  id='managers_selector_checklist_calendar_actions_tab',
                                                                  #options=regions,
                                                                  #value=regions_list,
                                                                  labelStyle=dict(display='block')
                                                              ),
                                                          ]
                                                      )
                                                  ]
                                                  ),


                                     ])

                        ]
                        ),
                dbc.Col(width=9,
                        children=[
                            html.P(),
                            html.Div(style={'paddingLeft': '30px', 'paddingRight': '20px',
                                            #'paddingTop': '10px',
                                            'color': 'white'},
                                     children=[

                                         dbc.Row([
                                             #dbc.Col(dbc.Card(card_tab_deals_qty_in_deals, color="dark", inverse=True)),
                                             #dbc.Col(dbc.Card(card_tab_deals_won_deals, color="dark", inverse=True)),
                                             #dbc.Col(dbc.Card(card_tab_deals_lost_deals, color="dark", inverse=True)),
                                         ],
                                         ),

                                         html.Div([
                                             dcc.DatePickerRange(
                                                 id='my-date-picker-range',
                                                 first_day_of_week =1,
                                                 #min_date_allowed=date(1995, 8, 5),
                                                 #max_date_allowed=datetime.datetime.now().date(),
                                                 initial_visible_month=datetime.datetime.now().date(),
                                                 #start_date = datetime.datetime.now().date(),
                                                 start_date = datetime.datetime.strptime("01.11.2021", "%d.%m.%Y").date(),
                                                 #end_date=datetime.datetime.now().date(),
                                                 end_date=datetime.datetime.strptime("31.12.2021", "%d.%m.%Y").date(),
                                                 display_format = 'D.M.YYYY',

                                             ),


                                         ]),
                                         html.Div(style={'paddingTop': '10px',},
                                                  children=[html.H4('РEГИОНЫ'),]),


                                         dbc.Row([
                                             dbc.Col(width=4,
                                                     children=[
                                                         #dcc.Graph(id='meetings_day_distribution_graph', config={'displayModeBar': False}),
                                                         dcc.Graph(id='closed_meetings_day_distribution_graph',
                                                                   config={'displayModeBar': False}),
                                                         html.P(),

                                                     ]
                                                     ),
                                             dbc.Col(width=4,
                                                     children=[

                                                         dcc.Graph(id='open_meetings_day_distribution_graph',
                                                                   config={'displayModeBar': False}),
                                                         html.P(),

                                                         html.P(),
                                                     ]
                                                     ),
                                             dbc.Col(width=4,
                                                     children=[

                                                         dcc.Graph(id='overdue_meetings_day_distribution_graph',
                                                                   config={'displayModeBar': False}),
                                                         html.P(),

                                                         html.P(),
                                                     ]
                                                     ),
                                         ]),
                                         dbc.Row([
                                             dbc.Col(
                                                 dcc.Checklist(
                                                     id='include_zeros_regions',
                                                     options=[{'label': " Показать регионы с нулями",
                                                               'value': "regions_zeros"}],
                                                     # value='regions_zeros',
                                                     # labelStyle=dict(display='block')
                                                 ),
                                             ),
                                         ]),
                                         # Графики по пользователям
                                         html.Div(style={'paddingTop': '10px', },
                                                  children=[html.H4('МЕНЕДЖЕРЫ'), ]),
                                         dbc.Row([
                                             dbc.Col(width=4,
                                                     children=[
                                                         # dcc.Graph(id='meetings_day_distribution_graph', config={'displayModeBar': False}),
                                                         dcc.Graph(id='closed_meetings_user_distribution_graph',
                                                                   config={'displayModeBar': False}),
                                                         html.P(),

                                                     ]
                                                     ),
                                             dbc.Col(width=4,
                                                     children=[

                                                         dcc.Graph(id='open_meetings_user_distribution_graph',
                                                                   config={'displayModeBar': False}),
                                                         html.P(),

                                                         html.P(),
                                                     ]
                                                     ),
                                             dbc.Col(width=4,
                                                     children=[

                                                         dcc.Graph(id='overdue_meetings_user_distribution_graph',
                                                                   config={'displayModeBar': False}),
                                                         html.P(),

                                                         html.P(),
                                                     ]
                                                     ),
                                         ]),
                                         # dbc.Card(
                                         #     [
                                         #         dbc.CardHeader("Встреча ООО Конный завод Чесменский",
                                         #                        className='card-header'),
                                         #         dbc.CardBody([
                                         #             html.P("текст card-title",
                                         #                 className="card-title",
                                         #                    ),
                                         #             html.P("Встреча с клиентом. Сообщил, что 13 ноября собственник будет смотреть кормосмеситель, после чего будет принимать решение.",
                                         #                 className="card-text", id='card_plan_fact_tab_plan_value'),
                                         #         ]
                                         #         ), ],
                                         #
                                         #     #color="dark", inverse=True
                                         # className='card'),
                                         html.Hr(className="hr"),
                                         dbc.Row([
                                             html.Div(
                                                 children=[
                                                     html.P("Встречи"),
                                                     html.Div(id='meetings-data-table')
                                                 ]
                                             ),
                                         ]),
                                     ])
                            ]),
            ])

        ]

    )
    return calendar_actions_tab_block

