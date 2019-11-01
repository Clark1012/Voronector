'''
Author: Peiyi Hou


============================ READ ME ==================================

run "python main.py" in terminal to start demo
libraries needed:
openCV
numpy
PyQt5

detailed instruction in report section 'GUI and OutPut Options'
OPEN and CONVERT do what they say...

MODE:
Delaunay Traingulation
Voronoi Tessellation
Tri-grid
Square-grid
Voronoi-grid
Ortho mst
Random mst

DENSITY:
recommended between [1 - 20]
controls number of points used to do delaunay_triangulation and voronoi

THRESHOULD:
strictly between [0 - 255]
controls edge feature Threshould according to sobel mapped greyscale.
recommended at a intermediate level [50 - 150]

GRID SIZE:
grid size of for Tri-grid and Square-grid, in pixel_count

SKEW DISTANCE:
recommended bewtween [0 - GRIDSIZE]
skew every other line by number of pixel_count, you may try go over recommeded
skew_dist, it might crash... and doesn't work well near right hand boundry

PIN_FRAME:
for delaunay and voronoi. if produced polygons does not fill the whole
rectangular image area, Select this option to add pin points around the boundry
so that resulted svg fills whole rectangular area

EDGE_ONLY:
fill polygon with nothing. Effective for delaunay and voronoi and grids

GREY_WEIGHTED:
Effective for delaunay and voronoi.
generating points based on greyscale of raster image, regardless of edge feature.
Darker area has denser polygons, lighter area has coarser ones.
'''

if __name__ == "__main__" :
    import sys
    from gui import *
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
