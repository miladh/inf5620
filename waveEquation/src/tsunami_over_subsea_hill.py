from pylab import *
import nose.tools as nt
import waveMotion as wm
import mayavi.mlab as mlab
import time
import os, errno

class TsunamiProblem(wm.Problem):
    def __init__(self, b, Lx, Ly, dx, dy, dt, hill, initial_wave):
        self.b = b
        self.Lx = Lx
        self.Ly = Ly
        self.hill = hill
        self.initial_wave = initial_wave
        self.dx = dx
        self.dy = dy
        self.dt = dt
           
    def I(self,x,y):
        if self.initial_wave == "gaussian_sphere":
            x0 = self.Lx / 2
            y0 = self.Ly / 4
            Is = self.Lx / 20
            Ia = 3
            b = 1
            return self.gaussian2D(x,y,x0=x0,y0=y0,I0=0,Ia=Ia,Is=Is,b=b)
        elif self.initial_wave == "gaussian_wall":
            x0 = self.Lx / 2
            y0 = 0
            Is = self.Lx *2
            Ia = 1
            b = 0.001
            return self.gaussian2D(x,y,x0=x0,y0=y0,I0=0,Ia=Ia,Is=Is,b=b)
        elif self.initial_wave == "rectangular":
            Ia = 1
            I0 = 0
            x0 = self.Lx / 2
            y0 = self.Ly / 8
            width = 0.8 * self.Lx
            height = 0.1 * self.Ly
            return self.rectangularHill(x,y,x0,y0,width,height,I0,Ia)
        else:
            return 0 * x + 0 * y
      
    def V(self,x,y):
        return 0 * x + 0 * y

    def f(self,x,y,t):
        if self.initial_wave == "gaussian_wall_source":
            x0 = self.Lx / 2
            y0 = self.dy * 2
            Is = self.Lx * 2
            dt = self.dt
            Ia = 3000
            b = 0.001
            frequency = 1 / dt * pi / 16
            return cos(frequency * t) * self.gaussian2D(x,y,x0=x0,y0=y0,I0=0,Ia=Ia,Is=Is,b=b)
        else:
            return 0 * x + 0 * y

    def q(self,x,y):
        if self.hill == "gaussian_sphere":
            x0 = self.Lx / 3
            y0 = self.Ly * 3. / 4.
            Is = self.Lx * 0.3
            #return self.rectangularHill(x,y,0.8)
            return self.gaussian2D(x,y,x0=x0, y0=y0, I0=1, Ia=-0.8, Is=Is, b = 1)
        if self.hill == "gaussian_blob":
            x0 = self.Lx / 3
            y0 = self.Ly * 3. / 4.
            Is = self.Lx * 0.3
            #return self.rectangularHill(x,y,0.8)
            return self.gaussian2D(x,y,x0=x0, y0=y0, I0=1, Ia=-0.8, Is=Is, b = 0.1)
        elif self.hill == "rectangular":
            I0 = 1.0
            Ia = -0.6
            x0 = self.Lx / 2
            y0 = self.Ly * 3 / 4
            width = 0.6 * self.Lx
            height = 0.4 * self.Ly
            return self.rectangularHill(x,y,x0,y0,width,height,I0,Ia)
        elif self.hill == "double_slit":
            I0 = 1.0
            Ia = -0.999
            x0 = self.Lx / 2
            y0 = self.Ly / 2 
            width = 0.05 * self.Lx
            height = 0.1 * self.Ly
            spacing = 0.2 * self.Lx
            return self.doubleSlit(x,y,x0,y0,width,height,spacing,I0,Ia)
        elif self.hill == "gaussian_wall":
            x0 = self.Lx / 3
            y0 = self.Ly * 3. / 4.
            Is = self.Lx *2
            b = 0.001
            #return self.rectangularHill(x,y,0.8)
            return self.gaussian2D(x,y,x0=x0, y0=y0, I0=1, Ia=-0.8, Is=Is, b=b)
        else:
            return 1 + 0 * x + 0 * y
    
    def rectangularHill(self,x,y,x0,y0,width,height,I0,Ia):
        result = I0 + Ia * logical_and(logical_and(x > x0 - width / 2, x < x0 + width / 2), logical_and(y > x0 - height / 2, y < x0 + height / 2))
        return result
    
    def doubleSlit(self,x,y,x0,y0,width,height,spacing,I0,Ia):
        result = I0 + Ia * logical_and(logical_or(logical_or(x < x0 - spacing / 2 - width, x > x0 + spacing / 2 + width), 
                                                  logical_and(x > x0 - spacing / 2, x < x0 + spacing / 2)), 
                                       logical_and(y > x0 - height / 2, y < x0 + height / 2))
        return result
    
    def linearHill(self,x,y,b):
        Lx = self.Lx
        Ly = self.Ly
        result = 1 - b * (Lx - x)
        return result
    
    def gaussian2D(self,x,y,x0,y0,I0,Ia,Is,b):
        r2 = (x - x0)**2 + (y - y0)**2 / b
        return I0 + Ia * exp(-r2 / Is**2)        

    def p(self,x,y):
        return 1.0
    
    def fileName(self):
        return self.hill + "-" + self.initial_wave + "-" + str(self.dx) + "-" + str(self.dy)

