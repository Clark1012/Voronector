from pprint import pprint
import math
import cv2
import argparse
import numpy as np
import random
import sys
import queue
from svg import *

'''
Author: Peiyi Hou
This file contains all geometry generating and processing functions
'''

# build saliency map serve as edge feature reference
# return nested list with grayscale value of each pixel
def sobel(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1)

    sobelx = np.uint8(np.absolute(sobelx))
    sobely = np.uint8(np.absolute(sobely))
    sobelcombine = cv2.bitwise_or(sobelx,sobely)

    return sobelcombine.tolist()

# extract featured points from saliency map given passed in Threshould
# return a list of points in tuple (x,y)
def cull_sobel(image, cull_perct):
    new_list = []
    for i in range(len(image)):
        for j in range(len(image[0])):
            if (image[i][j] >= cull_perct):
                new_list.append((j,i))
    return new_list

# Further reduce points count given specified cull percentage
# return a list of points in tuple (x,y)
def cull_points(points, cull_perct):
    new_list = []
    cull_num = int(len(points) * cull_perct/100)
    for i in range(cull_num):
        new_list.append(random.choice(points))
    return new_list


# wrapper function for cull_sobel and cull_points
def extract_points(image, cull_sobel_prect=0, cull_points_perct=100):
    saliency = sobel(image)
    culled_saliency = cull_sobel(saliency, cull_sobel_prect)
    return cull_points(culled_saliency, cull_points_perct)


