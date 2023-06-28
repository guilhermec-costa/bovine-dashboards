import plotly.express as px

def alter_legend(fig, title):
    fig.update_layout(legend=dict(font=dict(size=13, color="black", family='roboto'), bgcolor="#D5D5D1",
                                  bordercolor="black", borderwidth=2, title=dict(text=f'{title}', font=dict(size=16, color='black', family='roboto')), font_family='roboto'))
    
def alter_hover(fig, mode="closest"):
    fig.update_layout(hovermode=mode, hoverlabel=dict(bgcolor="AntiqueWhite", font_color="black",
                                                    font_size=14, bordercolor="blue", font_family='roboto'))