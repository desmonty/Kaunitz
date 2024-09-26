import pandas as pd
import plotly.express as px

from dash import dcc


def create_bar_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    color: str,
    title: str,
    x_axe_title: str,
    y_axe_title: str
):
    fig = px.bar(data, x=x, y=y, color=color, title=title)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title=x_axe_title)
    fig.update_yaxes(title=y_axe_title)
    fig.update_layout(margin=dict(t=40, b=40, r=40, l=40))
    return dcc.Graph(figure=fig, id='bar-chart')
