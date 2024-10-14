#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install bokeh')
from bokeh.layouts import column, row
from bokeh.palettes import Spectral5
from bokeh.plotting import curdoc
from bokeh.io import output_notebook
from bokeh.plotting import figure, show
from bokeh.io import output_notebook
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.models import ColumnDataSource, Select,HoverTool, LabelSet, Text, Legend, LegendItem


# In[2]:


import pandas as pd
import numpy as np


# In[3]:


def findcoord(LinkRow,NodeCoord):
    x_From=NodeCoord.loc[NodeCoord['Node']==LinkRow['From']]['X-Coord'].values
    y_From=NodeCoord.loc[NodeCoord['Node']==LinkRow['From']]['Y-Coord'].values
    
    x_To=NodeCoord.loc[NodeCoord['Node']==LinkRow['To']]['X-Coord'].values
    y_To=NodeCoord.loc[NodeCoord['Node']==LinkRow['To']]['Y-Coord'].values
    return x_From, y_From,x_To,y_To


# In[4]:


def manholescoord(ManholeDf,NodeCoord):
    Xcoord=[];
    Ycoord=[];
    for i in range(0,len(ManholeDf['ID'].values)):
        Xcoord.append(NodeCoord.loc[NodeCoord['Node']==ManholeDf['ID'][i]]['X-Coord'].values)
        Ycoord.append(NodeCoord.loc[NodeCoord['Node']==ManholeDf['ID'][i]]['Y-Coord'].values)
    return Xcoord,Ycoord


# In[5]:


def findlinkupstream(upstreamNode,NodeCoord):
    X=[];
    Y=[];
    for i in range(len(upstreamNode)):
        x=NodeCoord.loc[NodeCoord['Node']==upstreamNode[i]]['X-Coord'].values
        X.append(x)
        y=NodeCoord.loc[NodeCoord['Node']==upstreamNode[i]]['Y-Coord'].values
        Y.append(y)    
    if len(X):
        X=np.concatenate( X, axis=0 )
    if len(Y):
        Y=np.concatenate( Y, axis=0 )
    return X,Y


# In[6]:


excelfilepath='U:\phd_program_ninh\Data and code\paper1\System2_network.xlsx'
NodeCoord=pd.read_excel(excelfilepath,sheet_name='NodeCoordinate')
Link=pd.read_excel(excelfilepath,sheet_name='Link')
ManholesID=pd.read_excel(excelfilepath,sheet_name='ManholeLocation')
downstreamDependent=pd.read_excel(excelfilepath,sheet_name='DownstreamDependent')
a= []
for i in range(len(ManholesID['ID'].values)):
    a.append(str(ManholesID['ID'].values[i]))
    
ManholeXYcoord=manholescoord(ManholesID,NodeCoord)


# In[7]:


downstreamDependent


# In[8]:


fileName='U:\phd_program_ninh\Data and code\paper1\System2_network.xlsx'
GAresult=pd.read_excel(fileName,sheet_name='Optimal location')
GAresult.head(5)


# In[9]:


minSensor=len(GAresult.loc[GAresult['SensorLoc']!=0])


# In[10]:


minSensor


# In[11]:


sensorLoc=GAresult.loc[GAresult['SensorLoc']!=0]
sensorLoc=sensorLoc.reset_index()


# In[12]:


sensorLoc


# In[13]:


xs = NodeCoord['X-Coord'].values
ys = NodeCoord['Y-Coord'].values
  
xm=np.concatenate( ManholeXYcoord[0], axis=0 )
ym=np.concatenate( ManholeXYcoord[1], axis=0 )
source=ColumnDataSource(data= {'x':xm,'y':ym})    
   

TOOLTIPS = [('Index', '@ID')]    
p = figure(plot_height=1000, plot_width=800,tooltips=TOOLTIPS, toolbar_location="below")    
   
# Plot nodes
p.xaxis.axis_label = 'X-Coordinate'
p.yaxis.axis_label = 'Y-Coordinate'                  

p.circle(x=xs, y=ys,  line_color="black", alpha=0.5)#, legend_label="Unncovered nodes")
    
# Plot manhole locations:    
p.circle(x='x', y='y', line_color="red",size=10,fill_color="yellow", alpha=0.5, source=source)#, legend_label="Manhole locations") 
   