# add pin points on boundry of rectangular area
def add_frame_points(points, image, cull_perct):
    x = image.shape[1]
    y = image.shape[0]
    for i in range(len(points) * cull_perct // 400):
        xpos = random.randrange(x)
        points.append((xpos, 0))
        points.append((xpos, y-1))
    for i in range(len(points) * cull_perct // 400):
        ypos = random.randrange(y)
        points.append((0, ypos))
        points.append((x-1, ypos))
    points.append((0,y-1))
    points.append((x-1,y-1))
    points.append((x-1,0))
    points.append((0,0))

# produce regular 2d grid
# return nested list of points [[[x,y],[x,y]],
#                               [[x,y],[x,y]]]
# skew every other row of points if specified
def produce_grid(image, dist, skew_dist=None):
    x = image.shape[1]
    y = image.shape[0]
    pts = []
    for i in range(0,y,dist):
        row = []
        for j in range(0,x,dist):
            pt = [j,i]
            row.append(pt)
        pts.append(row)

    if skew_dist:
        #skew_angle = skew_angle % 45
        skew_dist = min(skew_dist, x)
        for i in range(1,len(pts),2):
            for pt in pts[i]:
                pt[0] += skew_dist
                if pt[0] >= x:
                    #print("removed")
                    pts[i].remove(pts[i][-1])
                    pts[i-1].remove(pts[i-1][-1])
    return pts


# produce triangle or quadlateral shape as specified from 2d grid
# return polygon represented by list of flattened points [x,y,x,y,x,y]
def polygons_from_grid(grid, sides=3):

    polygons = []
    for i in range(len(grid) - 1):
        for j in range(len(grid[i]) - 1):
            pt1 = grid[i][j]
            pt2 = grid[i][j+1]
            pt3 = grid[i+1][j]
            pt4 = grid[i+1][j+1]
            if sides == 3:
                if i%2==0:
                    triangle_1 = [pt1[0],pt1[1],pt2[0],pt2[1],pt3[0],pt3[1]]
                    triangle_2 = [pt2[0],pt2[1],pt3[0],pt3[1],pt4[0],pt4[1]]
                    polygons.append(triangle_1)
                    polygons.append(triangle_2)
                if i%2==1:
                    triangle_1 = [pt1[0],pt1[1],pt3[0],pt3[1],pt4[0],pt4[1]]
                    triangle_2 = [pt1[0],pt1[1],pt2[0],pt2[1],pt4[0],pt4[1]]
                    polygons.append(triangle_1)
                    polygons.append(triangle_2)
            if sides == 4:
                rect = [pt1[0],pt1[1],pt2[0],pt2[1],pt4[0],pt4[1],pt3[0],pt3[1]]
                polygons.append(rect)
    return polygons


# build opencv subdivison within image sized rectangluar area
# insert points into subdiv and return
def build_subdiv(image, points):
    #print(points)
    rect = (0,0, image.shape[1], image.shape[0])
    subdiv = cv2.Subdiv2D(rect)
    for point in points:
        if rect_contains(rect, point):
            #print(point)
            subdiv.insert(point)
    return subdiv

# check if point in rectangular area
def rect_contains(rect, point) :
    if point[0] < rect[0] :
        return False
    elif point[1] < rect[1] :
        return False
    elif point[0] > rect[2] :
        return False
    elif point[1] > rect[3] :
        return False
    return True


# get openCV delaunay_triangulation from subdiv
# return triangle represented by list [x,y,x,y,x,y]
def delaunay_triangulation(img, subdiv) :
    triangleList = subdiv.getTriangleList()
    size = img.shape
    r = (0, 0, size[1], size[0])
    valid_triangles = []
    for t in triangleList :
        pt1 = (t[0], t[1])
        pt2 = (t[2], t[3])
        pt3 = (t[4], t[5])
        if rect_contains(r, pt1) \
            and rect_contains(r, pt2) \
            and rect_contains(r, pt3) :
            valid_triangles.append(t)
    return valid_triangles


# get openCV voronoi facets from subdiv
# return facets represented by list [x,y,x,y,x,y...]
def make_voronoi(img, subdiv):
    x = img.shape[1]
    y = img.shape[0]
    (facets, centers) = subdiv.getVoronoiFacetList([])
    new_list = []
    for i in range(len(facets)):
        points = []
        for pt in facets[i]:
            pt_x = pt[0]
            pt_y = pt[1]
            if pt_x < 0:
                pt_x = 0
            if pt_y < 0:
                pt_y = 0
            if pt_x >= x:
                pt_x = x-1
            if pt_y >= y:
                pt_y = y-1
            points.append(pt_x)
            points.append(pt_y)
        new_list.append(points)
    return new_list


# produce a set of points based on the greyscale value of passed in Image
# darker area has keeps more points,lighter area keeps less points
# return a list of points in tuple [(x,y), ...]
def greyscale_points(image, cull_perct=85):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    dist = int(min(image.shape[0], image.shape[1])/100)
    points = produce_grid(image, dist)
    new_list = []
    for i in range(5,256,5):
        low = i-5
        high = i
        interval = []
        for n in range(len(points)):
            for m in range(len(points[n])):
                x = points[n][m][0]
                y = points[n][m][1]
                if gray[y][x] < high and gray[y][x] >= low:
                    fuzzy = list(range(int(-dist/2), int(dist/2)))
                    if (len(fuzzy) == 0):
                        fuzzy = [0]
                    fuzzy_x = x + random.choice(fuzzy)
                    fuzzy_y = y + random.choice(fuzzy)
                    if fuzzy_x < 0:
                        fuzzy_x = 0
                    if fuzzy_y < 0:
                        fuzzy_y = 0
                    if fuzzy_x >= image.shape[1]:
                        fuzzy_x = image.shape[1]-1
                    if fuzzy_y >= image.shape[0]:
                        fuzzy_y = image.shape[0]-1
                    interval.append((fuzzy_x,fuzzy_y))

        # use tanh as sigmoid function to control cull ratio
        # for each greyscale interval
        a = low * 6/255 - 3
        ratio = 1 - (math.tanh(a) + 1)/2
        count = int(cull_perct/100*len(interval))
        culled_count = int(count*ratio)
        for j in range(culled_count):
            new_list.append(random.choice(interval))
    return new_list


# produce a mst of points passed in as graph
# whose weight is the euclidean dist between points
# return a list of lines as [[s_x, s_y, e_x, e_y], ...]
def euclidean_mst(points, image):
    class Edge:
        def __init__(self, pt1, pt2, weight):
            self.u = pt1
            self.v = pt2
            self.w = weight
        def __eq__(self, other):
            return (self.w == other.w) and \
                    ((self.u == other.u and self.v == other.v) or\
                     (self.u == other.v and self.v == other.u))
        def __lt__(self, other):
            return self.w < other.w
        def __hash__(self):
            return hash(self.u[0]+self.u[1]+self.v[0]+self.v[1]+round(self.w,2))
        def __str__(self):
            return str(self.u)+str(self.v)+str(round(self.w,2))
        def __repr__(self):
            return str(self)

    # build graph from point set
    # do not connect every point with other points
    # instead perform triangulation and keep sides of triangles as edges of graph
    # returns adjList {pt:{edge, ...}, ...}
    def build_graph(points):
        adjLilst = {}
        for pt in points:
            adjLilst[pt] = set()
        subdiv = build_subdiv(image, points)
        triangleList = subdiv.getTriangleList()
        size = image.shape
        r = (0, 0, size[1], size[0])
        for t in triangleList :
            pt1 = (int(t[0]), int(t[1]))
            pt2 = (int(t[2]), int(t[3]))
            pt3 = (int(t[4]), int(t[5]))
            if rect_contains(r, pt1) and rect_contains(r, pt2) and rect_contains(r, pt3):
                dist_12 = math.sqrt((pt1[0]-pt2[0])*(pt1[0]-pt2[0])\
                                        +(pt1[1]-pt2[1])*(pt1[1]-pt2[1]))
                dist_13 = math.sqrt((pt1[0]-pt3[0])*(pt1[0]-pt3[0])\
                                        +(pt1[1]-pt3[1])*(pt1[1]-pt3[1]))
                dist_23 = math.sqrt((pt2[0]-pt3[0])*(pt2[0]-pt3[0])\
                                        +(pt2[1]-pt3[1])*(pt2[1]-pt3[1]))
                edge_12 = Edge(pt1, pt2, dist_12)
                edge_13 = Edge(pt1, pt3, dist_13)
                edge_23 = Edge(pt2, pt3, dist_23)
                adjLilst[pt1].add(edge_12)
                adjLilst[pt1].add(edge_13)
                adjLilst[pt2].add(edge_23)
        return adjLilst

    # prim's algorithm for mst
    # return a set of Edges
    def prims(start, adj):
        mst = set()
        pq = queue.PriorityQueue()
        visited = {start}
        visited_edge = set()
        for e in adj[start]:
            pq.put(e)
            visited_edge.add(e)
        while(len(visited) < len(adj)):
            if pq.qsize() <= 0:
                print("terminated early")
                # ternimated early, it is a bug happens time to time
                # with large point set that I have not fixed yet
                return mst
            min_edge = pq.get()
            curr_pt = min_edge.v
            if (min_edge.v not in visited):
                mst.add(min_edge)
                visited.add(min_edge.v)
            elif (min_edge.u not in visited):
                mst.add(min_edge)
                visited.add(min_edge.u)
                curr_pt = min_edge.u
            for edge in adj[curr_pt]:
                if (edge not in visited_edge):
                    if (edge.v not in visited) or (edge.u not in visited):
                        visited_edge.add(edge)
                        pq.put(edge)
        return mst
    # convert Edge to lines in [s_x, s_y, e_x, e_y]
    tree = prims(points[0], build_graph(points))
    lines = []
    for edge in tree:
        line = [edge.u[0], edge.u[1], edge.v[0], edge.v[1]]
        lines.append(line)
    return lines


# calculate area center point
# then find color base on center point
# return a tuple of rgb(r,g,b)
def polygon_color(image,points,mask=None):

    sum_x = 0
    for i in range(0, len(points), 2):
        sum_x += points[i]
    sum_y = 0
    for i in range(1, len(points), 2):
        sum_y += points[i]
    avg_x = sum_x/(len(points)/2)
    avg_y = sum_y/(len(points)/2)
    return average_color_from_mask(image, (avg_x, avg_y), mask)


# helper function for polygon_color
# build rectangular mask and calculate mean rgb of the mask area
# return rgb(r,g,b)
# or use center point color without mask
def average_color_from_mask(image, center, mask=None):

    avg_x = int(center[1]) - 1
    avg_y = int(center[0]) - 1
    avg_r = image[avg_x][avg_y][2]
    avg_g = image[avg_x][avg_y][1]
    avg_b = image[avg_x][avg_y][0]
    if mask:
        clr_r = 0
        clr_g = 0
        clr_b = 0
        pixel_count = 0
        half_mask_x = int(mask[0]//2)
        half_mask_y = int(mask[1]//2)
        for i in range(avg_x - half_mask_x, avg_x + half_mask_x):
            if i < 0:
                i = 0
            if i > image.shape[0]:
                i = image.shape[0]
            for j in range(avg_y - half_mask_y, avg_y + half_mask_y):
                if j < 0:
                    j = 0
                if j > image.shape[1]:
                    j = image.shape[1]
                rgb = image[i][j]
                clr_r += int(rgb[0])*int(rgb[0])
                clr_g += int(rgb[1])*int(rgb[1])
                clr_b += int(rgb[2])*int(rgb[2])
                pixel_count += 1
        avg_r = int(math.sqrt(clr_r/pixel_count))
        avg_g = int(math.sqrt(clr_g/pixel_count))
        avg_b = int(math.sqrt(clr_b/pixel_count))
    return [avg_r, avg_g, avg_b]


# get bounding rectangle of certain polygon served as mask used for above
# return tupe(x_size, y_size)
def bounding_size(polygon):
    min_x = sys.maxsize
    min_y = sys.maxsize
    max_x = sys.maxsize* -1
    max_y = sys.maxsize* -1

    for i in range(0, len(polygon), 2):
        if polygon[i] > max_x:
            max_x = polygon[i]
        if polygon[i] < min_x:
            min_x = polygon[i]
    for i in range(1, len(polygon), 2):
        if polygon[i] > max_y:
            max_y = polygon[i]
        if polygon[i] < min_y:
            min_y = polygon[i]

    size_x = abs(max_x - min_x)
    size_y = abs(max_y - min_y)
    return (size_x,size_y)


# associate_polygon_with_color wraps polygon and its average color
# return a list of tuple (color, points)
# svg will read the tuple for svg output
# should be called before any svg functions
def associate_polygon_with_color(image, polygons):
    alist = []
    for polygon in polygons:
        #msk = bounding_size(polygon)
        color = polygon_color(image,polygon, mask=None)
        wrapper = (color, polygon)
        alist.append(wrapper)
    return alist


# wrapper function to perform delaunay_triangulation on passed in Image
# output svg
# return output file name
def draw_dealunay(input, cull_pts_perct=5, cull_sbl_perct=100, frame=0, \
                    boundry=0, grey_weighted=0):
    im = cv2.imread(input)
    output = input.split('/')[-1]
    sobel_points = None
    if grey_weighted == 0:
        sobel_points = extract_points(im, cull_sobel_prect=cull_sbl_perct, \
                                        cull_points_perct=cull_pts_perct)
    else:
        sobel_points = greyscale_points(im)
    if frame:
        add_frame_points(sobel_points, im, cull_pts_perct)
    subdiv = build_subdiv(im, sobel_points)
    triangles = delaunay_triangulation(im, subdiv)
    polygon_list = associate_polygon_with_color(im, triangles)
    name = output.split('.')[0] + "_delaunay_" + \
            str(cull_pts_perct) + "_" + str(cull_sbl_perct) + ".svg"

    write_file(name, im.shape[1], im.shape[0], polygons=polygon_list, boundry=boundry)
    return name


# wrapper function to perform voronoi on passed in Image
# output svg
# return output file name
def draw_voronoi(input, cull_pts_perct=5, cull_sbl_perct=100, frame=0, \
                boundry=0, grey_weighted=0):
    im = cv2.imread(input)
    output = input.split('/')[-1]
    sobel_points = extract_points(im, cull_sobel_prect=cull_sbl_perct, \
                                    cull_points_perct=cull_pts_perct)
    if grey_weighted == 0:
        sobel_points = extract_points(im, cull_sobel_prect=cull_sbl_perct, \
                                        cull_points_perct=cull_pts_perct)
    else:
        sobel_points = greyscale_points(im)
    if frame:
        add_frame_points(sobel_points, im, cull_pts_perct)
    subdiv = build_subdiv(im, sobel_points)
    voronois = make_voronoi(im, subdiv)
    #pprint(voronois)
    polygon_list = associate_polygon_with_color(im, voronois)
    name = output.split('.')[0] + "_voronoi_" + \
            str(cull_pts_perct) + "_" + str(cull_sbl_perct) + ".svg"
    write_file(name, im.shape[1], im.shape[0], polygons=polygon_list, boundry=boundry)
    return name


# wrapper function to prodeuce MST on passed in Image
# output svg
# return output file name
def draw_tree(input, dist=10, skew_dist=None, cull_pts_perct=5, cull_sbl_perct=100, \
                random=0, grey_weighted=0):
    im = cv2.imread(input)
    output = input.split('/')[-1]
    points = None
    if random:
        points = extract_points(im, cull_sobel_prect=cull_sbl_perct, \
                                    cull_points_perct=cull_pts_perct)
    if grey_weighted:
        points = greyscale_points(im)
    if not points:
        print("ortho tree")
        points = produce_grid(im, dist, skew_dist)
        pts = []
        for row in points:
            for p in row:
                #print(p)
                pts.append(tuple(p))
        points = pts
        #print(points)
    lines = euclidean_mst(points, im)
    polygon_list = associate_polygon_with_color(im, lines)
    name = output.split('.')[0] + "_tree_" + str(dist) + ".svg"
    write_file(name, im.shape[1], im.shape[0], lines=polygon_list)
    return name


# wrapper function to prodeuce grids pattern on passed in Image
# output svg
# return output file name
def draw_grid(input, dist=10, sides=3, skew_dist=None, boundry=0, voronoi=0):
    im = cv2.imread(input)
    output = input.split('/')[-1]
    points = produce_grid(im, dist, skew_dist)
    polygons = polygons_from_grid(points, sides)
    if voronoi:
        pts = []
        for row in points:
            for p in row:
                pts.append(tuple(p))
        subdiv = build_subdiv(im, pts)
        polygons = make_voronoi(im, subdiv)
    polygon_list = associate_polygon_with_color(im, polygons)
    name = output.split('.')[0] + "_grid_" + str(sides) + "_" + str(skew_dist) + ".svg"
    write_file(name, im.shape[1], im.shape[0], polygons=polygon_list, boundry=boundry)
    return name