problem = None
surfaceHill = None
surfFig = None
frame = 0
doSave = False

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def plot_u_with_hill(u,x,y,t):
    global surfaceHill, problem, surfFig, frame
    if surfFig:
        surfFig.scene.disable_render = True
        
    wm.plot_u_mayavi(u,x,y,t,z_scale=1.0,disable_render=False,opacity=0.85,doSleep=False,resetZoom=False)
    surfFig = mlab.gcf()
    xv,yv = x[:,newaxis], y[newaxis,:]
    hill = -0.2 - problem.q(xv,yv) * 0.2
    if not surfaceHill:
        surfaceHill = mlab.surf(x,y,hill, warp_scale=1, colormap="GnBu",opacity=1)
        # Set reverse colormap
        lut = surfaceHill.module_manager.scalar_lut_manager.lut.table.to_array()
        ilut = lut[::-1]
        surfaceHill.module_manager.scalar_lut_manager.lut.table = ilut
    else:
        surfaceHill.mlab_source.set(x=x,y=y,scalars=hill)
    
    angle = 25 + 20 * (1 - cos(t * pi / 2)**2) + 60 * t # changes camera angle smoothly
    elevation = 55 - 20 * (1 - cos(1.2 * t * pi / 2)**2)  # changes camera elevation smoothly
    distance = 3 - 0.4 * (1 - cos(3 * t * pi / 2)**2) # changes camera distance smoothly
    mlab.view(azimuth=angle, elevation=elevation,distance=distance)
    #surfFig.scene.reset_zoom()
    surfFig.scene.disable_render = False
    #if t == 0:
    #    time.sleep(0.1)
    #time.sleep(0.01)
    if doSave:
        print "Saving frame %05d" % frame
        mkdir_p("../export/" + problem.fileName())
        mlab.savefig("../export/" + problem.fileName() + "/%05d.png" % frame)
    frame += 1

def runTsunamiProblem():
    global problem, filename, doSave, angularIncrement, surfaceHill, surfFig, surfPlot, frame
    dt=0.005; T = 10; Lx=1.0; Ly=1.0; dx=0.01; dy=0.01
    b=0.0
    BC = "neumann"
    
    problem = TsunamiProblem(b=b, Lx=Lx, Ly=Ly, dx=dx, dy=dy, dt=dt, hill="gaussian_sphere", initial_wave="gaussian_wall_source")
    u, x, y, t, cpu = wm.solver(problem, Lx, Ly, dx, dy, dt, T, BC, "vec",
                    user_action=plot_u_with_hill)
    return
    hills = ["rectangular", "gaussian_blob", "gaussian_sphere", "gaussian_wall", "double_slit", "none"]
    initial_waves = ["gaussian_sphere", "gaussian_wall", "gaussian_wall_source"]
    for hill in hills:
        for initial_wave in initial_waves:
            problem = TsunamiProblem(b=b, Lx=Lx, Ly=Ly, dx=dx, dy=dy, dt=dt, hill=hill, initial_wave=initial_wave)
            u, x, y, t, cpu = wm.solver(problem, Lx, Ly, dx, dy, dt, T, BC, "vec",
                            user_action=plot_u_with_hill)
            mlab.clf()
            surfaceHill = None
            wm.surfPlot = None
            frame = 0
    initial_waves = ["gaussian_wall_source","gaussian_sphere"]
    for diff in [0.02, 0.05, 0.1]:
        for initial_wave in initial_waves:
            dx = diff
            dy = diff
            problem = TsunamiProblem(b=b, Lx=Lx, Ly=Ly, dx=dx, dy=dy, dt=dt, hill="gaussian_blob", initial_wave=initial_wave)
            u, x, y, t, cpu = wm.solver(problem, Lx, Ly, dx, dy, dt, T, BC, "vec",
                            user_action=plot_u_with_hill)
            mlab.clf()
            surfaceHill = None
            wm.surfPlot = None
            frame = 0
    
    #problem = TsunamiProblem(b=b, Lx=Lx, Ly=Ly, dx=dx, dy=dy, dt=dt, hill="rectangular", intial_wave="gaussian_wall")                 
        
        #mlab.savefig("../export/test.vrml")
         
            
if __name__ == "__main__":
    runTsunamiProblem()