# Plot optimal locations selected from GA
allsensor = ()
for i in range(0,minSensor):
    if sensorLoc['SensorLoc'][i] in downstreamDependent:
        td = downstreamDependent[sensorLoc['SensorLoc'][i]].dropna()
        tmp1 = findlinkupstream(td, NodeCoord) 
        if (allsensor == ()):
            allsensor = tmp1
        else:
            allsensor = (np.concatenate((allsensor[0], tmp1[0])),np.concatenate((allsensor[1], tmp1[1]))) 
new_tuple = tuple(zip(*allsensor)) # all nodes covered by sensors

# plot covered and uncovered links
for i in range (0,len(Link['Name'].values)):
    rowData = Link.loc[ i , : ]
    fromtoNode=findcoord(rowData,NodeCoord)        
    n1 = (fromtoNode[0][0],fromtoNode[1][0]) # starting nodes of each link which is covered by sensors
    n2 = (fromtoNode[2][0],fromtoNode[3][0]) # ending nodes of each link which is covered by sensors
    if((n1 in new_tuple) and (n2 in new_tuple)):
        p.line([fromtoNode[0][0],fromtoNode[2][0]],[fromtoNode[1][0],fromtoNode[3][0]], line_width = 2.5,
               line_color='blue') #, legend_label='Covered length')
    else:
        p.line([fromtoNode[0][0],fromtoNode[2][0]],[fromtoNode[1][0],fromtoNode[3][0]], 
               line_color='blue', line_dash=[4, 4]) #, legend_label='Uncovered length')       

# plot covered nodes and optimal sensor locations        
for i in range(0,minSensor):
    xn=NodeCoord.loc[NodeCoord['Node']==sensorLoc['SensorLoc'][i]]['X-Coord'].values
    yn=NodeCoord.loc[NodeCoord['Node']==sensorLoc['SensorLoc'][i]]['Y-Coord'].values
    if sensorLoc['SensorLoc'][i] in downstreamDependent:
        td = downstreamDependent[sensorLoc['SensorLoc'][i]].dropna()
        tmp1 = findlinkupstream(td, NodeCoord) 
        p.circle(tmp1[0], tmp1[1], line_color="red", size=10, fill_color="pink", alpha=0.7)#, legend_label="Covered nodes")        
    else:
        print(f"KeyError: {sensorLoc['SensorLoc'][i]} not found in downstreamDependent dictionary") 

    p.circle(x=xn, y=yn, line_color="blue",size=12,fill_color="red", alpha=0.7)#, legend_label="Optimal sensor locations")
# plot labels for sensor nodes
    #source1 = ColumnDataSource(data={'x':xn,'y':yn, 'ID':np.array([str(sensorLoc['index'][i])])})
    #labels = LabelSet(x='x', y='y', text='ID', source=source1, x_offset=5, y_offset=5, render_mode='canvas', text_font_size='12pt')
    #p.add_layout(labels)

#p.legend.location = 'bottom_left'
#items = [("Optimal sensor locations", [p.circle(line_color="blue",size=12,fill_color="red", alpha=0.7)]),
#             ("Covered nodes", [p.circle(line_color="red", size=10, fill_color="pink", alpha=0.7)]), 
#                      ("Unncovered nodes", [p.circle(line_color="black", alpha=0.5)]),
#                      ("Covered length", [p.line(line_width = 2.5, line_color='blue')]),
#                      ("Uncovered length", [p.line(line_color='blue', line_dash=[4, 4])]) ]

#p.legend.items = items
    
legend = Legend(label_text_font_size="14pt", location='bottom_left')
items = [LegendItem(label="Optimal sensor locations", renderers=[p.circle(line_color="blue",size=14,fill_color="red", alpha=0.7)]),
    LegendItem(label="Covered nodes", renderers=[p.circle(line_color="red", size=10, fill_color="pink", alpha=0.7)]),
    LegendItem(label="Unncovered nodes", renderers=[p.circle(line_color="black", alpha=0.5)]),
    LegendItem(label="Covered length", renderers=[p.line(line_width = 2.5, line_color='blue')]),
    LegendItem(label="Uncovered length", renderers=[p.line(line_color='blue', line_dash=[4, 4])])]

legend.items = items

p.add_layout(legend)
p.text(x = max(xs) - 0.8*((min(xs)+max(xs))/2-min(xs)), y = max(ys), text=["System II - A steep system"], 
       text_color="Black", text_font_size="15pt", text_font_style = "bold")

output_notebook()
show(p)        


# In[14]:


len(new_tuple)


# In[ ]:





# In[ ]:




