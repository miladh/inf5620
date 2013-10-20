# -*- coding: utf-8 -*-
from pylab import*
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
import mayavi.mlab as mlab
import time

plt.ion()  # interactive mode on
close("all")

def plot_u(u, x, y, t,n):
    """
    user_action function for solver. 
    Make animation using matplotlib. 
    """
    X, Y = meshgrid(x, y)
    clf()
    ax = gca(projection='3d')
    ax.plot_wireframe(X, Y, u,rstride=1, cstride=1, cmap=cm.jet,
                    linewidth=0.1, antialiased=False)
    
    ax.set_zlim(-10,10)
    ax.set_xlabel('$X$', fontsize=15)
    ax.set_ylabel('$Y$', fontsize=15)
    ax.set_zlabel('$u(x,y)$', fontsize=15)
    plt.tight_layout()
    plt.draw()       
             
    # Let the initial condition stay on the screen for 2
    # seconds, else insert a pause of 0.2 s between each plot
    time.sleep(2) if t[n] == 0 else time.sleep(0.0)
"*****************************************************************************"

firstPlot = False
surfPlot = None
surfFig = None
surfAxes = None

def plot_u_mayavi(u, x, y, t,n,disable_render=True,
                  opacity=0.7,z_scale=0.5,doSleep=True,resetZoom=True):
    """
    user_action function for solver.
    Make animation using mayavi. 
    """
    global surfPlot, surfFig, surfAxes
    normalizationFactor = 1 / z_scale
    if not surfFig:        
        surfFig = mlab.figure(size=(1280,720),bgcolor=(0,0,0))
    if not surfPlot:
        # Set up temporary plot for scaling
        X,Y = meshgrid(x,y)
        utest = 0.5 * sin(20 * X) + 0.5 * cos(20 * Y)
        surfPlot = mlab.surf(x,y,utest, opacity=opacity, colormap="Blues", 
                             vmin=-0.2, vmax=0.7, 
                             extent=[x.min(), x.max(), y.min(), y.max(), -0.1, 0.1])
        # Set reverse colormap
        lut = surfPlot.module_manager.scalar_lut_manager.lut.table.to_array()
        ilut = lut[::-1]
        surfPlot.module_manager.scalar_lut_manager.lut.table = ilut
        
    if disable_render:
        surfFig.scene.disable_render = True
    surfFig.scene.anti_aliasing_frames = 0
    surfPlot.mlab_source.set(x=x, y=y, scalars=u*normalizationFactor)

    if disable_render:
        surfFig.scene.disable_render = False
    if doSleep:
        if t[n] == 0:
            time.sleep(0.5)
        time.sleep(0.02)
    if resetZoom:        
        surfFig.scene.reset_zoom()
