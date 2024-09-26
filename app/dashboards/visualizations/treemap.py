import pandas as pd
import plotly.express as px

from dash import dcc


def create_treemap_chart(
    data: pd.DataFrame,
    path: list,
    values: str
):
    fig = px.treemap(data, path=path, values=values)
    fig.update_traces(textinfo='label+percent entry')
    fig.update_layout(margin=dict(t=40, b=40, r=40, l=40))
    return dcc.Graph(figure=fig, id='treemap-chart')
