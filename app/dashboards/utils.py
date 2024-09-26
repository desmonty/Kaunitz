from dash import html, dcc
import dash_bootstrap_components as dbc


def draw_figure(
    plotly_figure,
    template: str = 'plotly_dark'
):
    return  html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=plotly_figure.update_layout(
                        template=template,
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)',
                    ),
                    config={
                        'displayModeBar': False
                    }
                ) 
            ])
        ),  
    ])

def draw_text(text: str, level: int, additional_style: dict = {}):
    level_to_heading = {
        1: html.H1,
        2: html.H2,
        3: html.H3,
    }
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    level_to_heading[level](text),
                ], style={'textAlign': 'center', **additional_style}) 
            ])
        ),
    ])
