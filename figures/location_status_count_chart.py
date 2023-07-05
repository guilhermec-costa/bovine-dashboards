import plotly.express as px
from . import update_fig_elements
import streamlit as st


def valid_status_count(data):
    fig = px.bar(data, x='Date', y='PLM', color='Valid location', facet_col='Valid location', barmode='stack', text_auto=True,
                 color_continuous_scale=px.colors.qualitative.Alphabet)
    fig.update_layout(height=520, title=dict(text=f'Valid location', xanchor='center',yanchor='top', 
                                    x=0.5, y=1, font=dict(size=25, family='roboto')
                                    ), showlegend=False, uniformtext_minsize=18,
                legend=dict(orientation='v'), template='plotly', font_family='roboto')

    fig.update_traces(textfont_size=16, textposition='outside')
    fig.update_yaxes(showticklabels=False, title=None)
    fig.update_xaxes(tickfont=dict(size=16, family='roboto'), showline=True, linewidth=1, title=dict(text=None), tickangle=30)
    fig.update_coloraxes(showscale=False)
    update_fig_elements.alter_legend(fig=fig, title='Valid location')
    update_fig_elements.alter_hover(fig=fig)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1].strip('.0') + ' Valid locations'))
    fig.update_annotations(font=dict(family='roboto', size=16))
    return fig

def invalid_status_count(data):
    fig = px.bar(data, x='Date', y='PLM', color='Invalid location', facet_col='Invalid location', barmode='stack', text_auto=True,
                 color_continuous_scale=px.colors.qualitative.Alphabet)
    fig.update_layout(height=520, title=dict(text=f'Invalid location', xanchor='center',yanchor='top', 
                                x=0.5, y=1, font=dict(size=25, family='roboto')
                                ), uniformtext_minsize=18,
            legend=dict(orientation='v'), template='plotly', font_family='roboto')

    fig.update_traces(textfont_size=16, textposition='outside')
    fig.update_xaxes(tickfont=dict(size=16, family='roboto'), showline=True, linewidth=1, title=dict(text=None))
    fig.update_yaxes(showticklabels=False, title=None)
    fig.update_coloraxes(showscale=False)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1].strip('.0') + ' Invalid locations'))
    fig.update_annotations(font=dict(family='roboto', size=16))
    update_fig_elements.alter_hover(fig=fig)
    return fig