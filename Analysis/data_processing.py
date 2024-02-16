#from webbrowser import get
import pandas as pd
import plotly.graph_objects as go
# import plotly.express as px
import numpy as np
# from shapely import affinity
# import networkx as nx
from miscellaneous_functions import *
from qsr import get_bounding_box_vals
# import matplotlib.pyplot as plt

#read the basemap csv file
basemap_df = pd.read_csv("basemap_df.csv")

# Data preperation
def process_data(data_path = "game_levels/",level_name = "00000_0_0_11_0_1.xml.json"):
    '''
    input: The level path and the level name
    output:  
    '''
    data = pd.read_json(data_path+level_name)
    #get ground coordinate value
    ground_coord = data['features'][0][0]['properties']['yindex']

    #make the dataframe with obj data
    id = 0
    obj_id = [] #obj counter
    label = []
    #visisble properties
    coords = []
    colours = []
    rotation = []
    invisible_properties = []

    for objs in data['features'][0]:
        obj_id.append(id)
        if len(objs['geometry'])!=0:
            coords.append(objs['geometry']['coordinates'][0])
        else: 
            coords.append(np.nan)
            
        label.append(objs['properties']['label'])
        colours.append(objs['properties']['colormap'])
        
        if 'rotation' in objs['properties']:
            rotation.append(objs['properties']['rotation'])
        else: rotation.append(np.nan)
            
        print(objs['properties'],"\n")  
        
        invisible_properties.append(objs['properties'])
        id += 1
    data_df = {"obj_id":obj_id, "label":label, "coords": coords, "colours":colours, 
           "rotation":rotation, "invisible_properties":invisible_properties}
    data_df = pd.DataFrame(data_df)

    # remove from invisible properties
    entries_to_remove = ("id","label","rotation","colormap","yindex") # from invisible property list
    for i in range(len(data_df)):
        remove_entries_from_dict(entries_to_remove,data_df['invisible_properties'][i])

    #round the datadf
    for i in range(len(data_df['colours'])):   
        for j in range(len(data_df['colours'][i])):
            data_df['colours'][i][j]['color'] = float(round(data_df['colours'][i][j]['color'],4))
            data_df['colours'][i][j]['percent'] = float(round(data_df['colours'][i][j]['percent'],4))

    
    # round all values to 4 decimals
    data_df['rotation'] = round(data_df['rotation'],4)
    for inv_prop in data_df['invisible_properties']:
        for key in inv_prop:
            inv_prop[key] = round(inv_prop[key],4)
            
    #adjusting the rotation
    data_df['rotation'] = [0.0000 if rot==-0.000 else rot for rot in data_df['rotation']]
    #add the sling rotation
    data_df.loc[1,'rotation'] = 0

    # #get basemap df
    # basemap_df = arrange_basemap(basemap)

    #adjust the label of the object 
    for j in range(2,len(data_df)):
        for i in range(len(basemap_df)):
            if basemap_df['colours'][i]==str(data_df['colours'][j]):
                #data_df['label'][j] = basemap_df['obj_label'][i]
                data_df.loc[j,'label'] = basemap_df['obj_label'][i]
                break
            else:
                data_df.loc[j,'label'] = "novel_object_"+data_df.loc[j,'label']
    # print data df
    print(data_df)
    #correct labels for novelty
    is_correct_labels = input('Are the labels correct (y/n)?\n')
    if is_correct_labels == "n":
        input_obj_id_to_change_labels(data_df)
    elif is_correct_labels == "y":
        print("no updates on object labels")
    else: 
        print("incorrect input! No changes will be made to labels")

    x_all = []
    y_all = []
    # getting vertices for visualization
    for i in range(len(data_df)):
        #print(data_df['label'][i])
        if data_df['label'][i]=='Ground':
            x_all.append([0])
            y_all.append([ground_coord])
        else:
            x = []
            y = []
            #print(data_df['coords'][i])
            for a,b in data_df['coords'][i]:
                x.append(a)
                y.append(np.abs(b-ground_coord))
                
            x.append(x[0])
            y.append(y[0])
            x_all.append(x)
            y_all.append(y)
    data_df['x_all'] = x_all
    data_df['y_all'] = y_all

    #show the figure
    fig = go.Figure()
    for i in range(len(data_df)):
        fig.add_trace(go.Scatter(
            x=x_all[i],
            y=y_all[i],
            name = data_df['label'][i] # legend entry 
        ))
        
    #fig['layout']['yaxis']['autorange'] = "reversed"      
    fig.show()

    data_df['xmin'], data_df['xmax'], data_df['x_bounds']= get_bounding_box_vals(data_df['x_all'],"x")
    data_df['ymin'], data_df['ymax'], data_df['y_bounds']= get_bounding_box_vals(data_df['y_all'],"y")

    #make the bounding box 
    bb = []
    for i in range(len(data_df)):
        bb.append(tuple(zip(data_df['x_bounds'][i],data_df['y_bounds'][i])))

    data_df['bounding_box'] = bb

    return data_df
    