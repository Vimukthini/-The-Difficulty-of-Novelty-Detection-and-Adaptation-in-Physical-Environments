from shapely.geometry import Polygon
from miscellaneous_functions import *

from qsr import get_bounding_box_vals,create_bounding_box_polygon, rcc_8_check, qdc_check, STAR_check
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

# QSR relations
def get_qsr_relations(data_df):
    '''
    input: data_df dataframe (modified dataframe after data processing)
    output: rcc8, qdc, star, index_order
    '''
    rcc_8, label_dict = get_rcc8(data_df)
    qdc = get_qdc(data_df)
    star = get_star(data_df)

    return rcc_8,qdc,star,label_dict


def get_rcc8(data_df):
    m_rcc8 = np.full((len(data_df)-1, len(data_df)-1), "ND") 
    rcc_8_rep = []
    index_dict = {}
    for i in range(1,len(data_df)):
        index_dict[i-1] = data_df['label'][i]
        for j in range(1,len(data_df)):
            p1 = Polygon(data_df['coords'][i])
            p2 = Polygon(data_df['coords'][j])
            
            rep = rcc_8_check(p1,p2)
            rcc_8_rep.append([data_df['label'][i],data_df['label'][j],rep])
            #print([i-1],[j-1],data_df['label'][i],data_df['label'][j],rep)
            add_value_to_a_matrix(m_rcc8,rep,i-1,j-1)
    return m_rcc8,index_dict


def get_qdc(data_df):
    qdc_rep = []
    m_qdc = np.full((len(data_df)-1, len(data_df)-1), "ND") 
    for i in range(1,len(data_df)):
        for j in range(1,len(data_df)):
            p1 = Polygon(data_df['coords'][i])
            p2 = Polygon(data_df['coords'][j])
            
            rep = qdc_check(p1,p2)
            qdc_rep.append([data_df['label'][i],data_df['label'][j],rep])
            add_value_to_a_matrix(m_qdc,rep,i-1,j-1)
    #qdc_rep
    return m_qdc

def get_star(data_df):
    data_df['xmid'] = (data_df['xmax']-data_df['xmin'])/2 + data_df['xmin']
    data_df['ymid'] = (data_df['ymax']-data_df['ymin'])/2 + data_df['ymin']

    STAR_rep = []
    m_star = np.full((len(data_df)-1, len(data_df)-1), "ND") 
    for i in range(1,len(data_df)):
        for j in range(1,len(data_df)):
            data_df['xmid'][j]
            rep  = STAR_check(p1=(data_df['xmid'][j],data_df['ymid'][j]),p=(data_df['xmid'][i],data_df['ymid'][i]),hypotenuse_len=1500)
            STAR_rep.append([data_df['label'][i],data_df['label'][j],rep])
            add_value_to_a_matrix(m_star,rep,i-1,j-1)

    #STAR_rep
    return m_star

#Observation state representation 

def draw_observation_state_graph(index = 1,main_node = "platform",sub_nodes = {"shape": "platform"+"_shape", "colour": "platform"+"_colour"},
                                nodesize = 1500, alpha_val = 0.9):
    plt.figure(index)
    G = nx.DiGraph()
    G.add_node(main_node, id = main_node)
    edge_lebel_dict = {}
    sub_node_list = list(sub_nodes.keys())
    for j in range(len(sub_nodes)):
        G.add_node(sub_nodes[sub_node_list[j]], id = sub_nodes[sub_node_list[j]])
        G.add_edge(main_node,sub_nodes[sub_node_list[j]])
        edge_lebel_dict[(main_node, sub_nodes[sub_node_list[j]])] = sub_node_list[j]
    pos = nx.spectral_layout(G)
    nx.draw(G, pos, node_size=nodesize, alpha=alpha_val,
            labels={node: node for node in G.nodes()})
    
    nx.draw_networkx_edge_labels(
    G, 
    pos,
    edge_labels= edge_lebel_dict
    )

    return G

#read polygon normalized dataset
ref_norm_polygon_df = pd.read_excel("normalized_polygon.xlsx")

#ajust x and y of normalized polygon
ref_x_coords,ref_y_coords = [""], [""]
for j in range(1,len(ref_norm_polygon_df)):
    x = list(map(float, ref_norm_polygon_df['normalized_polygon_x'][j][12:-2].split(', ')))
    y = list(map(float, ref_norm_polygon_df['normalized_polygon_y'][j][12:-2].split(', ')))
    
    ref_x_coords.append(x)
    ref_y_coords.append(y)
ref_norm_polygon_df['normalized_polygon_x'] = ref_x_coords
ref_norm_polygon_df['normalized_polygon_y'] = ref_y_coords
#ref_norm_polygon_df.head()

def get_observation_state(data_df):
    '''
    input: data_df dataframe
    output: observation state graph objects
    '''
    polygon_object_shape = [""]
    for i in range(1,len(data_df)):
        norm_pol_obj = create_normalized_polygon(Polygon(data_df['coords'][i]), data_df['rotation'][i])
        
        obj_shape = "novel_object_shape"
        for j in range(1,len(ref_norm_polygon_df)):
            len_ref_polygon = len(ref_norm_polygon_df['normalized_polygon_x'][j])
            if len_ref_polygon==len(norm_pol_obj.exterior.coords.xy[0]):
                offset = np.repeat(3,len_ref_polygon) # assuming an offset of 3 pixels
                max_x = ref_norm_polygon_df['normalized_polygon_x'][j] + offset
                min_x = ref_norm_polygon_df['normalized_polygon_x'][j] - offset
                max_y = ref_norm_polygon_df['normalized_polygon_y'][j] + offset
                min_y = ref_norm_polygon_df['normalized_polygon_y'][j] - offset

                x = norm_pol_obj.exterior.coords.xy[0]
                y = norm_pol_obj.exterior.coords.xy[1]

    #             print(min_y,y)
    #             print(min_y<=y)
    #             print(False in (min_y<=y))
    #             print(False in (max_x>=x))
                if not(False in (max_x>=x)) and not(False in (min_x<=x)) and not(False in (max_y>=y)) and not(False in (min_y<=y)):
                    obj_shape = ref_norm_polygon_df['polygon_name'][j]
    #                 print(obj_shape)
        polygon_object_shape.append(obj_shape)

    # add polygon object shape 
    data_df['polygon_object_shape'] = polygon_object_shape

    #draw obseration state
    graph_rep = []
    for i in range(1,len(data_df)):
        index = i
        main_node = data_df['label'][i][:-2] if data_df['label'][i].split('_')[-1].isdigit() else data_df['label'][i]
        #print(main_node)

        G = draw_observation_state_graph(index=index,main_node=main_node,
                                    sub_nodes={"shape":data_df['polygon_object_shape'][i],
                                                "colour":main_node+"_colour",
                                                "rotation":data_df['rotation'][i]},
                                    nodesize=2500, alpha_val=0.8)
        
        graph_rep.append(G)
        #print(index)
    
    return graph_rep

def get_world_state(data_df):
    '''
    input: data_df dataframe
    output: world state graph objects
    '''
    #draw world state
    graph_rep = []
    for i in range(2,len(data_df)):
        index = i-1
        main_node = data_df['label'][i][:-2] if data_df['label'][i].split('_')[-1].isdigit() else data_df['label'][i]
        #print(main_node)

        G = draw_observation_state_graph(index=index,main_node=main_node,
                                    sub_nodes=data_df['invisible_properties'][i],
                                    nodesize=2500, alpha_val=0.8)
        
        graph_rep.append(G)
        #print(index)
    
    return graph_rep