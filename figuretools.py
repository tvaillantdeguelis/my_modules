#!/usr/bin/env python
# coding: utf8

import sys
import os

import seaborn as sns
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.colors import from_levels_and_colors
from matplotlib.ticker import MultipleLocator
from cycler import cycler

from my_modules.geotools import geo_distance


# def setlatexfont():

#     mpl.rc('text', usetex=True) # Let TeX do the typsetting
#     mpl.rcParams['text.latex.unicode'] = True # use \\ for unicode
#     mpl.rcParams['text.latex.preamble'] = r"\usepackage{textcomp}" + \
#         r"\usepackage{textgreek}" +\
#         r"\usepackage{subscript}" +\
#         r"\usepackage{siunitx}" +\
#         r'\usepackage{amsmath}' # use \textmu for µ

#     fontProperties = {'family':'Helvetica',
#         'weight' : 'normal', 'size' : 12}

#     a = plt.gca()
#     a.set_xticklabels(a.get_xticks(), fontProperties)
#     a.set_yticklabels(a.get_yticks(), fontProperties)

#     return


class CALIOPFigureMaker():
    def __init__(self):
        self.fig_w = cm2in(17.7) # cm
        self.fig_h = cm2in(6) # cm
        self.adj_left = 0.09
        self.adj_bottom = 0.18
        self.adj_right = 0.84
        self.adj_top = 0.7
        self.y_major_locator = 5
        self.y_minor_locator = 1
        self.edges_removal = None
        self.axes_labelsize = 8
        self.xtick_labelsize = 8
        self.ytick_labelsize = 8
    
    def set_and_create_fig_folder(self, figures_path, granule_date, lon_min, lon_max):
        self.fig_folder = os.path.join(figures_path, f"{granule_date}_lon_{lon_min:.2f}_{lon_max:.2f}")
        os.makedirs(self.fig_folder, exist_ok=True)
        
    def set_head_filename(self, granule_date, lon_min, lon_max):
        self.head_filename = f'{granule_date}_lon_{lon_min:.2f}_{lon_max:.2f}'
        self.granule_date = granule_date
    
    def set_edges_removal(self, edges_removal):
        self.edges_removal = edges_removal
    
    def set_max_detect_level(self, max_detect_level):
        self.max_detect_level = max_detect_level
        
    def set_coordinates(self, lat, lon, alt=None):
        if self.edges_removal is None:
            self.edges_removal = 0
            # raise ValueError("edges_removal is None. Set edges_removal first.")
        if self.edges_removal != 0: # to avoid error with "-0"
            self.lat = remove_edges(lat, self.edges_removal)
            self.lon = remove_edges(lon, self.edges_removal)
        else:
            self.lat = lat
            self.lon = lon
        if alt is not None:
            self.alt = alt

        # Get x and y axes bin limits
        self.pindex = np.arange(self.lat.size)
        self.pindexbins = compute_bounds(self.pindex, 1)
        if alt is not None:
            self.altbins = compute_bounds(alt, alt[1]-alt[0])

    def plot_params(self, ax, ymin=None, ymax=None, flag_invert_xaxis=False, flag_lat_lon_label=True, flag_dist=True, flag_dist_label=True, flag_granule=True):
        # subtitle
        if flag_granule:
            ax.text(-0.1, 1.11, self.granule_date, ha='left', va='center', fontsize=6, weight='bold', transform=ax.transAxes)

        # y-axis
        ax.yaxis.set_major_locator(MultipleLocator(self.y_major_locator))
        ax.yaxis.set_minor_locator(MultipleLocator(self.y_minor_locator))
        if ymin is None:
            ymin = min(self.altbins)
        if ymax is None:
            ymax = max(self.altbins)
        plt.ylim(ymin, ymax)
        plt.ylabel('Altitude (km)')

        # x-axis
        lat_lon_dist_xaxis(ax, self.lat, self.lon, self.pindex, self.pindexbins, flag_lat_lon_label=flag_lat_lon_label, flag_dist=flag_dist, flag_dist_label=flag_dist_label, 
                            dist_labelsize=self.axes_labelsize, dist_tick_labelsize=self.xtick_labelsize)

        # Set fontsizes
        ax.xaxis.label.set_size(self.axes_labelsize)
        ax.yaxis.label.set_size(self.axes_labelsize)
        ax.xaxis.set_tick_params(labelsize=self.xtick_labelsize)
        ax.yaxis.set_tick_params(labelsize=self.ytick_labelsize)
        
        if flag_invert_xaxis:
            ax.invert_xaxis()
    
    def save_fig(self, filename, filetype='png', transparent=False, adjust=(None, None, None, None)):
        # Save figure
        adj_left = adjust[0] or self.adj_left
        adj_bottom = adjust[1] or self.adj_bottom
        adj_right = adjust[2] or self.adj_right
        adj_top = adjust[3] or self.adj_top
        plt.subplots_adjust(left=adj_left, bottom=adj_bottom, right=adj_right, top=adj_top)
        filename = f'{self.head_filename}_{filename}.{filetype}'
        plt.savefig(os.path.join(self.fig_folder, filename), format=filetype, dpi=600, transparent=transparent)
        print("\t%s saved" % filename)


