#coding:utf-8
#================mongodb数据库接口================================
from  pymongo import MongoClient 
from collections import defaultdict
#===========================布局及输入框============================
from bokeh.layouts import widgetbox,row,layout,column
from bokeh.models.widgets import Slider, Select, TextInput,Button
from bokeh.plotting import show, figure
#===========================导入工具=========================================
from bokeh.models import ColumnDataSource, HoverTool,Range1d, TapTool,BoxZoomTool,WheelZoomTool,UndoTool,ResetTool,CrosshairTool
#================================服务相关==============================
from bokeh.client import push_session
from bokeh.io import curdoc
#-----------------------------------------------------------------------
dbclient = MongoClient()
dbconnect = dbclient['test']
collconnect = dbconnect['flasktest']


#=====================初始化x,y====================================
xs = collconnect.find_one()['f']
end = len(xs)
ys = []
num = collconnect.find().count()
numline = Slider(title="Minimum number of lines", value=0, start=0, end=num, step=1)
tools = [HoverTool(tooltips=[("vars", "@vars")]), TapTool(),BoxZoomTool(),WheelZoomTool(),UndoTool(),ResetTool(),CrosshairTool()]
source = ColumnDataSource(data=dict(x=[], y=[],vars=[],fre_point=[],fre_count=[]))
#===========================绘制多曲线=============================
p = figure(plot_height=300, plot_width=700, title="",tools=tools)
p.multi_line("x", "y",hover_color="red",line_width=1,source=source)
p.xaxis.axis_label = 'Frequency(GHz)'
p.yaxis.axis_label = 'S11(dB)'
#===============================绘制频点与数量关系的rect============
q = figure(plot_height=300, plot_width=700, title="",tools=tools)
q.rect('fre_point', 'fre_count',0.05,0.05,hover_color="red", source=source)
#q.circle('fre_point', 'fre_count',size=1,hover_color="red", source=source)
q.xaxis.axis_label = u"频点(GHZ)"
q.yaxis.axis_label = u"个数(个)"

#=============================获取每一条曲线的频点与相同频点的个数==========
def get_frepoint_count(multi_s_list):
    dd = defaultdict(list)
    source_fre_point = []
    source_fre_count = []
    for s_list in multi_s_list:
        Ref_temp=[s_list[i+1]-s_list[i] for i in range(end-1)]
        fre_index_list = list()
        [fre_index_list.append(i) for i in range(0,end-2) if (Ref_temp[i]<0) and (Ref_temp[i+1]>0) and s_list[i+1]<-2]
        if fre_index_list:
            fre_point_list = [xs[i] for i in fre_index_list] 
            for i in fre_point_list:
                dd[i].append('0')
    for j in dd.items():
        source_fre_point.append(j[0])
        source_fre_count.append(len(j[1]))
    return source_fre_point,source_fre_count
#================================开始，暂停按钮===========================
def start_handler():
    global playing
    if not playing:
        curdoc().add_periodic_callback(sliderchanges,3000)
        playing = True

def stop_handler():
    global playing
    if playing:
        curdoc().remove_periodic_callback(sliderchanges)
        playing = False

button_start = Button(label=u"继续更新",button_type="primary")
button_start.on_click(start_handler)

button_stop = Button(label=u"暂停更新", button_type="danger")
button_stop.on_click(stop_handler)

controls = row(button_start, button_stop)
#========================TextInput=======================
x_min = TextInput(title="X_min", value='%.1f'%min(xs))
x_max = TextInput(title="X_max", value='%.1f'%max(xs))
y_min = TextInput(title="X_min", value= '%.1f'%-30.0)
y_max = TextInput(title="X_max", value='%.1f'%1.0)
axis_controls = [x_min,x_max,y_min,y_max]
xy_inputs = widgetbox(x_min,x_max,y_min,y_max)
#========================================================
def sliderchanges():
    if playing:
        if numline.value < num:
           numline.value +=1
def update():
    update_num = int(numline.value)
    x_list = [xs for x in range(update_num)]
    y_list = [x['value'] for x in collconnect.find()[:update_num]]
    vars_list = [str(x['vars']) for x in collconnect.find()[:update_num]]
    p.title.text = "%d lines selected" % update_num
    p.xaxis.axis_label = 'Frequency(GHz)'
    p.yaxis.axis_label = 'S11(dB)'
    #================================================
    #print(float(x_min.value),type(float(x_min.value)))
    xminval = float(x_min.value)
    xmaxval = float(x_max.value)
    
    yminval = float(y_min.value)
    ymaxval = float(y_max.value)
    p.x_range = Range1d(start=xminval, end=xmaxval)
    #p.x_range = Range1d(start=2.0, end=3.0)
    p.y_range = Range1d(start=yminval, end=ymaxval)
    source.data = dict(
        x=x_list,
        y=y_list,
        vars = vars_list,
    )
def update_frepoint():
    update_num = int(numline.value)
    y_list = [x['value'] for x in collconnect.find()[:update_num]]
    source_from_frepoint = get_frepoint_count(y_list)
    source_fre_point = source_from_frepoint[0]
    source_fre_count = source_from_frepoint[1]
    source.data = dict(
        fre_point=source_fre_point,
        fre_count=source_fre_count,
    )
#=========================更新坐标轴信息=================
def update_axis():
    xminval = float(x_min.value)
    xmaxval = float(x_max.value)
    
    yminval = float(y_min.value)
    ymaxval = float(y_max.value)
    p.x_range = Range1d(start=xminval, end=xmaxval)
    #p.x_range = Range1d(start=2.0, end=3.0)
    p.y_range = Range1d(start=yminval, end=ymaxval)
#plot_lay = column(p,q)
line_plot_lay = layout(numline,q,controls)

#numline.on_change('value', lambda attr, old, new: update())
numline.on_change('value', lambda attr, old, new: update_frepoint())
for control in axis_controls:
    control.on_change('value', lambda attr, old, new: update_axis())

#update()  
update_frepoint()
playing = True
document = curdoc()
document.add_root(row(xy_inputs,line_plot_lay))
document.add_periodic_callback(sliderchanges,1000)

document.title = "lines of databases"
if __name__ == "__main__":
    print("\npress ctrl-C to exit")
    session = push_session(document)
    session.show()
    session.loop_until_closed()