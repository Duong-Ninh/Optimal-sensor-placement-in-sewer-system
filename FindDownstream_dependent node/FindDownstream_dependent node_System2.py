# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 08:50:28 2022

@author: a1643537
"""
#Python code for sensor localization of a wastewater network using network topology
#Read network characteristics
import numpy as np
import pandas as pd

# All functions required for find downstream nodes of a node
def ismember(A, B):
    return [ np.sum(a == B) for a in A ]
def is_empty(any_structure):
    if any_structure:        
        return False
    else:        
        return True
def findDownstreamNode(source,sink,node):
    notvisit=np.ones(len(source)+1,dtype=bool)
    p=fdn(source,sink,node,notvisit,[])
    p=np.sort(p)
    return p

def fdn(source,sink,node,notvisit,p):
    idx=ismember(source,node)
    pp=[]
    for i in range (len(source)):
        if (idx[i] ==1):
            pp.append(sink[i])        
    if (is_empty(pp)==False):
        notvisit[pp]=False
        p.append(pp)
        p= fdn(source, sink, pp, notvisit, p)
    
    return p   


excelfilepath= 'U:\phd_program_ninh\Data and code\paper1\System2_network.xlsx'
NodeDB=pd.read_excel(excelfilepath,sheet_name='Node')
LinkDB=pd.read_excel(excelfilepath,sheet_name='Link')
ManholeID=pd.read_excel(excelfilepath,sheet_name='ManholeLocation')





#Identify index of FromNode and ToNode

nodeIndex=list(NodeDB['ID'].index)

fromNodeIndex=[]
toNodeIndex=[]
try:
    for i in range(len(LinkDB)):
        tmp=list(NodeDB.loc[NodeDB['ID'].astype(float)==LinkDB['From'][i].astype(float)].index)
        tmp1=list(NodeDB.loc[NodeDB['ID'].astype(float)==LinkDB['To'][i].astype(float)].index)    
        if (tmp==[]):
            tmp=9999999999
            fromNodeIndex.append(tmp)
        else:
            fromNodeIndex.append(tmp[0])
        if (tmp1==[]):
            tmp1=9999999999
            toNodeIndex.append(tmp1)
        else:
            toNodeIndex.append(tmp1[0])
    manholeIndex=[]
    manholeElev=[]
    for i in range(len(ManholeID)):
        tmp=list(NodeDB.loc[NodeDB['ID'].astype(float)==ManholeID['ID'][i].astype(float)].index)
        tmp1=list(NodeDB['Elevation'].loc[NodeDB['ID'].astype(float)==ManholeID['ID'][i].astype(float)])
        manholeIndex.append(tmp[0])
        manholeElev.append(tmp1[0])
        
except ValueError:
    print(" ERROR!!! For this network ID of Node and Link are in types of INTEGER or FLOAT")
    print(" PLEASE chane Node, Link IDs to these types or remove .ASTYPE() in the code")


# Identify all possible downstream dependent nodes of a manhole
AlldependentLst=[]
DependentonElevLst=[]
elev_error=0
Depth_normal=0
a=np.asarray(fromNodeIndex)
b=np.asarray(toNodeIndex)
c=np.asarray(manholeIndex)
for i in range(len(c)):    
    x=findDownstreamNode(a,b,c[i])
    tmp=[val for sublist in x for val in sublist]
    AlldependentLst.append(NodeDB['ID'][tmp]) # This List could be ignored                              
    # Now identify all dependent nodes that has their ground elevations above the corresponding manhole invert elevation
    tmp1=[]
    for j in range(len(tmp)):
        if (NodeDB['Elevation'][tmp[j]]+0.7*NodeDB['MaxDepth'][tmp[j]]+elev_error>manholeElev[i]+Depth_normal):
            tmp1.append(NodeDB['ID'][tmp[j]])
    DependentonElevLst.append(tmp1)   

### save to csv then done
out=pd.DataFrame(DependentonElevLst).transpose()
out
out.to_csv('Output_downstream_dependent_nodes_system2_70%.csv')