def remove_edges(data, edges_removal):
    return data[edges_removal:-edges_removal] # on first dim when several
        

def cm2in(v_cm):
    return v_cm/2.54


def setstyle(stylename):

# see https://matplotlib.org/3.2.1/tutorials/introductory/customizing.html?highlight=figure.frameon#a-sample-matplotlibrc-file
    
    # Figure
    mpl.rcParams['figure.dpi'] = 150
    
    # Grid
    mpl.rcParams['axes.grid']=True
    mpl.rcParams['grid.linewidth']=1.
    mpl.rcParams['axes.grid.which']="major"
    # Note: There are no separate parameters for major/minor grid properties 
    # in rcParams, use ax.grid(b=True, which='minor', lw=0.3)
    
    # Default color list
    mpl.rcParams['axes.prop_cycle']=cycler('color', ['#1E6CA6', '#1EE31E', '#B21E1E',
                                                     '#81ADED', '#272727', '#E2720E',
                                                     '#52E0CB', '#ECE600', '#AD17F5',
                                                     '#E5639F'])

    # xtick
    mpl.rcParams['xtick.direction']='out'
    mpl.rcParams['xtick.bottom']=True
    mpl.rcParams['xtick.top']=True
    mpl.rcParams['xtick.major.size']=4
    mpl.rcParams['xtick.minor.size']=2
    mpl.rcParams['xtick.major.width']=0.8
    mpl.rcParams['xtick.minor.width']=0.6
    mpl.rcParams['xtick.minor.visible']=True

    # ytick
    mpl.rcParams['ytick.direction']='out'
    mpl.rcParams['ytick.left']=True
    mpl.rcParams['ytick.right']=True
    mpl.rcParams['ytick.major.size']=4
    mpl.rcParams['ytick.minor.size']=2
    mpl.rcParams['ytick.major.width']=0.8
    mpl.rcParams['ytick.minor.width']=0.6
    mpl.rcParams['ytick.minor.visible']=True

    # Colors    
    mpl.rcParams["axes.facecolor"]='1.'
    mpl.rcParams["axes.edgecolor"]='0.'
    mpl.rcParams['grid.color']='0.9'
    mpl.rcParams['xtick.color']='0.'
    mpl.rcParams['ytick.color']='0.'

    # Fontsize
    mpl.rcParams['font.size']=9
    mpl.rcParams['figure.titlesize']=10
    mpl.rcParams['axes.titlesize']=10
    mpl.rcParams['axes.labelsize']=9
    mpl.rcParams['legend.fontsize']=9
    mpl.rcParams['legend.title_fontsize']=9
    mpl.rcParams['xtick.labelsize']=9
    mpl.rcParams['ytick.labelsize']=9

    # Title pad
    mpl.rcParams['axes.titlepad']=8.
    
    # LaTeX Font
    # Use MathText instead: https://matplotlib.org/stable/tutorials/text/mathtext.html
    if False:
        mpl.rcParams['text.usetex']=True # LaTeX
        mpl.rcParams['text.latex.preamble'] = r'\usepackage{sansmath} \sansmath' 
                                          # use sans-serif for math (and ticklabel) 
    # ******************************************************************

    if stylename=='ticks_grid':
        mpl.rcParams['axes.grid']=True

    elif stylename=='ticks_nogrid':
        mpl.rcParams['axes.grid']=False

    return


