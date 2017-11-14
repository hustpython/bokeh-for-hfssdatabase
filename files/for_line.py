import threading
import bokeh
from bokeh.models import ColumnDataSource, HoverTool, TapTool,BoxZoomTool,WheelZoomTool,UndoTool,ResetTool,CrosshairTool
from  pymongo import MongoClient 
from bokeh.client import push_session
from bokeh.plotting import show, figure,curdoc
from bokeh.layouts import gridplot
from bokeh.palettes import inferno
from bokeh.layouts import row, column
from bokeh.models import Line
dbclient = MongoClient()
dbconnect = dbclient['HFSSDataBase']
collconnect = dbconnect['Square_circular']
figure_opts = dict(plot_width=1200, plot_height=600)
hover_opts = dict(
    tooltips=[('MZ', '@MZ_tip'), ('Rel Intensity', '@Intensity_tip')],
    show_arrow=True,
    line_policy='interp'
)
xs = collconnect.find_one()['f']
ys = []
for j in collconnect.find():
    ys.append(j['value'])
tools = [HoverTool(), TapTool(),BoxZoomTool(),WheelZoomTool(),UndoTool(),ResetTool(),CrosshairTool()]
rt_plot = figure(tools=tools,**figure_opts)

for i in range(3):
    #rt_plot.multi_line([xs for j in range(len(ys))],ys,line_width=2)
    renderer = rt_plot.multi_line([xs],[ys[i]],line_width=2)
selected_circle = Line(line_alpha=1)
nonselected_circle = Line(line_alpha=0.1)
renderer.selection_glyph = selected_circle
renderer.nonselection_glyph = nonselected_circle

show(rt_plot)
