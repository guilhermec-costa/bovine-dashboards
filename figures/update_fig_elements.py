import plotly.express as px

def alter_legend(fig):
    fig.update_layout(legend=dict(font=dict(size=13, color="white"), bgcolor="#051732",
                                  bordercolor="black", borderwidth=2, title=dict(text=f'{" " * 15}Número da PLM', font=dict(size=16))))
    
def alter_hover(fig, mode="closest"):
    fig.update_layout(hovermode=mode, hoverlabel=dict(bgcolor="AntiqueWhite", font_color="black",
                                                    font_size=14, bordercolor="blue"))