def takecmap(cmapname, nb_colors=256, clight=0.95, cdark=0.05):

    d = {}

    # ******************************************************************
    name = "cubeh1"
    palette = sns.cubehelix_palette(nb_colors, start=2, rot=1, hue=1.,
                                    gamma=1., light=clight, dark=cdark)
    luma_palette = np.ones(len(palette))*-9999.
    for i in range(len(palette)):
        luma_palette[i] = np.sqrt(0.241*palette[i][0] + 0.691*palette[i][1] +\
                                  0.068*palette[i][2])
        # luma_palette[i] = 0.3*palette[i][0] + 0.59*palette[i][1] +\
        #                 0.11*palette[i][2]
    # Monotonically increasing perception of intensity
    luma_monoton = 1 - np.arange(256)/255.
    if False:
        plt.plot(luma_palette)
        plt.plot(luma_monoton, '--')
        plt.show()
        stop
    d[name] = mpl.colors.ListedColormap(palette)
    # Reverse
    name = name + "_r"
    d[name] = mpl.colors.ListedColormap(palette[::-1])

    # ******************************************************************
    name = "cubeh2"
    palette = sns.cubehelix_palette(nb_colors, start=1.5, rot=5, hue=1.,
                                    gamma=1., light=clight, dark=cdark)
    luma_palette = np.ones(len(palette))*-9999.
    for i in range(len(palette)):
        luma_palette[i] = np.sqrt(0.241*palette[i][0] + 0.691*palette[i][1] +\
                                  0.068*palette[i][2])
        # luma_palette[i] = 0.3*palette[i][0] + 0.59*palette[i][1] +\
        #                 0.11*palette[i][2]
    # Monotonically increasing perception of intensity
    luma_monoton = 1 - np.arange(256)/255.
    if False:
        plt.plot(luma_palette)
        plt.plot(luma_monoton, '--')
        plt.show()
        stop
    d[name] = mpl.colors.ListedColormap(palette)
    # Reverse
    name = name + "_r"
    d[name] = mpl.colors.ListedColormap(palette[::-1])

    # ******************************************************************
    name = "extviridis" # extended viridis to almost black and almost white
    cmap = mpl.cm.viridis
    palette = cmap(range(256))
    # Palette of black colors
    n = 70
    r = np.linspace(0., palette[0][0], n)
    g = np.linspace(0., palette[0][1], n)
    b = np.linspace(0., palette[0][2], n)
    palette_k = [(r[i], g[i], b[i], 1.) for i in range(n)]
    # Palette of white colors
    n = 70
    r = np.linspace(palette[-1][0], 1., n)
    g = np.linspace(palette[-1][1], 1., n)
    b = np.linspace(palette[-1][2], 1., n)
    palette_w = [(r[i], g[i], b[i], 1.) for i in range(n)]
    # New palette with extended black and white
    palette = np.concatenate((palette_k[30:-1], palette, palette_w[1:-10]))
        #-1 1 because color already in initial colormap
        # 20 -10 because we don't want to go until black or white
    # Nb of colors to take in the new palette
    color_index = np.round(np.linspace(0, palette.shape[0]-1, nb_colors))\
                                                                   .astype(int)
    palette = palette[color_index]
    luma_palette = np.ones(palette.shape[0])*-9999.
    for i in range(palette.shape[0]):
        luma_palette[i] = np.sqrt(0.241*palette[i][0] + 0.691*palette[i][1] +\
                                  0.068*palette[i][2])
        # luma_palette[i] = 0.3*palette[i][0] + 0.59*palette[i][1] +\
        #                 0.11*palette[i][2]
    # Monotonically increasing perception of intensity
    luma_monoton = np.arange(256)/255.
    if False:
        plt.plot(luma_palette)
        plt.plot(luma_monoton)
        plt.plot(np.array((0, 255)), np.array((1, 1)), color='k', ls='--')
        plt.plot(np.array((0, 255)), np.array((0, 0)), color='k', ls='--')
        plt.show()
        stop
    d[name] = mpl.colors.ListedColormap(palette)
    # Reverse
    name = name + "_r"
    d[name] = mpl.colors.ListedColormap(palette[::-1])

    # ******************************************************************
    name = "extviridis_black_white" # extended viridis to black and white
    cmap = mpl.cm.viridis
    palette = cmap(range(256))
    # Palette of black colors
    n = 30
    r = np.linspace(0., palette[0][0], n)
    g = np.linspace(0., palette[0][1], n)
    b = np.linspace(0., palette[0][2], n)
    palette_k = [(r[i], g[i], b[i], 1.) for i in range(n)]
    # Palette of white colors
    n = 70
    r = np.linspace(palette[-1][0], 1., n)
    g = np.linspace(palette[-1][1], 1., n)
    b = np.linspace(palette[-1][2], 1., n)
    palette_w = [(r[i], g[i], b[i], 1.) for i in range(n)]
    # New palette with extended black and white
    palette = np.concatenate((palette_k[0:-1], palette, palette_w[1:-1]))
        #-1 1 because color already in initial colormap
        # 0 -1 because we want to go until black or white
    # Nb of colors to take in the new palette
    color_index = np.round(np.linspace(0, palette.shape[0]-1, nb_colors))\
                                                                   .astype(int)
    palette = palette[color_index]
    luma_palette = np.ones(palette.shape[0])*-9999.
    for i in range(palette.shape[0]):
        luma_palette[i] = np.sqrt(0.241*palette[i][0] + 0.691*palette[i][1] +\
                                  0.068*palette[i][2])
        # luma_palette[i] = 0.3*palette[i][0] + 0.59*palette[i][1] +\
        #                 0.11*palette[i][2]
    # Monotonically increasing perception of intensity
    luma_monoton = np.arange(256)/255.
    if False:
        plt.plot(luma_palette)
        plt.plot(luma_monoton)
        plt.plot(np.array((0, 255)), np.array((1, 1)), color='k', ls='--')
        plt.plot(np.array((0, 255)), np.array((0, 0)), color='k', ls='--')
        plt.show()
        stop
    d[name] = mpl.colors.ListedColormap(palette)
    # Reverse
    name = name + "_r"
    d[name] = mpl.colors.ListedColormap(palette[::-1])
    

    # ******************************************************************
    name = "caliop" # 33 colors (over 1e-1 removed, added with '_both')
        # Bounds
        # b1 = np.arange(1, 9+.01, 1)*1e-4
        # b2 = np.arange(1, 8+.01, 0.5)*1e-3
        # b3 = np.arange(1, 9+.01, 1)*1e-2
        # b4 = np.array((1e-1,))
        # bounds = np.concatenate((b1, b2, b3, b4))
    palette = np.array([[  1/255.,   1/255.,   1/255.],
                        [  0/255.,  42/255., 170/255.],
                        [  0/255., 127/255., 255/255.],
                        [  0/255., 170/255., 255/255.],
                        [  0/255., 212/255., 255/255.],
                        [  0/255., 255/255., 255/255.],
                        [  0/255., 255/255., 212/255.],
                        [  0/255., 255/255., 170/255.],
                        [  0/255., 127/255., 127/255.],
                        [  0/255., 170/255.,  85/255.],
                        [255/255., 255/255.,   0/255.],
                        [255/255., 255/255.,   0/255.],
                        [255/255., 212/255.,   0/255.],
                        [255/255., 170/255.,   0/255.],
                        [255/255., 127/255.,   0/255.],
                        [255/255.,  85/255.,   0/255.],
                        [255/255.,   0/255.,   0/255.],
                        [255/255.,  42/255.,  85/255.],
                        [255/255.,  85/255., 127/255.],
                        [255/255., 127/255., 170/255.],
                        [ 70/255.,  70/255.,  70/255.],
                        [100/255., 100/255., 100/255.],
                        [130/255., 130/255., 130/255.],
                        [155/255., 155/255., 155/255.],
                        [180/255., 180/255., 180/255.],
                        [200/255., 200/255., 200/255.],
                        [225/255., 225/255., 225/255.],
                        [235/255., 235/255., 235/255.],
                        [240/255., 240/255., 240/255.],
                        [242/255., 242/255., 242/255.],
                        [245/255., 245/255., 245/255.],
                        [249/255., 249/255., 249/255.],
                        [253/255., 253/255., 253/255.]])
    if cmapname == "caliop":
        # Nb of colors to take in the new palette
        color_index = np.round(np.linspace(0, len(palette)-1, nb_colors))\
                      .astype(int)
        palette = palette[color_index]
        d[name] = mpl.colors.ListedColormap(palette)
        # Reverse
        name = name + "_r"
        d[name] = mpl.colors.ListedColormap(palette[::-1])

    # ******************************************************************
    name = "caliop_both" # 35 colors, 2 more colors at both edges
    palette = np.vstack(([0,  0, 0], palette))
    palette = np.vstack((palette, [1, 1, 1]))
    # Nb of colors to take in the new palette
    color_index = np.round(np.linspace(0, len(palette)-1, nb_colors))\
                                                                   .astype(int)
    palette = palette[color_index]
    d[name] = mpl.colors.ListedColormap(palette)
    # Reverse
    name = name + "_r"
    d[name] = mpl.colors.ListedColormap(palette[::-1])


    # ******************************************************************
    name = "caliop_browse" # 33 colors (over 1e-1 removed, added with '_both')
    # As in the lidar browse images
        # Bounds
        # b1 = np.arange(1, 9+.01, 1)*1e-4
        # b2 = np.arange(1, 8+.01, 0.5)*1e-3
        # b3 = np.arange(1, 9+.01, 1)*1e-2
        # b4 = np.array((1e-1,))
        # bounds = np.concatenate((b1, b2, b3, b4))
    palette =  ['#062EA6',
                '#062EA6',
                '#127EFB',
                '#127EFB',
                '#127EFB',
                '#127EFB',
                '#127EFB',
                '#19FEAA',
                '#087D7D',
                '#0CA858',
                '#FFFF39',
                '#FFFF39',
                '#FFD333',
                '#FEAA2E',
                '#FE802A',
                '#FE5A27',
                '#FE2025',
                '#FE365A',
                '#FE5A80',
                '#FE80A9',
                '#484848',
                '#646464',
                '#818181',
                '#9A9A9A',
                '#B3B3B3',
                '#C7C7C7',
                '#E0E0E0',
                '#EAEAEA',
                '#F0F0F0',
                '#F2F2F2',
                '#F5F5F5',
                '#F9F9F9',
                '#FDFDFD']
    if cmapname == "caliop_browse":
        # Nb of colors to take in the new palette
        color_index = np.round(np.linspace(0, len(palette)-1, nb_colors))\
                                                                       .astype(int)
        palette = [palette[i] for i in color_index]
        d[name] = mpl.colors.ListedColormap(palette)
        # Reverse
        name = name + "_r"
        d[name] = mpl.colors.ListedColormap(palette[::-1])

    # ******************************************************************
    name = "caliop_browse_both" # 35 colors, 2 more colors (same) at both edges
    palette.insert(0, palette[0])
    palette.append('#FFFFFF')
    # Nb of colors to take in the new palette
    color_index = np.round(np.linspace(0, len(palette)-1, nb_colors))\
                                                                   .astype(int)
    palette = [palette[i] for i in color_index]
    d[name] = mpl.colors.ListedColormap(palette)
    # Reverse
    name = name + "_r"
    d[name] = mpl.colors.ListedColormap(palette[::-1])


    # ******************************************************************
    name = "caliop_browse_colorblind" # 33 colors (over 1e-1 removed, added with '_both')
    # As in the lidar browse images
        # Bounds
        # b1 = np.arange(1, 9+.01, 1)*1e-4
        # b2 = np.arange(1, 8+.01, 0.5)*1e-3
        # b3 = np.arange(1, 9+.01, 1)*1e-2
        # b4 = np.array((1e-1,))
        # bounds = np.concatenate((b1, b2, b3, b4))
    palette =  ["#062EA6",
                "#0838B1",
                "#0942BC",
                "#0B4CC7",
                "#0C56D1",
                "#0E60DC",
                "#0F6AE6",
                "#1174F1",
                "#127EFB",#
                "#fff437",
                "#ffe035",
                "#ffcf33",
                "#ffbf31",
                "#ffb02f",
                "#ffa22e",
                "#ff902c",
                "#ff7c2a",
                "#ff6628",
                "#ff4c27",
                "#fe2025",#
                '#484848',
                '#646464',
                '#818181',
                '#9A9A9A',
                '#B3B3B3',
                '#C7C7C7',
                '#E0E0E0',
                '#EAEAEA',
                '#F0F0F0',
                '#F2F2F2',
                '#F5F5F5',
                '#F9F9F9',
                '#FDFDFD']
    if cmapname == "caliop_browse_colorblind":
        # Nb of colors to take in the new palette
        color_index = np.round(np.linspace(0, len(palette)-1, nb_colors))\
                                                                       .astype(int)
        palette = [palette[i] for i in color_index]
        d[name] = mpl.colors.ListedColormap(palette)
        # Reverse
        name = name + "_r"
        d[name] = mpl.colors.ListedColormap(palette[::-1])

    # ******************************************************************
    name = "caliop_browse_colorblind_both" # 35 colors, 2 more colors (same) at both edges
    palette.insert(0, palette[0])
    palette.append("#FFFFFF")
    # Nb of colors to take in the new palette
    color_index = np.round(np.linspace(0, len(palette)-1, nb_colors))\
                                                                   .astype(int)
    palette = [palette[i] for i in color_index]
    d[name] = mpl.colors.ListedColormap(palette)
    # Reverse
    name = name + "_r"
    d[name] = mpl.colors.ListedColormap(palette[::-1])


    # ******************************************************************
    # Not great... do not use
    name = "caliop_browse_colorblind_lin" # 33 colors (over 1e-1 removed, added with '_both')
    # As in the lidar browse images
        # Bounds
        # b1 = np.arange(1, 9+.01, 1)*1e-4
        # b2 = np.arange(1, 8+.01, 0.5)*1e-3
        # b3 = np.arange(1, 9+.01, 1)*1e-2
        # b4 = np.array((1e-1,))
        # bounds = np.concatenate((b1, b2, b3, b4))
    greys = np.linspace(189./255, 255./255, 14)
    palette =  ["#08306b",
                "#0f3f7c",
                "#154d8d",
                "#1a5b9d",
                "#1f69ad",
                "#2377bc",
                "#2784ca",
                "#2a92da",
                "#2fa2ec",#
                "#fc4e2a",
                "#fe6730",
                "#ff7b37",
                "#ff8d3d",
                "#ff9c43",
                "#feaa49",
                "#feb84e",
                "#fcc655",
                "#fad35b",
                "#f8de60",
                "#f6ea65",#
                [greys[0], greys[0], greys[0]],
                [greys[1], greys[1], greys[1]],
                [greys[2], greys[2], greys[2]],
                [greys[3], greys[3], greys[3]],
                [greys[4], greys[4], greys[4]],
                [greys[5], greys[5], greys[5]],
                [greys[6], greys[6], greys[6]],
                [greys[7], greys[7], greys[7]],
                [greys[8], greys[8], greys[8]],
                [greys[9], greys[9], greys[9]],
                [greys[10], greys[10], greys[10]],
                [greys[11], greys[11], greys[11]],
                [greys[12], greys[12], greys[12]]]
    if cmapname == "caliop_browse_colorblind_lin":
        # Nb of colors to take in the new palette
        color_index = np.round(np.linspace(0, len(palette)-1, nb_colors))\
                                                                       .astype(int)
        palette = [palette[i] for i in color_index]
        d[name] = mpl.colors.ListedColormap(palette)
        # Reverse
        name = name + "_r"
        d[name] = mpl.colors.ListedColormap(palette[::-1])

    # ******************************************************************
    name = "caliop_browse_colorblind_lin_both" # 35 colors, 2 more colors (same) at both edges
    palette.insert(0, palette[0])
    palette.append([greys[13], greys[13], greys[13]])
    # Nb of colors to take in the new palette
    color_index = np.round(np.linspace(0, len(palette)-1, nb_colors))\
                                                                   .astype(int)
    palette = [palette[i] for i in color_index]
    d[name] = mpl.colors.ListedColormap(palette)
    # Reverse
    name = name + "_r"
    d[name] = mpl.colors.ListedColormap(palette[::-1])


    # ******************************************************************
    name = "caliop_colorblind" # 27 colors
        # Bounds
        # b1 = np.arange(1, 9+.01, 1)*1e-4
        # b2 = np.arange(1, 9+.01, 1)*1e-3
        # b3 = np.arange(1, 9+.01, 1)*1e-2
        # b4 = np.array((1e-1,))
        # bounds = np.concatenate((b1, b2, b3, b4))
    greys = np.linspace(0.15, 1, 10)
    palette = np.array([[ 31/255.,  32/255., 107/255.],
                        [ 51/255.,  52/255., 125/255.],
                        [ 67/255.,  71/255., 142/255.],
                        [ 82/255.,  89/255., 157/255.],
                        [ 95/255., 106/255., 171/255.],
                        [108/255., 123/255., 186/255.],
                        [121/255., 141/255., 200/255.],
                        [135/255., 161/255., 217/255.],
                        [151/255., 183/255., 235/255.],#
                        [252/255., 255/255., 112/255.],
                        [250/255., 227/255.,  96/255.],
                        [247/255., 201/255.,  81/255.],
                        [243/255., 175/255.,  67/255.],
                        [238/255., 150/255.,  54/255.],
                        [231/255., 123/255.,  40/255.],
                        [224/255.,  96/255.,  28/255.],
                        [216/255.,  65/255.,  15/255.],
                        [206/255.,   0/255.,   3/255.],#
                        [greys[0], greys[0], greys[0]],
                        [greys[1], greys[1], greys[1]],
                        [greys[2], greys[2], greys[2]],
                        [greys[3], greys[3], greys[3]],
                        [greys[4], greys[4], greys[4]],
                        [greys[5], greys[5], greys[5]],
                        [greys[6], greys[6], greys[6]],
                        [greys[7], greys[7], greys[7]],
                        [greys[8], greys[8], greys[8]]])
    if cmapname == "caliop_colorblind":
        # Nb of colors to take in the new palette
        color_index = np.round(np.linspace(0, len(palette)-1, nb_colors))\
                                                                       .astype(int)
        palette = palette[color_index]
        d[name] = mpl.colors.ListedColormap(palette)
        # Reverse
        name = name + "_r"
        d[name] = mpl.colors.ListedColormap(palette[::-1])

    # ******************************************************************
    name = "caliop_colorblind_both" # 29 colors, 2 more colors at both edges
    palette = np.vstack(([ 24/255.,  23/255.,  81/255.], palette))
    palette = np.vstack((palette, [1, 1, 1]))
    # Nb of colors to take in the new palette
    color_index = np.round(np.linspace(0, len(palette)-1, nb_colors))\
                                                                   .astype(int)
    palette = palette[color_index]
    d[name] = mpl.colors.ListedColormap(palette)
    # Reverse
    name = name + "_r"
    d[name] = mpl.colors.ListedColormap(palette[::-1])


    # ******************************************************************
    name = "caliop_browse_acr" # 16 colors
    # As in the lidar browse images
        # Bounds
        # bounds = np.arange(0, 1.61, 0.1) + extremes
    palette =  ["#16A8FC",
                "#12D226",
                "#FFFF39",
                "#FEAA2E",
                "#FE2025",
                "#FE20FC",
                "#FFD3FE",
                "#A857FC",
                "#7E0CA6",
                "#A8157D",
                "#A9D2FD",
                "#A9FEFE",
                "#A9FED4",
                "#D3FFD4",
                "#FFFFD5",
                "#FFFFFF"]
    if cmapname == "caliop_browse_acr":
        # Nb of colors to take in the new palette
        color_index = np.round(np.linspace(0, len(palette)-1, nb_colors))\
                                                                       .astype(int)
        palette = [palette[i] for i in color_index]
        d[name] = mpl.colors.ListedColormap(palette)
        # Reverse
        name = name + "_r"
        d[name] = mpl.colors.ListedColormap(palette[::-1])

    # ******************************************************************
    name = "caliop_browse_acr_both"
    palette.insert(0, "#000000")
    palette.append("#9A9A9A")
    # Nb of colors to take in the new palette
    color_index = np.round(np.linspace(0, len(palette)-1, nb_colors))\
                                                                   .astype(int)
    palette = [palette[i] for i in color_index]
    d[name] = mpl.colors.ListedColormap(palette)
    # Reverse
    name = name + "_r"
    d[name] = mpl.colors.ListedColormap(palette[::-1])


    # ******************************************************************
    name = "caliop_browse_depol" # 12 colors
    # As in the lidar browse images
        # Bounds
        # bounds = np.arange(0, 1., 0.1) + extremes
    palette =  ["#16A8FC",
                "#12D226",
                "#FFFF39",
                "#FEAA2E",
                "#FE2025",
                "#FE20FC",
                "#FFD3FE",
                "#A857FC",
                "#FFFFFF",
                "#FFFFFF"]
    if cmapname == "caliop_browse_depol":
        # Nb of colors to take in the new palette
        color_index = np.round(np.linspace(0, len(palette)-1, nb_colors))\
                                                                       .astype(int)
        palette = [palette[i] for i in color_index]
        d[name] = mpl.colors.ListedColormap(palette)
        # Reverse
        name = name + "_r"
        d[name] = mpl.colors.ListedColormap(palette[::-1])

    # ******************************************************************
    name = "caliop_browse_depol_both"
    palette.insert(0, "#000000")
    palette.append("#FFFFFF")
    # Nb of colors to take in the new palette
    color_index = np.round(np.linspace(0, len(palette)-1, nb_colors))\
                                                                   .astype(int)
    palette = [palette[i] for i in color_index]
    d[name] = mpl.colors.ListedColormap(palette)
    # Reverse
    name = name + "_r"
    d[name] = mpl.colors.ListedColormap(palette[::-1])

    return d[cmapname]


