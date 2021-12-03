from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

def tab_settings():
    tab_settings_block = dcc.Tab(
        label='Настройки',
        value='tab_settings',
        className='custom-tab',
        selected_className='custom-tab--selected',
        children=[dbc.Row([
            dbc.Col(
                #width=3,
                children=[

                    # html.P('Фильтр по регионам'),
                    # dcc.RadioItems(
                    #     id = 'region_view_selector',
                    #     options=[
                    #         {'label': ' Мультиселект', 'value': 'region_multiselect'},
                    #         {'label': ' Список чек-боксов', 'value': 'region_checklist'},
                    #     ],
                    #     value='region_multiselect',
                    #     labelStyle=dict(display='block'),
                    #
                    # ),
                ]


                    )
        ]

        )]

    )
    return tab_settings_block