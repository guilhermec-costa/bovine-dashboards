import plotly.express as px
from . import update_fig_elements

def mapbox_last_location(data, theme: str, ident):
    fig = px.scatter_mapbox(data_frame=data, lat='Latitude', lon='Longitude', hover_name='PLM', zoom=3, height=800, size_max=20, size='battery', color='battery',
                            color_continuous_scale=px.colors.sequential.RdBu, center=(dict(lat=-20.65785026550293, lon=-51.5435791015625)),
                            hover_data=['battery', 'Name', 'Deveui', 'race_name', 'Date'])
    fig.update_layout(mapbox_style=theme, title=dict(
    text="Last bovine location", x=0.5, y=0.98,
    xanchor="center", yanchor="top", font=dict(size=27, color="white", family='roboto')),
    template='plotly', font_family='roboto', mapbox=dict(accesstoken='pk.eyJ1IjoiY2hpbmluaGEiLCJhIjoiY2xncGdxYzByMHphNzN0bHVzN20xbjlkYyJ9.N1T4HtNFTI-kf-XQAEJNOg'),
    margin=dict(r=2, l=2, t=2, b=2),
    coloraxis_colorbar=dict(title='Battery voltage', ticksuffix='V', thickness=35, ticks='outside', y=0.9, yanchor='top',))

    update_fig_elements.alter_legend(fig=fig, title='PLM')
    update_fig_elements.alter_hover(fig=fig)
    
    return fig
