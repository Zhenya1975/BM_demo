from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

def tab_plan_fact():
    tab_plan_fact = dcc.Tab(
        label='Встречи. План-факт',
        value='tab_plan_fact',
        className='custom-tab',
        selected_className='custom-tab--selected',
        children=[dbc.Row([
            dbc.Col(width=3,
                    children=[
                        html.Div(style={'paddingLeft': '30px', 'paddingRight': '20px',
                                        'marginTop': '10px', 'color': 'white'},
                                 children=[

                                     html.Div(style={'marginLeft': '3px'},
                                              children=[

                                                  html.P(),
                                                  html.Div(id='plan_fact_tab_region_div_checklist',
                                                           children=[
                                                               html.P(),
                                                               dbc.Button("Выбрать все", size="sm",
                                                                          id="select_all_regions_button_tab_plan_fact",
                                                                          style={'marginBottom': '3px',
                                                                                 'marginTop': '3px',
                                                                                 'backgroundColor': '#232632'}),
                                                               dbc.Button("Снять выбор", color="secondary",
                                                                          size="sm",
                                                                          style={'marginBottom': '3px',
                                                                                 'marginTop': '3px',
                                                                                 'backgroundColor': '#232632'},
                                                                          id="release_all_regions_button_tab_plan_fact"),
                                                               html.P(),
                                                               dcc.Checklist(
                                                                   id='region_selector_checklist_tab_plan_fact',
                                                                   # options=regions,
                                                                   # value=regions_list,
                                                                   labelStyle=dict(display='block')),
                                                               html.Hr(className="hr"),

                                                           ],
                                                           ),
                                                  html.Div(
                                                      id='managers_check-list_div_tab_plan_fact',
                                                      children=[
                                                          # блок чек-боксов с Менеджерами
                                                          html.P(),
                                                          dbc.Button("Выбрать все", size="sm",
                                                                     id="select_all_managers_button_tab_plan_fact",
                                                                     style={'marginBottom': '3px',
                                                                            'marginTop': '3px',
                                                                            'backgroundColor': '#232632'}),
                                                          dbc.Button("Снять выбор", color="secondary",
                                                                     size="sm",
                                                                     style={'marginBottom': '3px',
                                                                            'marginTop': '3px',
                                                                            'backgroundColor': '#232632'},
                                                                     id="release_all_managers_button_tab_plan_fact"),
                                                          html.P(),
                                                          dcc.Checklist(
                                                              id='managers_selector_checklist_tab_plan_fact',
                                                              # options=regions,
                                                              # value=regions_list,
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
                        dcc.Graph(id='meetings_plan_fact_graph', config={'displayModeBar': False}),
                    ]),
        ]

        )]

    )
    return tab_plan_fact