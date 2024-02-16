import math
from shapely import affinity
from shapely.geometry import Polygon
import numpy as np

def quardratic_equation_solver(a,b,c):
    '''
    input: a,b,c in form ax^2+bx+c=0
    output: The roots of the equation 
    '''
    x1,x2 = 0,0
    d = b**2-4*a*c # discriminant
    if d < 0:
        print("This equation has no real solution")
    elif d == 0:
        x = (-b+math.sqrt(b**2-4*a*c))/2*a
        print("This equation has one solutions: ", x)
        x1,x2 = x,x
    else:
        x1 = (-b + math.sqrt(d)) / (2 * a)
        x2 = (-b - math.sqrt(d)) / (2 * a)
    return x1,x2

# remove entries from the dict
def remove_entries_from_dict(entries, the_dict):
    '''
    input: entries to remove (a set), the dict to remove 
    '''
    for key in entries:
        if key in the_dict:
            del the_dict[key]

#added to match nodes
def nmatch(n1, n2):
    return n1==n2


#normalized polygon
def create_normalized_polygon(p1,r1):
    '''
    input: Polygon object p1, rotation of the polygon r1
    output: Normalized polygon object
    '''
    p2 = affinity.rotate(p1,r1,origin='centroid')
    normalized_x = p2.exterior.coords.xy[0] - np.repeat(min(p2.exterior.coords.xy[0]),len(p2.exterior.coords.xy[0]))
    normalized_y = p2.exterior.coords.xy[1] - np.repeat(min(p2.exterior.coords.xy[1]),len(p2.exterior.coords.xy[1]))

    normalized_polygon = Polygon(tuple(zip(normalized_x,normalized_y)))
    return normalized_polygon

def combine_a_list(ls,delimiter="_"):
    '''
    input: list and the delimiter
    output: concatenated name
    '''
    name = ""
    for item in ls:
        name = name +delimiter+item
        
    return name[1:len(name)]

def add_value_to_a_matrix(m, value,position_row,position_col):
    '''
    Input: matrix, value to add, position_row, position_col
    Assigns the value to the matrix
    '''
    num_of_cols = m.shape[1]
    position = [int(num_of_cols * position_row + position_col)]
    np.put(m, position,value)


def input_obj_id_to_change_labels(data_df):
    '''
    This function changes the label of the data_df according to the user input
    '''
    obj_id_to_change = input("What is the object id you want to change? \n")
    label_of_the_id = input("What is the label of object ID? \n")
    if isinstance(obj_id_to_change, int):
        data_df.loc[int(obj_id_to_change),'label'] = label_of_the_id
    else: 
        print("incorrect input! No more changes will be made to labels")
    more_entries = input("Are there more changes to do (y/n)? \n")
    if more_entries == "y":
        input_obj_id_to_change_labels(data_df)
    elif more_entries == "n":
        print("no more updates on object labels")
    else:
        print("incorrect input! No more changes will be made to labels")