# Formatter for interactive_pixel_info()
class Formatter(object):
    def __init__(self, yarray, xarray, zarray):
        self.yar = yarray
        self.xar = xarray
    def __call__(self, xm, ym):
        xi = (np.abs(self.xar - xm)).argmin() # nearest index in x-axis for xm
        yi = (np.abs(self.yar - ym)).argmin() # nearest index in y-axis for ym
        x = self.xar[xi]
        y = self.yar[yi]
        z = np.ma.ones(1)*-9999. # mask array to detect mask or nan
        z[0] = zarray.T[xi, yi] 
        if z.mask[0]: # if data masked
            message = 'x={:g}, y={:g}, z=--'.format(x, y)
        else:
            message = 'x={:g}, y={:g}, z={:g}'.format(x, y, z[0])
        return message

def interactive_pixel_info(ax, yarray, xarray, zarray):
    """Does not work"""
    ax.format_coord = Formatter(yarray, xarray, zarray)

    plt.show()
    sys.exit("End of intactive pixel information")

    return


def compute_bounds(x, l0):
    """Compute bounds vector of a vector of linear mid coords
    l0: width of the first interval
    """
    interval_widths = np.ones(x.size)*-9999.
    interval_widths[0] = l0
    for i in np.arange(interval_widths.size-1)+1:
        interval_widths[i] = 2*(x[i] - x[i-1]) - interval_widths[i-1]

    xb = np.ones(x.size+1)*-9999.
    xb[0] = x[0] - 0.5*l0
    xb[1:] = x + 0.5*interval_widths

    return xb

