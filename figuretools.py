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

    if cmapname == "cubeh1" or cmapname == "cubeh1_r":
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
        if cmapname[-2:] == "_r":
            palette = palette[::-1]

    elif cmapname == "cubeh2" or cmapname == "cubeh2_r":
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
        if cmapname[-2:] == "_r":
            palette = palette[::-1]

    elif cmapname == "extviridis" or cmapname == "extviridis_r": # extended viridis to almost black and almost white
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
        if cmapname[-2:] == "_r":
            palette = palette[::-1]

    elif cmapname == "extviridis_black_white" or cmapname == "extviridis_black_white_r": # extended viridis to black and white
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
        if cmapname[-2:] == "_r":
            palette = palette[::-1]
    
    elif cmapname ==  "caliop" # 33 colors (over 1e-1 removed, added with '_both')
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
        # Nb of colors to take in the new palette
        color_index = np.round(np.linspace(0, len(palette)-1, nb_colors)).astype(int)
        palette = palette[color_index]

    elif cmapname == "caliop_both" # 35 colors, 2 more colors at both edges
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
        # Nb of colors to take in the new palette
        color_index = np.round(np.linspace(0, len(palette)-1, nb_colors)).astype(int)
        palette = palette[color_index]
        palette = np.vstack(([0,  0, 0], palette))
        palette = np.vstack((palette, [1, 1, 1]))
        # Nb of colors to take in the new palette
        color_index = np.round(np.linspace(0, len(palette)-1, nb_colors))\
                                                                    .astype(int)
        palette = palette[color_index]

    elif cmapname == "caliop_browse" # 33 colors (over 1e-1 removed, added with '_both')
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
        color_index = np.round(np.linspace(0, len(palette)-1, nb_colors))\.astype(int)
        palette = [palette[i] for i in color_index]

    elif cmapname == "caliop_browse_both" # 35 colors, 2 more colors (same) at both edges
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
        color_index = np.round(np.linspace(0, len(palette)-1, nb_colors)).astype(int)
        palette = [palette[i] for i in color_index]
        palette.insert(0, palette[0])
        palette.append('#FFFFFF')
        # Nb of colors to take in the new palette
        color_index = np.round(np.linspace(0, len(palette)-1, nb_colors)).astype(int)
        palette = [palette[i] for i in color_index]

    elif cmapname == "thermal" or cmapname == "thermal_r": # thermal from cmocean
        palette =  [[ 0.01555601, 0.13824425, 0.20181089],
                    [ 0.01620184, 0.14105074, 0.20897651],
                    [ 0.01685649, 0.14382701, 0.21623868],
                    [ 0.0175264 , 0.14657173, 0.2235997 ],
                    [ 0.01821872, 0.14928346, 0.23106187],
                    [ 0.01894138, 0.15196073, 0.23862748],
                    [ 0.01969968, 0.15460145, 0.24630497],
                    [ 0.02050332, 0.15720378, 0.25409711],
                    [ 0.02136721, 0.15976645, 0.26199915],
                    [ 0.02230341, 0.16228755, 0.27001321],
                    [ 0.0233252 , 0.16476505, 0.27814139],
                    [ 0.02444728, 0.16719678, 0.28638573],
                    [ 0.02568582, 0.16958042, 0.29474817],
                    [ 0.02705867, 0.1719135 , 0.30323056],
                    [ 0.02858553, 0.17419338, 0.31183463],
                    [ 0.03028808, 0.17641726, 0.32056191],
                    [ 0.03219022, 0.17858215, 0.32941369],
                    [ 0.03431826, 0.18068487, 0.33839101],
                    [ 0.03670118, 0.18272205, 0.34749451],
                    [ 0.03937082, 0.18469014, 0.35672441],
                    [ 0.04230474, 0.18658537, 0.36608039],
                    [ 0.04544128, 0.1884038 , 0.37556146],
                    [ 0.04879889, 0.1901413 , 0.38516584],
                    [ 0.05238565, 0.19179358, 0.39489082],
                    [ 0.05620897, 0.19335621, 0.40473254],
                    [ 0.06027561, 0.19482469, 0.41468582],
                    [ 0.06459519, 0.19618775, 0.42477146],
                    [ 0.06917294, 0.19744583, 0.43495728],
                    [ 0.07401398, 0.19859437, 0.44523225],
                    [ 0.07912633, 0.19962514, 0.45559656],
                    [ 0.08452075, 0.20052842, 0.46605087],
                    [ 0.09019392, 0.20130794, 0.47654788],
                    [ 0.09616431, 0.20194725, 0.48710445],
                    [ 0.1024254 , 0.20245202, 0.49766462],
                    [ 0.10899443, 0.20280889, 0.50822709],
                    [ 0.11585974, 0.20302735, 0.51872453],
                    [ 0.12304243, 0.2030938 , 0.52914838],
                    [ 0.13052767, 0.20302178, 0.53942012],
                    [ 0.13830991, 0.20281956, 0.54947678],
                    [ 0.14637971, 0.20250018, 0.55924613],
                    [ 0.15471863, 0.20208507, 0.56864226],
                    [ 0.16329705, 0.20160546, 0.57756769],
                    [ 0.17207282, 0.20110273, 0.58591838],
                    [ 0.18099176, 0.20062705, 0.59359182],
                    [ 0.18999022, 0.20023416, 0.60049707],
                    [ 0.19899974, 0.19998029, 0.60656515],
                    [ 0.20795298, 0.19991643, 0.61175706],
                    [ 0.21678952, 0.20008303, 0.61606739],
                    [ 0.22546043, 0.20050671, 0.61952279],
                    [ 0.23393063, 0.2011992 , 0.62217608],
                    [ 0.24217907, 0.20215872, 0.62409793],
                    [ 0.25019713, 0.20337273, 0.62536824],
                    [ 0.25798611, 0.20482134, 0.62606879],
                    [ 0.26555442, 0.20648047, 0.62627797],
                    [ 0.27291504, 0.20832446, 0.62606758],
                    [ 0.28008339, 0.21032792, 0.62550133],
                    [ 0.28706751, 0.21246914, 0.624642  ],
                    [ 0.29388514, 0.21472543, 0.62353802],
                    [ 0.30055772, 0.21707565, 0.62222519],
                    [ 0.30708438, 0.21950598, 0.6207555 ],
                    [ 0.31349163, 0.22199831, 0.61914522],
                    [ 0.31977984, 0.22454204, 0.61743434],
                    [ 0.32596955, 0.22712412, 0.61563293],
                    [ 0.33205791, 0.22973736, 0.61377715],
                    [ 0.33806601, 0.23237153, 0.61186606],
                    [ 0.34399174, 0.23502151, 0.60992807],
                    [ 0.34984607, 0.23768089, 0.60796949],
                    [ 0.35563846, 0.2403444 , 0.60599535],
                    [ 0.36136863, 0.24300892, 0.60402414],
                    [ 0.36704345, 0.24567078, 0.60206076],
                    [ 0.37267088, 0.2483267 , 0.60010594],
                    [ 0.3782548 , 0.25097436, 0.59816563],
                    [ 0.38379608, 0.25361228, 0.59624988],
                    [ 0.38929883, 0.25623877, 0.5943618 ],
                    [ 0.3947691 , 0.25885207, 0.59249964],
                    [ 0.40020989, 0.26145107, 0.59066609],
                    [ 0.40562409, 0.26403484, 0.58886331],
                    [ 0.41101442, 0.26660262, 0.58709291],
                    [ 0.41638322, 0.26915383, 0.5853566 ],
                    [ 0.42173132, 0.27168825, 0.58365836],
                    [ 0.42706343, 0.27420503, 0.5819941 ],
                    [ 0.43238181, 0.2767038 , 0.58036393],
                    [ 0.43768862, 0.27918426, 0.57876764],
                    [ 0.44298597, 0.28164615, 0.5772048 ],
                    [ 0.44827587, 0.28408925, 0.57567472],
                    [ 0.45356026, 0.28651338, 0.57417648],
                    [ 0.45884104, 0.28891838, 0.57270899],
                    [ 0.46412001, 0.2913041 , 0.57127095],
                    [ 0.46939893, 0.29367044, 0.5698609 ],
                    [ 0.47467951, 0.29601729, 0.56847725],
                    [ 0.47996336, 0.29834456, 0.56711823],
                    [ 0.48525207, 0.30065217, 0.56578195],
                    [ 0.49054716, 0.30294008, 0.5644664 ],
                    [ 0.49585007, 0.30520822, 0.56316946],
                    [ 0.50116221, 0.30745656, 0.56188888],
                    [ 0.50648491, 0.30968508, 0.56062233],
                    [ 0.51181943, 0.31189376, 0.55936737],
                    [ 0.51716699, 0.31408263, 0.55812148],
                    [ 0.52252871, 0.31625172, 0.55688205],
                    [ 0.52790567, 0.31840106, 0.55564642],
                    [ 0.53329886, 0.32053073, 0.55441182],
                    [ 0.5387092 , 0.32264084, 0.55317546],
                    [ 0.54413753, 0.3247315 , 0.55193448],
                    [ 0.54958461, 0.32680287, 0.55068596],
                    [ 0.55505113, 0.32885514, 0.54942696],
                    [ 0.56053768, 0.33088852, 0.54815451],
                    [ 0.56604476, 0.33290327, 0.54686563],
                    [ 0.57157236, 0.33489987, 0.54555812],
                    [ 0.57712131, 0.33687845, 0.54422801],
                    [ 0.58269186, 0.33883938, 0.54287227],
                    [ 0.58828416, 0.34078308, 0.54148789],
                    [ 0.59389827, 0.34271002, 0.54007187],
                    [ 0.59953415, 0.34462069, 0.53862124],
                    [ 0.60519167, 0.34651565, 0.53713308],
                    [ 0.61087061, 0.34839552, 0.5356045 ],
                    [ 0.61657065, 0.35026093, 0.53403268],
                    [ 0.62229138, 0.3521126 , 0.53241484],
                    [ 0.62803229, 0.35395127, 0.53074831],
                    [ 0.63379279, 0.35577776, 0.52903045],
                    [ 0.63957219, 0.35759292, 0.52725878],
                    [ 0.64536975, 0.35939765, 0.52543076],
                    [ 0.6511847 , 0.36119285, 0.52354391],
                    [ 0.6570161 , 0.36297956, 0.52159597],
                    [ 0.66286293, 0.36475881, 0.51958481],
                    [ 0.6687241 , 0.36653173, 0.51750839],
                    [ 0.67459845, 0.36829947, 0.5153648 ],
                    [ 0.68048472, 0.37006325, 0.51315222],
                    [ 0.68638162, 0.37182432, 0.51086898],
                    [ 0.69228775, 0.37358401, 0.50851352],
                    [ 0.69820166, 0.37534367, 0.50608439],
                    [ 0.70412186, 0.37710473, 0.50358028],
                    [ 0.71004688, 0.37886859, 0.50099965],
                    [ 0.71597525, 0.3806367 , 0.49834106],
                    [ 0.72190503, 0.38241075, 0.4956041 ],
                    [ 0.72783443, 0.38419239, 0.49278795],
                    [ 0.73376164, 0.3859833 , 0.4898919 ],
                    [ 0.73968475, 0.38778523, 0.48691538],
                    [ 0.7456018 , 0.38960001, 0.48385794],
                    [ 0.75151077, 0.39142951, 0.48071927],
                    [ 0.75740957, 0.39327566, 0.47749914],
                    [ 0.76329604, 0.39514048, 0.4741975 ],
                    [ 0.76916794, 0.39702603, 0.47081439],
                    [ 0.77502298, 0.39893446, 0.46735   ],
                    [ 0.78085877, 0.400868  , 0.46380463],
                    [ 0.78667286, 0.40282892, 0.46017874],
                    [ 0.79246271, 0.4048196 , 0.45647292],
                    [ 0.79822569, 0.40684249, 0.45268792],
                    [ 0.80395908, 0.40890011, 0.44882462],
                    [ 0.80966007, 0.41099506, 0.44488409],
                    [ 0.81532584, 0.41313001, 0.4408672 ],
                    [ 0.82095338, 0.41530771, 0.43677537],
                    [ 0.82653946, 0.41753108, 0.43261066],
                    [ 0.83208085, 0.41980305, 0.42837489],
                    [ 0.83757423, 0.42212661, 0.42407011],
                    [ 0.84301618, 0.42450482, 0.4196986 ],
                    [ 0.84840316, 0.42694082, 0.41526288],
                    [ 0.85373155, 0.4294378 , 0.41076573],
                    [ 0.8589976 , 0.43199897, 0.40621024],
                    [ 0.8641975 , 0.4346276 , 0.40159975],
                    [ 0.86932733, 0.43732696, 0.39693796],
                    [ 0.87438311, 0.44010033, 0.39222887],
                    [ 0.87936081, 0.44295096, 0.38747682],
                    [ 0.88425632, 0.44588207, 0.38268654],
                    [ 0.88906554, 0.44889681, 0.37786308],
                    [ 0.89378437, 0.45199824, 0.3730116 ],
                    [ 0.89840867, 0.45518929, 0.36813827],
                    [ 0.90293439, 0.45847274, 0.36324942],
                    [ 0.90735756, 0.46185117, 0.35835166],
                    [ 0.91167433, 0.46532694, 0.35345197],
                    [ 0.915881  , 0.46890217, 0.34855767],
                    [ 0.91997406, 0.47257868, 0.34367638],
                    [ 0.92395023, 0.47635796, 0.33881601],
                    [ 0.92780648, 0.48024117, 0.33398471],
                    [ 0.93154008, 0.48422909, 0.3291908 ],
                    [ 0.93514863, 0.48832213, 0.32444275],
                    [ 0.93863008, 0.49252027, 0.31974912],
                    [ 0.94198274, 0.49682311, 0.31511847],
                    [ 0.94520535, 0.50122981, 0.31055931],
                    [ 0.94829701, 0.50573917, 0.30608003],
                    [ 0.95125725, 0.51034957, 0.30168887],
                    [ 0.954086  , 0.51505906, 0.29739377],
                    [ 0.95678355, 0.51986536, 0.2932024 ],
                    [ 0.95935057, 0.52476587, 0.28912206],
                    [ 0.96178805, 0.52975777, 0.28515964],
                    [ 0.9640973 , 0.53483802, 0.28132156],
                    [ 0.96627986, 0.54000343, 0.27761379],
                    [ 0.9683375 , 0.5452507 , 0.27404177],
                    [ 0.97027215, 0.55057645, 0.27061043],
                    [ 0.97208896, 0.55597442, 0.26733231],
                    [ 0.97378824, 0.56144311, 0.26420514],
                    [ 0.97537225, 0.56697917, 0.2612321 ],
                    [ 0.97684333, 0.5725793 , 0.2584161 ],
                    [ 0.97820376, 0.57824032, 0.25575953],
                    [ 0.9794557 , 0.58395922, 0.25326432],
                    [ 0.9806012 , 0.58973318, 0.25093197],
                    [ 0.98164451, 0.59555764, 0.24876746],
                    [ 0.9825958 , 0.60142353, 0.24678389],
                    [ 0.98344841, 0.60733543, 0.24496692],
                    [ 0.98420378, 0.61329131, 0.24331643],
                    [ 0.98486309, 0.61928934, 0.24183204],
                    [ 0.98543359, 0.62532321, 0.24052074],
                    [ 0.98592661, 0.63138392, 0.2393925 ],
                    [ 0.98632908, 0.63748058, 0.2384285 ],
                    [ 0.98664126, 0.64361223, 0.23762727],
                    [ 0.9868743 , 0.64977022, 0.23699778],
                    [ 0.98703872, 0.65594684, 0.236546  ],
                    [ 0.98711602, 0.66215449, 0.23625164],
                    [ 0.98710548, 0.66839291, 0.23611251],
                    [ 0.98704522, 0.67463615, 0.23615516],
                    [ 0.98690081, 0.68090692, 0.23634896],
                    [ 0.98666929, 0.68720645, 0.23669008],
                    [ 0.98639295, 0.6935072 , 0.23720252],
                    [ 0.98603581, 0.69983201, 0.23785913],
                    [ 0.98559369, 0.70618283, 0.23865535],
                    [ 0.98511668, 0.71252856, 0.23961378],
                    [ 0.98455154, 0.71890163, 0.24070275],
                    [ 0.98392192, 0.72528731, 0.2419305 ],
                    [ 0.98324116, 0.73167761, 0.24329811],
                    [ 0.98246864, 0.738096  , 0.2447854 ],
                    [ 0.98166755, 0.74450581, 0.24641186],
                    [ 0.98078113, 0.75093941, 0.24815276],
                    [ 0.97983772, 0.75738047, 0.25001371],
                    [ 0.97883927, 0.7638279 , 0.25199054],
                    [ 0.97775747, 0.7702969 , 0.25407166],
                    [ 0.97664794, 0.77675738, 0.25626641],
                    [ 0.9754357 , 0.78324913, 0.25855344],
                    [ 0.9742107 , 0.7897247 , 0.26094721],
                    [ 0.97288357, 0.79623051, 0.2634262 ],
                    [ 0.97152974, 0.80272764, 0.26599948],
                    [ 0.97008613, 0.80924798, 0.2686529 ],
                    [ 0.96860571, 0.81576486, 0.27138993],
                    [ 0.96704307, 0.82230061, 0.27420073],
                    [ 0.96543772, 0.82883583, 0.27708584],
                    [ 0.96375242, 0.83538829, 0.28003763],
                    [ 0.96202315, 0.84194079, 0.28305544],
                    [ 0.96021049, 0.84851164, 0.28613254],
                    [ 0.95835763, 0.85508072, 0.28926815],
                    [ 0.95641175, 0.86167196, 0.29245571],
                    [ 0.95443484, 0.8682573 , 0.29569479],
                    [ 0.95234871, 0.87487125, 0.29897882],
                    [ 0.95024646, 0.88147281, 0.30230776],
                    [ 0.94801413, 0.88811109, 0.3056752 ],
                    [ 0.94578198, 0.89473018, 0.30908112],
                    [ 0.94341986, 0.90138491, 0.31252002],
                    [ 0.94102862, 0.90803285, 0.31599064],
                    [ 0.93853313, 0.91470475, 0.31948933],
                    [ 0.93597111, 0.92138481, 0.32301384],
                    [ 0.9333376 , 0.92807483, 0.32656155],
                    [ 0.93059157, 0.93479051, 0.33012998],
                    [ 0.92781425, 0.94149986, 0.33371683],
                    [ 0.92488992, 0.94824702, 0.33731997],
                    [ 0.92194114, 0.95498491, 0.34093705],
                    [ 0.91886139, 0.96175325, 0.3445663 ],
                    [ 0.91569318, 0.96853549, 0.34820569],
                    [ 0.91244907, 0.97532669, 0.35185336],
                    [ 0.90904184, 0.98215741, 0.35550781]]
        if cmapname[-2:] == "_r":
            palette = palette[::-1]

    elif cmapname == "balance" or cmapname == "balance_r": # balance from cmocean
        palette =  [[0.0931763, 0.11117333, 0.26151239], 
                    [0.09696374, 0.11685935, 0.27307323], 
                    [0.10095308, 0.12237182, 0.28486368], 
                    [0.10496919, 0.12779277, 0.29680302], 
                    [0.10895646, 0.13315177, 0.3088586], 
                    [0.11288435, 0.13846141, 0.32103257], 
                    [0.11673422, 0.14372908, 0.33333054], 
                    [0.12049569, 0.14896155, 0.34574763], 
                    [0.12415974, 0.15416362, 0.35828434], 
                    [0.12771658, 0.1593383, 0.37094853], 
                    [0.13115867, 0.16448923, 0.38374118], 
                    [0.13447947, 0.16962038, 0.39665961], 
                    [0.13767135, 0.17473515, 0.40970398], 
                    [0.14072458, 0.17983627, 0.42287909], 
                    [0.14363072, 0.18492757, 0.43618236], 
                    [0.14637894, 0.19001244, 0.44961519], 
                    [0.14895812, 0.19509499, 0.4631753], 
                    [0.15135593, 0.20017976, 0.47685912], 
                    [0.15355462, 0.20527041, 0.4906717], 
                    [0.15553975, 0.21037331, 0.50460208], 
                    [0.15729216, 0.21549466, 0.51864395], 
                    [0.15878825, 0.22064121, 0.53279215], 
                    [0.15999746, 0.22582007, 0.54704506], 
                    [0.16089188, 0.23104196, 0.56138183], 
                    [0.16143377, 0.23631816, 0.57578653], 
                    [0.16157793, 0.24166222, 0.590238], 
                    [0.16127025, 0.2470906, 0.60470753], 
                    [0.16044598, 0.25262344, 0.61915562], 
                    [0.15902323, 0.2582851, 0.63353349], 
                    [0.15689338, 0.26410533, 0.64778267], 
                    [0.1539574, 0.27012323, 0.66178456], 
                    [0.15004087, 0.27638362, 0.67543723], 
                    [0.14499545, 0.28294239, 0.68854289], 
                    [0.13863186, 0.2898614, 0.70086942], 
                    [0.13079338, 0.29720146, 0.71211193], 
                    [0.12142429, 0.30500298, 0.72192403], 
                    [0.11064197, 0.31326107, 0.72999963], 
                    [0.09884412, 0.32190111, 0.73617986], 
                    [0.08660745, 0.33079572, 0.74053763], 
                    [0.07455574, 0.339807, 0.74332937], 
                    [0.0633252, 0.34881721, 0.74489033], 
                    [0.05350594, 0.35774924, 0.74553506], 
                    [0.04569546, 0.3665586, 0.74551969], 
                    [0.04048845, 0.37522119, 0.7450453], 
                    [0.03830251, 0.38372944, 0.7442575], 
                    [0.03920747, 0.39208653, 0.74325491], 
                    [0.04296193, 0.40029296, 0.74213151], 
                    [0.04895176, 0.40836099, 0.74092981], 
                    [0.05659405, 0.41629659, 0.73970312], 
                    [0.06536138, 0.42410971, 0.73848087], 
                    [0.07486024, 0.43181006, 0.73728405], 
                    [0.08481877, 0.43940606, 0.73613168], 
                    [0.09505364, 0.44690577, 0.73503767], 
                    [0.10544388, 0.45431673, 0.73401239], 
                    [0.11591079, 0.46164592, 0.73306355], 
                    [0.12640422, 0.46890008, 0.73219451], 
                    [0.13689318, 0.47608507, 0.73140878], 
                    [0.14735951, 0.4832062, 0.73070847], 
                    [0.1577938, 0.49026825, 0.73009467], 
                    [0.16819273, 0.49727551, 0.72956758], 
                    [0.17855726, 0.50423175, 0.72912674], 
                    [0.18889149, 0.51114026, 0.72877114], 
                    [0.19920183, 0.51800389, 0.72849931], 
                    [0.20949647, 0.52482502, 0.72830945], 
                    [0.219785, 0.53160557, 0.72819947], 
                    [0.23007819, 0.53834701, 0.7281671], 
                    [0.2403878, 0.54505036, 0.72820993], 
                    [0.25072643, 0.5517162, 0.72832553], 
                    [0.26110744, 0.55834464, 0.72851152], 
                    [0.27154477, 0.56493533, 0.72876568], 
                    [0.28205286, 0.57148747, 0.72908607], 
                    [0.29264639, 0.57799981, 0.7294712], 
                    [0.30334008, 0.5844707, 0.72992014], 
                    [0.31414834, 0.5908981, 0.73043272], 
                    [0.32508485, 0.59727967, 0.73100971], 
                    [0.33616202, 0.60361287, 0.73165302], 
                    [0.34739074, 0.60989508, 0.73236543], 
                    [0.3587791, 0.61612376, 0.7331515], 
                    [0.37033081, 0.62229676, 0.73401859], 
                    [0.3820464, 0.62841247, 0.7349745], 
                    [0.39392195, 0.63447006, 0.73602825], 
                    [0.40594886, 0.64046972, 0.73718984], 
                    [0.41811207, 0.64641303, 0.73847157], 
                    [0.43039507, 0.65230255, 0.73988294], 
                    [0.44277754, 0.65814212, 0.74143349], 
                    [0.45523722, 0.66393667, 0.74313142], 
                    [0.46775119, 0.66969195, 0.74498318], 
                    [0.48029712, 0.67541433, 0.74699317], 
                    [0.49285435, 0.68111044, 0.7491636], 
                    [0.50540471, 0.68678692, 0.75149454], 
                    [0.51793296, 0.6924502, 0.75398412], 
                    [0.53042697, 0.69810631, 0.75662886], 
                    [0.54287759, 0.70376077, 0.75942404], 
                    [0.55526676, 0.70942105, 0.76237214], 
                    [0.56759867, 0.71509001, 0.76546091], 
                    [0.57987197, 0.72077145, 0.76868332], 
                    [0.59207312, 0.72647184, 0.7720415], 
                    [0.60420847, 0.73219314, 0.77552495], 
                    [0.61627838, 0.73793842, 0.77912812], 
                    [0.62827566, 0.74371251, 0.78285113], 
                    [0.64021122, 0.74951572, 0.78668281], 
                    [0.65207654, 0.755353, 0.79062532], 
                    [0.66388068, 0.76122481, 0.79466979], 
                    [0.6756228, 0.76713394, 0.79881424], 
                    [0.68730201, 0.77308319, 0.80305705], 
                    [0.6989276, 0.77907249, 0.80739031], 
                    [0.71049221, 0.78510618, 0.81181716], 
                    [0.72200403, 0.7911843, 0.81633084], 
                    [0.73346579, 0.79730828, 0.82092829], 
                    [0.7448736, 0.80348134, 0.82561092], 
                    [0.75623327, 0.80970394, 0.83037385], 
                    [0.7675464, 0.81597764, 0.83521502], 
                    [0.77881242, 0.82230461, 0.84013382], 
                    [0.79003289, 0.82868636, 0.84512821], 
                    [0.80120893, 0.8351245, 0.85019639], 
                    [0.81234017, 0.84162106, 0.85533742], 
                    [0.82342843, 0.84817744, 0.86054876], 
                    [0.83447136, 0.85479626, 0.86583048], 
                    [0.84546684, 0.86148012, 0.8711823], 
                    [0.85641738, 0.86823022, 0.87660018], 
                    [0.86731711, 0.8750504, 0.88208562], 
                    [0.87815874, 0.88194502, 0.88764074], 
                    [0.88894628, 0.88891503, 0.89325809], 
                    [0.89966112, 0.89596856, 0.89894662], 
                    [0.9102966, 0.90311022, 0.90470462], 
                    [0.92083077, 0.91034961, 0.91054117], 
                    [0.93123405, 0.91769896, 0.91647033], 
                    [0.94142592, 0.92518603, 0.92255498], 
                    [0.94634709, 0.92901013, 0.92575324], 
                    [0.94132632, 0.91984736, 0.9154241], 
                    [0.93686346, 0.91055922, 0.90474739], 
                    [0.93266145, 0.90124101, 0.89392449], 
                    [0.92864616, 0.89191502, 0.88300387], 
                    [0.92477958, 0.8825918, 0.87200971], 
                    [0.92103803, 0.8732773, 0.86095667], 
                    [0.91740482, 0.86397523, 0.84985489], 
                    [0.91386714, 0.85468808, 0.83871202], 
                    [0.91041491, 0.84541748, 0.82753398], 
                    [0.90703981, 0.83616452, 0.81632562], 
                    [0.90373524, 0.82692974, 0.80509065], 
                    [0.90049562, 0.81771336, 0.79383214], 
                    [0.89731486, 0.80851582, 0.78255374], 
                    [0.89418811, 0.79933714, 0.77125826], 
                    [0.89111096, 0.79017723, 0.75994825], 
                    [0.88808029, 0.78103554, 0.7486253], 
                    [0.88509303, 0.7719115, 0.73729103], 
                    [0.88214442, 0.76280522, 0.72594861], 
                    [0.87923119, 0.75371626, 0.7146001], 
                    [0.8763502, 0.74464415, 0.70324744], 
                    [0.87350146, 0.73558719, 0.69188989], 
                    [0.87068003, 0.72654561, 0.68053118], 
                    [0.86788271, 0.71751901, 0.66917362], 
                    [0.86510687, 0.70850676, 0.65781907], 
                    [0.86235347, 0.69950673, 0.64646609], 
                    [0.85961805, 0.69051904, 0.63511837], 
                    [0.85689709, 0.68154344, 0.62377885], 
                    [0.85418868, 0.67257901, 0.61244905], 
                    [0.85149567, 0.66362272, 0.60112588], 
                    [0.84881064, 0.65467602, 0.5898163], 
                    [0.84613135, 0.64573812, 0.57852239], 
                    [0.84346121, 0.63680564, 0.56724066], 
                    [0.84079447, 0.62787931, 0.55597679], 
                    [0.83812737, 0.61895905, 0.54473466], 
                    [0.83546465, 0.61004065, 0.53350956], 
                    [0.8327994, 0.60112544, 0.52230874], 
                    [0.83012886, 0.59221284, 0.51113538], 
                    [0.82745885, 0.58329784, 0.49998384], 
                    [0.82477864, 0.57438378, 0.48886578], 
                    [0.82209351, 0.5654658, 0.4777763], 
                    [0.8193981, 0.55654448, 0.4667218], 
                    [0.81669164, 0.54761797, 0.45570396], 
                    [0.81397435, 0.5386838, 0.44472359], 
                    [0.81124166, 0.52974208, 0.43378676], 
                    [0.80849561, 0.52078914, 0.42289263], 
                    [0.80573189, 0.51182485, 0.41204743], 
                    [0.80294987, 0.50284691, 0.40125361], 
                    [0.80015027, 0.49385203, 0.39051246], 
                    [0.79732536, 0.48484204, 0.37983461], 
                    [0.79448389, 0.47580837, 0.36921324], 
                    [0.79161598, 0.46675401, 0.35866201], 
                    [0.78872016, 0.45767666, 0.34818589], 
                    [0.7858017, 0.44856917, 0.33778299], 
                    [0.78285445, 0.43943184, 0.3274643], 
                    [0.77987598, 0.43026243, 0.31723734], 
                    [0.77686525, 0.42105744, 0.30710879], 
                    [0.77382106, 0.41181324, 0.29708627], 
                    [0.77074198, 0.40252603, 0.28717856], 
                    [0.76762628, 0.39319192, 0.27739578], 
                    [0.76447184, 0.38380698, 0.26774959], 
                    [0.7612761, 0.37436725, 0.2582535], 
                    [0.75803592, 0.36486886, 0.24892308], 
                    [0.75474753, 0.35530812, 0.23977628], 
                    [0.7514064, 0.34568159, 0.23083365], 
                    [0.74800939, 0.33598414, 0.22211675], 
                    [0.74455467, 0.32620861, 0.21364884], 
                    [0.74102893, 0.31635876, 0.20546519], 
                    [0.73743444, 0.30642218, 0.19759197], 
                    [0.73375464, 0.29640553, 0.19007224], 
                    [0.72998135, 0.28630683, 0.18294545], 
                    [0.72610583, 0.27612434, 0.1762545], 
                    [0.72211068, 0.26586686, 0.17004801], 
                    [0.71797972, 0.25554309, 0.1643732], 
                    [0.71369465, 0.24516618, 0.15927527], 
                    [0.7092368, 0.23475218, 0.15479434], 
                    [0.7045832, 0.22432695, 0.15096086], 
                    [0.69971287, 0.21391846, 0.14779166], 
                    [0.69460803, 0.20355522, 0.14528888], 
                    [0.68925026, 0.19327329, 0.14343469], 
                    [0.68362765, 0.18310449, 0.14219685], 
                    [0.67773093, 0.17308255, 0.14152696], 
                    [0.67155603, 0.16323763, 0.14136778], 
                    [0.66510231, 0.15359857, 0.14165564], 
                    [0.65837217, 0.14419254, 0.14232539], 
                    [0.65137002, 0.13504657, 0.14331304], 
                    [0.6441014, 0.1261888, 0.14455832], 
                    [0.63657214, 0.11765076, 0.14600414], 
                    [0.62878806, 0.1094681, 0.14759896], 
                    [0.62075455, 0.10168277, 0.1492933], 
                    [0.61247664, 0.09434294, 0.15104188], 
                    [0.60395923, 0.08750309, 0.15280055], 
                    [0.59520759, 0.08122188, 0.15452537], 
                    [0.58622754, 0.07555913, 0.1561749], 
                    [0.57702676, 0.07056925, 0.15770548], 
                    [0.56761519, 0.06629402, 0.15907416], 
                    [0.558005, 0.06275633, 0.16024132], 
                    [0.54821164, 0.05995167, 0.16116863], 
                    [0.53825351, 0.05784533, 0.16182217], 
                    [0.52815138, 0.05637398, 0.16217425], 
                    [0.51792734, 0.05545236, 0.16220493], 
                    [0.50760343, 0.05498327, 0.16190307], 
                    [0.49720286, 0.05486041, 0.16126216], 
                    [0.486747, 0.0549832, 0.16028395], 
                    [0.47625192, 0.05527092, 0.15898043], 
                    [0.46573629, 0.05564106, 0.15736082], 
                    [0.45521509, 0.05602873, 0.15543963], 
                    [0.44469726, 0.05639244, 0.15323702], 
                    [0.43419316, 0.0566917, 0.15076979], 
                    [0.42371075, 0.05689701, 0.14805546], 
                    [0.41325574, 0.05698815, 0.14511166], 
                    [0.40283182, 0.05695245, 0.14195559], 
                    [0.39244086, 0.05678317, 0.13860362], 
                    [0.38209283, 0.05645532, 0.13506562], 
                    [0.37178172, 0.05598316, 0.13135965], 
                    [0.36150633, 0.05536891, 0.12749858], 
                    [0.3512776, 0.05458756, 0.12348844], 
                    [0.34108131, 0.05367069, 0.11934559], 
                    [0.3309303, 0.0525894, 0.11507352], 
                    [0.32081338, 0.051367, 0.11068434], 
                    [0.31073013, 0.05000264, 0.10618475], 
                    [0.30068793, 0.04847913, 0.1015787], 
                    [0.29067463, 0.046819, 0.09687492], 
                    [0.280689, 0.04502128, 0.09207801], 
                    [0.27073125, 0.04308157, 0.08719176], 
                    [0.26080251, 0.04099314, 0.08221948], 
                    [0.25089381, 0.03876029, 0.07716551], 
                    [0.24100216, 0.03645747, 0.07203246]]
        if cmapname[-2:] == "_r":
            palette = palette[::-1]

    elif cmapname == "my_diverging" or cmapname == "my_diverging_r": # own-made my_diverging from viscm (see files in projects/colors)
        palette =  [[0.04695462, 0.05042128, 0.44822042], 
                    [0.04825398, 0.04927129, 0.4718903], 
                    [0.04961692, 0.04737865, 0.49578926], 
                    [0.05109011, 0.04416217, 0.52036478], 
                    [0.05513987, 0.03796754, 0.54567066], 
                    [0.06837628, 0.02570596, 0.57076771], 
                    [0.08745855, 0.01558113, 0.58927803], 
                    [0.10566755, 0.01298444, 0.60052144], 
                    [0.12204126, 0.01563471, 0.60772686], 
                    [0.13709475, 0.02135971, 0.61278451], 
                    [0.15118319, 0.02899637, 0.61663914], 
                    [0.16443204, 0.03875279, 0.61927202], 
                    [0.17697036, 0.05023268, 0.62040081], 
                    [0.18873943, 0.06267978, 0.61972081], 
                    [0.19972463, 0.07593089, 0.6171156], 
                    [0.20983482, 0.08990503, 0.61247536], 
                    [0.21904131, 0.10429446, 0.60595696], 
                    [0.2273778, 0.11872433, 0.59793781], 
                    [0.23494223, 0.13285318, 0.5889198], 
                    [0.24183961, 0.14646675, 0.57939659], 
                    [0.24770301, 0.15992111, 0.56939399], 
                    [0.25147798, 0.17387961, 0.55897047], 
                    [0.25224446, 0.18802397, 0.55037973], 
                    [0.25094192, 0.20115902, 0.54594287], 
                    [0.24882056, 0.21309899, 0.54491304], 
                    [0.24632426, 0.22416144, 0.54608169], 
                    [0.24353078, 0.23461411, 0.54874153], 
                    [0.24046423, 0.24462718, 0.55245037], 
                    [0.23723622, 0.25442802, 0.55626781], 
                    [0.23385339, 0.26412373, 0.55981041], 
                    [0.23036702, 0.27373041, 0.5629746], 
                    [0.22687144, 0.28325903, 0.56561623], 
                    [0.22352052, 0.29271507, 0.56753929], 
                    [0.2206466, 0.30207885, 0.56844023], 
                    [0.21884648, 0.31129022, 0.56790094], 
                    [0.21914043, 0.32019769, 0.56545829], 
                    [0.22342941, 0.32839572, 0.56082075], 
                    [0.23631465, 0.33431278, 0.55601293], 
                    [0.25213732, 0.33854441, 0.55535868], 
                    [0.26754485, 0.34230826, 0.55703621], 
                    [0.28231955, 0.34588919, 0.55997272], 
                    [0.29657439, 0.34935739, 0.56374331], 
                    [0.31038594, 0.3527499, 0.56813179], 
                    [0.3238607, 0.35606975, 0.57302381], 
                    [0.33706926, 0.3593198, 0.57834378], 
                    [0.35005796, 0.3625041, 0.58403791], 
                    [0.36290665, 0.36561204, 0.59004545], 
                    [0.37566675, 0.36867659, 0.59609814], 
                    [0.38833913, 0.37172284, 0.60208205], 
                    [0.4009688, 0.374751, 0.6079179], 
                    [0.41351719, 0.37781333, 0.61342891], 
                    [0.42601925, 0.38095573, 0.61829814], 
                    [0.43825028, 0.38446788, 0.62149994], 
                    [0.44693281, 0.39054292, 0.61930921], 
                    [0.44910184, 0.39960178, 0.61712644], 
                    [0.45012114, 0.40879181, 0.61687573], 
                    [0.45139871, 0.41783465, 0.61644256], 
                    [0.45336061, 0.42663125, 0.615372], 
                    [0.45591809, 0.43518979, 0.61395151], 
                    [0.45898244, 0.44353091, 0.6123756], 
                    [0.46248327, 0.45168014, 0.61074145], 
                    [0.46636154, 0.45965987, 0.60912246], 
                    [0.47056734, 0.46749002, 0.6075731], 
                    [0.47505906, 0.47518753, 0.60613718], 
                    [0.47980437, 0.48276812, 0.60483369], 
                    [0.48478189, 0.49024684, 0.60364785], 
                    [0.48995849, 0.49763272, 0.60264055], 
                    [0.49532595, 0.50493821, 0.60176814], 
                    [0.50085864, 0.51217065, 0.60107579], 
                    [0.50654256, 0.51933799, 0.60056664], 
                    [0.51237296, 0.52644854, 0.60020868], 
                    [0.51832955, 0.53350733, 0.6000437], 
                    [0.52440216, 0.54052038, 0.60007274], 
                    [0.53058057, 0.5474935, 0.60029665], 
                    [0.53685722, 0.55443358, 0.60069689], 
                    [0.5432231, 0.56134259, 0.60130138], 
                    [0.54966131, 0.56822749, 0.60212009], 
                    [0.55615191, 0.57509615, 0.60316492], 
                    [0.56266713, 0.58195995, 0.60444178], 
                    [0.56916787, 0.58883459, 0.60595566], 
                    [0.57560098, 0.59574237, 0.60769845], 
                    [0.58190025, 0.60271321, 0.60963504], 
                    [0.58799677, 0.60978202, 0.6116887], 
                    [0.59384246, 0.61698077, 0.61373033], 
                    [0.59943775, 0.6243264, 0.61559218], 
                    [0.6048412, 0.63181304, 0.61710955], 
                    [0.61014886, 0.63941556, 0.61816606], 
                    [0.61545913, 0.64710133, 0.6187113], 
                    [0.62084813, 0.65484111, 0.618747], 
                    [0.62636395, 0.66261354, 0.61830363], 
                    [0.63203185, 0.67040502, 0.61742095], 
                    [0.63786223, 0.67820773, 0.61613783], 
                    [0.64385706, 0.68601755, 0.61448794], 
                    [0.65001401, 0.69383271, 0.61249783], 
                    [0.65632893, 0.70165279, 0.61018696], 
                    [0.66279887, 0.70947785, 0.60756543], 
                    [0.6694215, 0.71730802, 0.60463943], 
                    [0.6761903, 0.72514383, 0.60142874], 
                    [0.68310183, 0.732986, 0.59793782], 
                    [0.69015327, 0.74083524, 0.59416921], 
                    [0.69734224, 0.7486918, 0.59012845], 
                    [0.70466676, 0.7565562, 0.58581662], 
                    [0.71212916, 0.76442866, 0.58121804], 
                    [0.71973005, 0.77230888, 0.57633109], 
                    [0.72746368, 0.78019802, 0.57116452], 
                    [0.73532906, 0.7880962, 0.56571866], 
                    [0.74332575, 0.79600388, 0.55998625], 
                    [0.75145498, 0.80392087, 0.55395993], 
                    [0.75973482, 0.81185063, 0.54749055], 
                    [0.76812311, 0.81980015, 0.54068491], 
                    [0.776618, 0.82776993, 0.53353842], 
                    [0.78521901, 0.83575993, 0.52604684], 
                    [0.79392689, 0.84377053, 0.51819159], 
                    [0.8027406, 0.85180146, 0.50997363], 
                    [0.81165999, 0.85985281, 0.50138232], 
                    [0.82068535, 0.8679248, 0.49240144], 
                    [0.82981652, 0.87601752, 0.48301714], 
                    [0.83905616, 0.88413164, 0.47318509], 
                    [0.84840291, 0.89226694, 0.46289974], 
                    [0.85786101, 0.90042416, 0.4520952], 
                    [0.86743297, 0.90860355, 0.44071929], 
                    [0.87712406, 0.91680548, 0.42868654], 
                    [0.88691354, 0.92502776, 0.4161651], 
                    [0.89683513, 0.93327357, 0.40276666], 
                    [0.90686576, 0.94154079, 0.38866143], 
                    [0.91702422, 0.94983047, 0.37358021], 
                    [0.92730584, 0.95814205, 0.35746735], 
                    [0.9377571, 0.96647569, 0.33968787], 
                    [0.93882403, 0.97226818, 0.3290531], 
                    [0.94061685, 0.96057148, 0.31045592], 
                    [0.94216706, 0.94895614, 0.29155409], 
                    [0.94362497, 0.93737071, 0.27208244], 
                    [0.94499731, 0.92581177, 0.25189829], 
                    [0.94629213, 0.91427525, 0.2308031], 
                    [0.94751482, 0.90275783, 0.20851625], 
                    [0.94875962, 0.89116455, 0.18713403], 
                    [0.94983296, 0.8794976, 0.17078935], 
                    [0.95052104, 0.86790286, 0.15794409], 
                    [0.95083884, 0.85641048, 0.14752884], 
                    [0.95083822, 0.84502, 0.13890421], 
                    [0.95054588, 0.83373526, 0.13159835], 
                    [0.95002769, 0.82253446, 0.12543792], 
                    [0.94928989, 0.8114233, 0.1201385], 
                    [0.94836161, 0.80039328, 0.11556804], 
                    [0.94726296, 0.78943885, 0.11161344], 
                    [0.94600732, 0.77855685, 0.10817471], 
                    [0.94461063, 0.76774178, 0.10518615], 
                    [0.94309353, 0.75698459, 0.10262214], 
                    [0.94144776, 0.74629213, 0.10035828], 
                    [0.93969414, 0.73565408, 0.09840228], 
                    [0.93783613, 0.72506977, 0.09669705], 
                    [0.9358794, 0.71453676, 0.09521578], 
                    [0.93382679, 0.70405433, 0.0939105], 
                    [0.93169431, 0.69361304, 0.09281009], 
                    [0.92947143, 0.68321998, 0.09182676], 
                    [0.92717046, 0.67286762, 0.09097805], 
                    [0.92480008, 0.6625503, 0.09026964], 
                    [0.92235298, 0.65227274, 0.08964446], 
                    [0.91983334, 0.64203206, 0.0890959], 
                    [0.91724542, 0.63182512, 0.08862026], 
                    [0.91459998, 0.62164397, 0.08824184], 
                    [0.91189113, 0.61149212, 0.08791641], 
                    [0.90911946, 0.60136846, 0.08763526], 
                    [0.90628912, 0.59126932, 0.08739648], 
                    [0.90340002, 0.58119381, 0.08719136], 
                    [0.900456, 0.57113817, 0.08701858], 
                    [0.89745797, 0.56110053, 0.08687214], 
                    [0.89440619, 0.55107943, 0.08674533], 
                    [0.89130359, 0.54107126, 0.08663652], 
                    [0.88815107, 0.53107374, 0.08654088], 
                    [0.88494978, 0.52108429, 0.08645432], 
                    [0.88170072, 0.51110022, 0.08637287], 
                    [0.87840486, 0.50111873, 0.08629278], 
                    [0.87506358, 0.49113645, 0.0862113], 
                    [0.87166117, 0.48116338, 0.08614126], 
                    [0.86820501, 0.47119046, 0.08612014], 
                    [0.86469509, 0.46121514, 0.08614879], 
                    [0.86113119, 0.45123486, 0.08622772], 
                    [0.85751305, 0.44124686, 0.08635738], 
                    [0.85384091, 0.43124771, 0.08653912], 
                    [0.85011478, 0.4212339, 0.08677397], 
                    [0.84633385, 0.41120242, 0.08706163], 
                    [0.84249712, 0.40115017, 0.08740165], 
                    [0.83860702, 0.39107017, 0.08779965], 
                    [0.83466034, 0.38096078, 0.08825169], 
                    [0.83065911, 0.37081443, 0.08876315], 
                    [0.82658864, 0.36064087, 0.08933362], 
                    [0.82246115, 0.35042104, 0.08996784], 
                    [0.81827551, 0.340149, 0.09066596], 
                    [0.81403121, 0.32981728, 0.09143026], 
                    [0.8097265, 0.31941889, 0.09226506], 
                    [0.80534177, 0.30896805, 0.09317648], 
                    [0.80089564, 0.29843182, 0.09416593], 
                    [0.79638745, 0.28779814, 0.09523765], 
                    [0.7917858, 0.27709529, 0.09640169], 
                    [0.78711972, 0.26626937, 0.09766211], 
                    [0.78236264, 0.25534039, 0.0990281], 
                    [0.77752352, 0.2442764, 0.10050638], 
                    [0.77258047, 0.23308914, 0.10211162], 
                    [0.76754547, 0.22173497, 0.103854], 
                    [0.76238873, 0.21023539, 0.10574952], 
                    [0.75710601, 0.19856782, 0.10781545], 
                    [0.75168652, 0.18671682, 0.11007195], 
                    [0.74610938, 0.17468352, 0.11254456], 
                    [0.74034991, 0.16247688, 0.115262], 
                    [0.7343792, 0.15011763, 0.11825748], 
                    [0.7281618, 0.13764905, 0.12156698], 
                    [0.72162289, 0.1252392, 0.12523473], 
                    [0.7147253, 0.11300209, 0.12929105], 
                    [0.70736469, 0.1013216, 0.13375836], 
                    [0.69944385, 0.09070602, 0.13861464], 
                    [0.6908664, 0.08183514, 0.14376712], 
                    [0.68156022, 0.07544487, 0.14902652], 
                    [0.67159988, 0.07165676, 0.15414611], 
                    [0.66123262, 0.06964533, 0.15896375], 
                    [0.65046238, 0.06944432, 0.16336013], 
                    [0.63931954, 0.07086914, 0.1672341], 
                    [0.62783585, 0.07366268, 0.17046842], 
                    [0.61608697, 0.07736767, 0.17300227], 
                    [0.60413876, 0.08160665, 0.17479948], 
                    [0.59206337, 0.08603578, 0.17587456], 
                    [0.57992307, 0.09040632, 0.17627166], 
                    [0.56776354, 0.09456795, 0.1760486], 
                    [0.55562122, 0.0984267, 0.17526924], 
                    [0.54351998, 0.10194012, 0.17399559], 
                    [0.5314744, 0.10509775, 0.17228037], 
                    [0.51950537, 0.10787619, 0.17018393], 
                    [0.50761126, 0.11030736, 0.1677421], 
                    [0.49580307, 0.11239117, 0.16499852], 
                    [0.48408499, 0.11414212, 0.16198729], 
                    [0.47245715, 0.11558058, 0.15873623], 
                    [0.46092005, 0.11672386, 0.15526954], 
                    [0.44947375, 0.11758785, 0.15160855], 
                    [0.43811803, 0.11818704, 0.14777212], 
                    [0.42685257, 0.11853449, 0.14377682], 
                    [0.41567688, 0.11864213, 0.13963734], 
                    [0.40459014, 0.11852104, 0.13536666], 
                    [0.39357712, 0.1182023, 0.13097178], 
                    [0.38262363, 0.11770265, 0.12653019], 
                    [0.37173477, 0.11701741, 0.12207017], 
                    [0.36090977, 0.11615365, 0.11759059], 
                    [0.35014823, 0.11511719, 0.11309018], 
                    [0.33944921, 0.11391386, 0.10856767], 
                    [0.32881092, 0.11254989, 0.10402187], 
                    [0.31823245, 0.11102975, 0.09945133], 
                    [0.30770998, 0.10936066, 0.09485491], 
                    [0.2972395, 0.1075492, 0.09023138], 
                    [0.28682226, 0.10559557, 0.08557864], 
                    [0.27645528, 0.10350416, 0.08089504], 
                    [0.26613725, 0.10127705, 0.07617857], 
                    [0.25586271, 0.09892002, 0.07142756], 
                    [0.24562779, 0.09643647, 0.06663993], 
                    [0.23543541, 0.09382265, 0.06181262], 
                    [0.22527198, 0.09109023, 0.05694419], 
                    [0.21513602, 0.08823827, 0.05203151], 
                    [0.20501057, 0.08527922, 0.04707266]]
        if cmapname[-2:] == "_r":
            palette = palette[::-1]
    
    elif cmapname == "backscatter_beta" or "backscatter_beta_r":
        palette =  [[0.00000, 0.00000, 0.00000],
                    [0.03529, 0.02353, 0.07059],
                    [0.06667, 0.04314, 0.11373],
                    [0.07843, 0.06275, 0.15686],
                    [0.09020, 0.07843, 0.20000],
                    [0.09804, 0.08627, 0.24706],
                    [0.10588, 0.09804, 0.29412],
                    [0.11373, 0.10980, 0.34118],
                    [0.11765, 0.12157, 0.39216],
                    [0.12549, 0.12941, 0.39608],
                    [0.13333, 0.14118, 0.40000],
                    [0.13725, 0.14902, 0.40784],
                    [0.14510, 0.16078, 0.41176],
                    [0.14902, 0.16863, 0.41569],
                    [0.15686, 0.17647, 0.41961],
                    [0.16078, 0.18824, 0.42353],
                    [0.16863, 0.19608, 0.43137],
                    [0.17255, 0.20784, 0.43529],
                    [0.18039, 0.21569, 0.43922],
                    [0.18431, 0.22353, 0.44314],
                    [0.18824, 0.23529, 0.44706],
                    [0.19608, 0.24314, 0.45490],
                    [0.20000, 0.25490, 0.45882],
                    [0.20392, 0.26275, 0.46275],
                    [0.21176, 0.27059, 0.46667],
                    [0.21961, 0.28235, 0.47059],
                    [0.22745, 0.29020, 0.47451],
                    [0.23529, 0.29804, 0.48235],
                    [0.23922, 0.30588, 0.48627],
                    [0.24706, 0.31765, 0.49020],
                    [0.25490, 0.32549, 0.49412],
                    [0.26275, 0.33333, 0.49804],
                    [0.27059, 0.34510, 0.50196],
                    [0.27451, 0.35294, 0.50588],
                    [0.28235, 0.36078, 0.50980],
                    [0.29020, 0.37255, 0.51765],
                    [0.29804, 0.38039, 0.52157],
                    [0.30196, 0.39216, 0.52549],
                    [0.30980, 0.40000, 0.52941],
                    [0.32157, 0.40784, 0.53333],
                    [0.33333, 0.41569, 0.53725],
                    [0.34510, 0.42745, 0.54118],
                    [0.35294, 0.43529, 0.54510],
                    [0.36471, 0.44314, 0.54902],
                    [0.37647, 0.45098, 0.55294],
                    [0.38824, 0.46275, 0.55686],
                    [0.39608, 0.47059, 0.56078],
                    [0.40784, 0.47843, 0.56078],
                    [0.41961, 0.48627, 0.56471],
                    [0.42745, 0.49804, 0.56863],
                    [0.43922, 0.50588, 0.57255],
                    [0.45098, 0.51373, 0.57647],
                    [0.45882, 0.52549, 0.58039],
                    [0.47059, 0.53333, 0.58431],
                    [0.48235, 0.54118, 0.58824],
                    [0.49412, 0.54902, 0.58824],
                    [0.50980, 0.56078, 0.59216],
                    [0.52157, 0.56863, 0.59608],
                    [0.53333, 0.57647, 0.60000],
                    [0.54510, 0.58431, 0.60000],
                    [0.55686, 0.59608, 0.60392],
                    [0.56863, 0.60392, 0.60784],
                    [0.58039, 0.61176, 0.61176],
                    [0.59608, 0.61961, 0.61176],
                    [0.60784, 0.63137, 0.61569],
                    [0.61961, 0.63922, 0.61961],
                    [0.63137, 0.64706, 0.62353],
                    [0.64314, 0.65882, 0.62353],
                    [0.65490, 0.66667, 0.62745],
                    [0.67059, 0.67843, 0.63137],
                    [0.69020, 0.69020, 0.63529],
                    [0.70588, 0.70196, 0.63922],
                    [0.72549, 0.71765, 0.64314],
                    [0.74118, 0.72941, 0.64706],
                    [0.75686, 0.74118, 0.65098],
                    [0.77647, 0.75294, 0.65490],
                    [0.79216, 0.76471, 0.65882],
                    [0.81176, 0.78039, 0.66275],
                    [0.82745, 0.79216, 0.66275],
                    [0.84314, 0.80392, 0.66667],
                    [0.86275, 0.81569, 0.67059],
                    [0.87843, 0.82745, 0.67451],
                    [0.89804, 0.84314, 0.67843],
                    [0.91373, 0.85490, 0.68235],
                    [0.92157, 0.86275, 0.65882],
                    [0.92549, 0.87451, 0.63529],
                    [0.93333, 0.88235, 0.61176],
                    [0.94118, 0.89412, 0.58824],
                    [0.94510, 0.90196, 0.56078],
                    [0.94902, 0.91373, 0.53725],
                    [0.95686, 0.92157, 0.50980],
                    [0.96078, 0.93333, 0.48627],
                    [0.96471, 0.94118, 0.45882],
                    [0.96863, 0.95294, 0.42745],
                    [0.97255, 0.96078, 0.40000],
                    [0.97647, 0.96863, 0.36863],
                    [0.98039, 0.98039, 0.33333],
                    [0.98039, 0.98824, 0.29804],
                    [0.98431, 1.00000, 0.25490],
                    [0.98824, 0.97647, 0.24314],
                    [0.99216, 0.95294, 0.22745],
                    [0.99216, 0.92941, 0.21176],
                    [0.99608, 0.90196, 0.20000],
                    [0.99608, 0.87843, 0.18431],
                    [1.00000, 0.85490, 0.17255],
                    [1.00000, 0.83137, 0.15686],
                    [1.00000, 0.80784, 0.14118],
                    [1.00000, 0.78039, 0.12549],
                    [1.00000, 0.75686, 0.10980],
                    [1.00000, 0.73333, 0.09020],
                    [1.00000, 0.70588, 0.07059],
                    [1.00000, 0.68235, 0.05098],
                    [0.99608, 0.65882, 0.02353],
                    [0.99608, 0.63137, 0.00000],
                    [0.99216, 0.60784, 0.00000],
                    [0.98824, 0.58039, 0.00000],
                    [0.98431, 0.55294, 0.00000],
                    [0.98431, 0.52941, 0.00000],
                    [0.97647, 0.50196, 0.00000],
                    [0.97255, 0.47451, 0.00000],
                    [0.96863, 0.44314, 0.00000],
                    [0.96471, 0.41569, 0.00000],
                    [0.96078, 0.38431, 0.00000],
                    [0.95294, 0.35294, 0.00000],
                    [0.94902, 0.32157, 0.00000],
                    [0.94510, 0.28627, 0.00000],
                    [0.93725, 0.24314, 0.00000],
                    [0.93333, 0.20000, 0.00000],
                    [0.92549, 0.14118, 0.00392],
                    [0.89804, 0.13725, 0.00784],
                    [0.87059, 0.12941, 0.01569],
                    [0.83922, 0.12549, 0.01961],
                    [0.81176, 0.12157, 0.02353],
                    [0.78431, 0.11373, 0.02745],
                    [0.75686, 0.10980, 0.03137],
                    [0.72941, 0.10588, 0.03529],
                    [0.70196, 0.10196, 0.03529],
                    [0.67451, 0.09412, 0.03922],
                    [0.64706, 0.09020, 0.04314],
                    [0.62353, 0.08627, 0.04314],
                    [0.59608, 0.08235, 0.04314],
                    [0.56863, 0.07451, 0.04706],
                    [0.54510, 0.07059, 0.04706],
                    [0.51765, 0.06667, 0.04706],
                    [0.49020, 0.06275, 0.04706],
                    [0.46667, 0.05882, 0.04706],
                    [0.44314, 0.05490, 0.04314],
                    [0.41569, 0.05098, 0.04314],
                    [0.39216, 0.04706, 0.03922],
                    [0.36863, 0.04314, 0.03922],
                    [0.34510, 0.03529, 0.03529],
                    [0.32157, 0.03137, 0.03137],
                    [0.29804, 0.03137, 0.02745],
                    [0.27451, 0.02745, 0.02353],
                    [0.25098, 0.02353, 0.01961],
                    [0.22745, 0.01961, 0.01569],
                    [0.20784, 0.01569, 0.00784],
                    [0.18824, 0.01176, 0.00392],
                    [0.16863, 0.00000, 0.00000],
                    [0.17255, 0.01961, 0.02353],
                    [0.18039, 0.03922, 0.04706],
                    [0.18824, 0.05490, 0.06667],
                    [0.19216, 0.07059, 0.08235],
                    [0.20000, 0.08627, 0.09412],
                    [0.20784, 0.10196, 0.10588],
                    [0.21569, 0.11765, 0.12157],
                    [0.22353, 0.12941, 0.13333],
                    [0.23137, 0.14510, 0.14902],
                    [0.23529, 0.15686, 0.16078],
                    [0.24314, 0.17255, 0.17647],
                    [0.25098, 0.18824, 0.18824],
                    [0.25490, 0.20392, 0.20392],
                    [0.26275, 0.21569, 0.21569],
                    [0.26667, 0.23137, 0.23137],
                    [0.27451, 0.23922, 0.23922],
                    [0.28235, 0.25098, 0.25098],
                    [0.29020, 0.25882, 0.25882],
                    [0.29412, 0.27059, 0.27059],
                    [0.30196, 0.27843, 0.27843],
                    [0.30980, 0.28627, 0.28627],
                    [0.31765, 0.29804, 0.29804],
                    [0.32549, 0.30588, 0.30588],
                    [0.33333, 0.31765, 0.31765],
                    [0.34118, 0.32549, 0.32549],
                    [0.34510, 0.33725, 0.33725],
                    [0.35294, 0.34510, 0.34510],
                    [0.36078, 0.35686, 0.35686],
                    [0.36863, 0.36471, 0.36471],
                    [0.37647, 0.37647, 0.37647],
                    [0.38431, 0.38431, 0.38431],
                    [0.39608, 0.39608, 0.39608],
                    [0.40392, 0.40392, 0.40392],
                    [0.41569, 0.41569, 0.41569],
                    [0.42353, 0.42353, 0.42353],
                    [0.43529, 0.43529, 0.43529],
                    [0.44314, 0.44314, 0.44314],
                    [0.45098, 0.45098, 0.45098],
                    [0.46275, 0.46275, 0.46275],
                    [0.47059, 0.47059, 0.47059],
                    [0.48235, 0.48235, 0.48235],
                    [0.49020, 0.49020, 0.49020],
                    [0.50196, 0.50196, 0.50196],
                    [0.50980, 0.50980, 0.50980],
                    [0.52157, 0.52157, 0.52157],
                    [0.53333, 0.53333, 0.53333],
                    [0.54118, 0.54118, 0.54118],
                    [0.55294, 0.55294, 0.55294],
                    [0.56078, 0.56078, 0.56078],
                    [0.57255, 0.57255, 0.57255],
                    [0.58039, 0.58039, 0.58039],
                    [0.59216, 0.59216, 0.59216],
                    [0.60392, 0.60392, 0.60392],
                    [0.61176, 0.61176, 0.61176],
                    [0.62353, 0.62353, 0.62353],
                    [0.63137, 0.63137, 0.63137],
                    [0.64314, 0.64314, 0.64314],
                    [0.65490, 0.65490, 0.65490],
                    [0.66275, 0.66275, 0.66275],
                    [0.67451, 0.67451, 0.67451],
                    [0.68627, 0.68627, 0.68627],
                    [0.69412, 0.69412, 0.69412],
                    [0.70588, 0.70588, 0.70588],
                    [0.71765, 0.71765, 0.71765],
                    [0.72549, 0.72549, 0.72549],
                    [0.73725, 0.73725, 0.73725],
                    [0.74902, 0.74902, 0.74902],
                    [0.76078, 0.76078, 0.76078],
                    [0.76863, 0.76863, 0.76863],
                    [0.78039, 0.78039, 0.78039],
                    [0.79216, 0.79216, 0.79216],
                    [0.80392, 0.80392, 0.80392],
                    [0.81176, 0.81176, 0.81176],
                    [0.82353, 0.82353, 0.82353],
                    [0.83529, 0.83529, 0.83529],
                    [0.85490, 0.85490, 0.85490],
                    [0.87451, 0.87451, 0.87451],
                    [0.89804, 0.89804, 0.89804],
                    [0.91765, 0.91765, 0.91765],
                    [0.93725, 0.93725, 0.93725],
                    [0.95686, 0.95686, 0.95686],
                    [0.98039, 0.98039, 0.98039],
                    [1.00000, 1.00000, 1.00000]]
    return mpl.colors.ListedColormap(palette)


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
    
    x = np.arange(16)
    y = np.arange(16)
    a = np.arange(256).reshape(16, 16)
    ax = plt.subplot(111)
    plt.pcolormesh(x, y, a.T, cmap=takecmap('backscatter_beta'))
    cbar = plt.colorbar(orientation="horizontal")
    cbar.set_ticks([])
    cbar.set_ticklabels([])
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
    