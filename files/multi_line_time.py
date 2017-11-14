#coding:utf-8
#================mongodb数据库接口================================
from  pymongo import MongoClient 

#===========================布局及输入框============================
from bokeh.layouts import layout, widgetbox
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.plotting import show, figure
#===========================导入工具=========================================
from bokeh.models import ColumnDataSource, HoverTool, TapTool,BoxZoomTool,WheelZoomTool,UndoTool,ResetTool,CrosshairTool
#================================服务相关==============================
from bokeh.client import push_session
from bokeh.io import curdoc
#-----------------------------------------------------------------------
dbclient = MongoClient()
dbconnect = dbclient['HFSSDataBase']
collconnect = dbconnect['Square_circular']


#=====================初始化x,y====================================
xs = collconnect.find_one()['f']
ys = []
num = collconnect.find().count()
numline = Slider(title="Minimum number of lines", value=0, start=0, end=num, step=1)
tools = [HoverTool(tooltips=[("vars", "@vars")]), TapTool(),BoxZoomTool(),WheelZoomTool(),UndoTool(),ResetTool(),CrosshairTool()]
source = ColumnDataSource(data=dict(x=[], y=[],vars=[]))
p = figure(plot_height=300, plot_width=700, title="", tools=tools)
p.multi_line("x", "y",source=source,hover_color="red",line_width=1)
p.xaxis.axis_label = 'Frequency(GHz)'
p.yaxis.axis_label = 'S11(dB)'
def sliderchanges():
    if numline.value < num:
       numline.value +=1
def update():
    update_num = int(numline.value)
    x_list = [xs for x in range(update_num)]
    y_list = [x['value'] for x in collconnect.find()[:update_num]]
    vars_list = [str(x['vars']) for x in collconnect.find()[:update_num]]
    p.title.text = "%d lines selected" % update_num
    source.data = dict(
        x=x_list,
        y=y_list,
        vars = vars_list
    )
l = layout([numline],[p])

numline.on_change('value', lambda attr, old, new: update())
update()  
document = curdoc()
document.add_root(l)
document.add_periodic_callback(sliderchanges,100)#1000 = 1second
document.title = "lines of databases"
if __name__ == "__main__":
    print("\npress ctrl-C to exit")
    session = push_session(document)
    session.show()
    session.loop_until_closed()