def get_midbins(bins):
    """ Get a vector of the mid of bins """

    midbins = (bins[1:] + bins[:-1]) / 2.

    return midbins

def lat_lon_dist_xaxis(ax, lat, lon, pindex, pindexbins, flag_lat_lon_label=True, flag_dist=True,
                       flag_dist_label=True, one_bin_dist=0.333,
                       dist_labelsize=6, dist_tick_labelsize=6):
    # Lat/Lon x-axis
    ax.xaxis.set_tick_params(which='minor', bottom=False) # do not work, I don't understand why
    x_ticks = np.linspace(0, pindex.size - 1, 6, dtype=int)
    # plt.xticks([pindex[x] for x in x_ticks],
    #            ['%.2f\n%.2f' % (lat[x], lon[x]) for x in x_ticks])
    lat_ticks = []
    lon_ticks = []
    for x in x_ticks:
        latx = '%.2f° S' % np.abs(lat[x]) if lat[x] < 0 else '%.2f° N' % lat[x]
        lonx = '%.2f° W' % np.abs(lon[x]) if lon[x] < 0 else '%.2f° E' % lon[x]
        lat_ticks.append(latx)
        lon_ticks.append(lonx)
    plt.xticks([pindex[x] for x in x_ticks],
               ['%s\n%s' % (lat_ticks[i], lon_ticks[i]) for i in range(len(lat_ticks))])
    plt.xlim(pindexbins[0], pindexbins[-1])
    plt.tick_params(axis='x', which='minor', bottom=False)
    # if flag_lat_lon_label:
    #     ax.text(1.1, -0.085, 'Latitude\nLongitude', ha='left', va='top',
    #             transform=ax.transAxes)
    if not flag_lat_lon_label:
        # Don't show labels
        ax.set_xticklabels([])
        plt.xlabel('')

    # Add distance in km on the top of the figure
    if flag_dist:
        total_dist = geo_distance(lat[0], lon[0], lat[-1], lon[-1])
        ax_dist = ax.twiny()
        plt.xlim(0, total_dist + one_bin_dist)
        plt.xlabel('Distance (km)', fontsize=dist_labelsize)
        ax_dist.xaxis.set_tick_params(labelsize=dist_tick_labelsize)
        if not flag_dist_label:
            # Don't show labels
            ax_dist.set_xticklabels([])
            plt.xlabel('')

    return

if __name__ == '__main__':
    
    x = np.arange(6)
    y = np.arange(4)
    a = np.arange(24).reshape(6,4)
    ax = plt.subplot(111)
    plt.pcolormesh(x, y, a.T)
    plt.colorbar()
    plt.show()
    
    
    # import matplotlib
    # print(matplotlib.__version__)
    #
    # my_cmap = mpl.cm.viridis
    # bounds = np.arange(10)
    # nb_colors = len(bounds) + 1
    # colors = my_cmap(np.linspace(100, 255, nb_colors).astype(int))
    # my_cmap, my_norm = from_levels_and_colors(bounds, colors, extend='both')
    #
    # plt.figure(figsize=(5, 1))
    # ax = plt.subplot(111)
    # cbar = mpl.colorbar.ColorbarBase(ax, cmap=my_cmap, norm=my_norm, orientation='horizontal',
    #                                  drawedges=True)
    # plt.axvline(max(bounds), color='k', linewidth=1.5) # add missing edges at the edge (bug of colorbar)
    # plt.axvline(min(bounds), color='k', linewidth=1.5) # add missing edges at the edge (bug of colorbar)
    # plt.subplots_adjust(left=0.05, bottom=0.4, right=0.95, top=0.9)
    # plt.show()
    