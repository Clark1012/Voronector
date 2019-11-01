
'''
Author: Peiyi Hou
This file contains functions that write dataset into svg
'''


# return string of xml header
def svg_header(width, height):
    svg_header = '''<?xml version="1.0" standalone="no"?>
                <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
                "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
                '''
    size = '<svg width="' + str(width/100) + 'cm" height="' + str(height/100) +\
            'cm" viewBox="0 0 ' + str(width) + " " + str(height) + '" '\
                '''xmlns="http://www.w3.org/2000/svg" version="1.1">
                <desc>Testing - lowpoly</desc>'''
    return svg_header+size

# return string of a single <polygon>...</polygon>
def write_polygon(polygons, line=0):
    polygon_strs = []
    for polygon in polygons:
        color_str = "rgb(%s)"%(",".join([str(clr) for clr in polygon[0]]))
        points_str = " ".join([str(pos) for pos in polygon[1]])
        header = "<polygon fill="
        tail = '"/>'
        stroke_str = ""
        if line:
            stroke_str = 'stroke="rgb(1,1,1)" stroke-width="1"'
            color_str = "rgb(254,254,254)"
        polygon_str = header + '"' + color_str + '" '+ stroke_str + ' points="'\
                    + points_str + tail
        polygon_strs.append(polygon_str)
    return polygon_strs

# return string of a single <polygline>...</polyline>
def write_lines(lines,thickness=1,uni_color = None):
    line_strs = []
    for line in lines:
        clr = line[0]
        if uni_color != None:
            clr = uni_color
        color_str = "rgb(%s)"%(",".join([str(clr) for clr in line[0]]))
        thickness_str = 'stroke-width="%d"'%(thickness)
        points_str = " ".join([str(pt) for pt in line[1]])
        header = '<polyline fill="RGB(254,254,254)" stroke='
        tail = '"/>'
        line_str = header + '"' + color_str + '" ' + thickness_str + ' points="'\
                    + points_str + tail
        line_strs.append(line_str)
    return line_strs


# concatennate header, polygons and lines, and write to file
def write_file(path, width, height, polygons=None, \
                lines=None, uni_color=None, thickness=None, boundry=0):
    file = open(path, 'w')
    file.write(svg_header(width, height))
    file.write('\n')
    if polygons:
        for polygon in write_polygon(polygons,line=boundry):
            file.write(polygon)
            file.write('\n')
    if lines:
        for line in write_lines(lines):
            file.write(line)
            file.write('\n')
    file.write("</svg>")
    file.close()
