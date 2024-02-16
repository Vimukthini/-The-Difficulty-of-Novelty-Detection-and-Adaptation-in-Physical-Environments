from shapely.geometry import Polygon, Point
import numpy as np
from miscellaneous_functions import quardratic_equation_solver

#creating the bounding box 
def get_bounding_box_vals(df_row, coord_type = "x/y"):
    '''
    returns the min, max, and bounding box vals
    coord_type = "x", "y" (coord type should be specified)
    '''
    min_row = []
    max_row = []
    bounding_box_vals = []

    for vals in df_row:
        min_val = min(vals)
        max_val = max(vals)
        if coord_type=="x":
            bounding_box =[min_val,min_val,max_val,max_val,min_val]
        elif coord_type =="y":
            bounding_box =[min_val,max_val,max_val,min_val,min_val]
        else:
            print("unspecified coordinates")
            bounding_box = []
        
        min_row.append(min_val)
        max_row.append(max_val)
        bounding_box_vals.append(bounding_box)
        
    return min_row,max_row,bounding_box_vals


#creating the polygon
def create_bounding_box_polygon(x_min,y_min,x_max,y_max):
    '''
    input: float values of the bounding box
    output: cordinates of the polygon, x- coordinates, y-coordinates, Polygon object
    '''
    x_coords = [x_min,x_min,x_max,x_max,x_min]
    y_coords = [y_min,y_max,y_max,y_min,y_min]
    polygon_coords = tuple(zip(x_coords,y_coords))
    polygon_obj = Polygon(polygon_coords)

    return polygon_coords,x_coords,y_coords,polygon_obj


#TPP check
def tangential_touch_check(p1,p2):
    '''
    input: two polygons
    output: True/False
    '''
    TPP_flag = False
    for i in range(4):
        if p1.bounds[i]==p2.bounds[i]:
            TPP_flag = True
            break
    return TPP_flag

# RCC-8 code
def rcc_8_check(p1,p2):
    '''
    input: two polygons
    output: rcc-8 representation
    '''
    representation = "ND"
    if p1.disjoint(p2):
        if p1.distance(p2)<=1.0:
            #The adjustment is done to account for noise. Threshold is taken as +/-1
            representation = "EC"
        else:
            representation = "DC"
    else:
        if p1.intersection(p2).geom_type == "LineString":
            representation = "EC"
        elif ((p1.intersection(p2).bounds==p1.bounds) and (p1.intersection(p2).bounds==p2.bounds)):
            representation = "EQ"
        elif p1.within(p2):
            representation = "TPP" if tangential_touch_check(p1,p2) else "NTPP"
        elif p2.within(p1):
            representation = "TPPi" if tangential_touch_check(p1,p2) else "NTPPi"
        elif ((p1.intersection(p2)!=p1) and (p1.intersection(p2)!=p2)):
            representation = "PO"
        else:
            print(p1.intersection(p2))
            
    return representation

#QDC code 
def qdc_check(p1,p2,threshold_x =70, threshold_y = 70):
    '''
    input: two polygons, threshold to determine far/near
    output: qdc representation
    '''
    representation = "ND"
    if p1.disjoint(p2) == False:
        representation = "to"
    elif p1.disjoint(p2):
        #create the bigger polygon for relation check
        p0xmin, p0ymin, p0xmax, p0ymax = (np.array(p1.bounds)+(-threshold_x,-threshold_y,threshold_x,threshold_y))
        p0 = create_bounding_box_polygon(p0xmin, p0ymin, p0xmax, p0ymax)[3]   
        representation = "fr" if p0.disjoint(p2) else "nr"
    else:
        print(p1.intersection(p2))
        print(p0.intersection(p2))
    return representation

#making the triangle for STAR
def triangles_for_STAR(p=(0,0),hypotenuse_len=500):
    '''
    input: reference point, hypotenuse length
    output: coordinates of the STAR ref traingle 
    '''
    cos_factor = hypotenuse_len*np.cos(67.5*np.pi/180)
    sin_factor = hypotenuse_len*np.sin(67.5*np.pi/180)
    
    t1 = adjust_point(p,cos_factor,sin_factor)
    t2 = adjust_point(p,sin_factor,cos_factor)
    t3 = adjust_point(p,sin_factor,-cos_factor)
    t4 = adjust_point(p,cos_factor,-sin_factor)
    t5 = adjust_point(p,-cos_factor,-sin_factor)
    t6 = adjust_point(p,-sin_factor,-cos_factor)
    t7 = adjust_point(p,-sin_factor,cos_factor)
    t8 = adjust_point(p,-cos_factor,sin_factor)
    
    STAR_rep = ["tp","tr","rt","br","bt","bl","lt","tl"]
    t = [t1,t2,t3,t4,t5,t6,t7,t8]
        
    polygon_list = []
    
    polygon_list.append([STAR_rep[0],Polygon([p,t1,t8])])
    for i in range(1,8):
        p0 = Polygon([p,t[i-1],t[i]])
        polygon_list.append([STAR_rep[i],p0])
        
    return polygon_list

#adjusting x and y point
def adjust_point(p,x_adjust,y_adjust):
    '''
    input: reference point, x-adjust point, y-adjust point
    output: adjusted point
    '''
    p_adj = p[0]+x_adjust,p[1]+y_adjust
    
    return p_adj

#STAR code
def STAR_check(p1=(0,0),p=(0,0),hypotenuse_len=500):
    '''
    input: (p1) point to check, (p) point of reference, hypotenuse length
    output: STAR representation
    '''
    triangle_rep = triangles_for_STAR(p,hypotenuse_len)
    
    representation = "ND"
    for i in range(8):
        if Point(p1).disjoint(triangle_rep[i][1])==False:
            representation = triangle_rep[i][0]
            break
            
    return representation