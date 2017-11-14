import bokeh
from bokeh.models import ColumnDataSource, HoverTool, TapTool,BoxZoomTool,WheelZoomTool,UndoTool,ResetTool,CrosshairTool
from  pymongo import MongoClient 
from bokeh.client import push_session
from bokeh.plotting import show, figure,curdoc
from bokeh.layouts import gridplot
from bokeh.palettes import inferno
from bokeh.layouts import row, column
dbclient = MongoClient()
dbconnect = dbclient['HFSSDataBase']
collconnect = dbconnect['Square_circular']
figure_opts = dict(plot_width=1200, plot_height=600)
hover_opts = dict(
    tooltips=[('MZ', '@MZ_tip'), ('Rel Intensity', '@Intensity_tip')],
    show_arrow=True,
    line_policy='prev'
)
xs = collconnect.find_one()['f']
ys = []
for j in collconnect.find():
    ys.append(j['value'])
tools = [HoverTool(**hover_opts), TapTool(),BoxZoomTool(),WheelZoomTool(),UndoTool(),ResetTool(),CrosshairTool()]
rt_plot = figure(tools=tools,**figure_opts)
def update():
    #rt_plot.multi_line([xs for j in range(len(ys))],ys,line_width=2)
    rt_plot.multi_line(xs,ys[0],line_width=2)
layout = column(rt_plot)
update()
document = curdoc()
document.add_root(layout)
document.add_periodic_callback(update,50)

if __name__ == "__main__":
    print("\nanimating... press ctrl-C to stop")
    session = push_session(document)
    session.show()
    session.loop_until_closed()