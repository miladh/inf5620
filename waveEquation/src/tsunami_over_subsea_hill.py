from pylab import *
import nose.tools as nt
import waveMotion as wm
import mayavi.mlab as mlab
import time

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
            Is = self.Lx / 30
            Ia = 1
            b = 1
            return self.gaussian2D(x,y,x0=x0,y0=y0,I0=0,Ia=Ia,Is=Is,b=b)
        elif self.initial_wave == "gaussian_wall":
            x0 = self.Lx / 2
            y0 = self.Ly / 4
            Is = self.Lx / 30
            Ia = 1
            b = 0.01
            return self.gaussian2D(x,y,x0=x0,y0=y0,I0=0,Ia=Ia,Is=Is,b=b)
        elif self.intial_wave == "rectangular":
            Ia = 1.0
            x0 = self.Lx / 2
            y0 = self.Ly / 4
            width = 0.6 * self.Lx
            height = 0.4 * self.Ly
            return self.rectangularHill(x,y,x0,y0,width,height,Ia)
      
    def V(self,x,y):
        return 0 * x + 0 * y

    def f(self,x,y,t):
        return 0 * x + 0 * y

    def q(self,x,y):
        if self.hill == "gaussian_sphere":
            x0 = self.Lx / 3
            y0 = self.Ly * 3. / 4.
            Is = self.Lx * 0.3
            #return self.rectangularHill(x,y,0.8)
            return self.gaussian2D(x,y,x0=x0, y0=y0, I0=1, Ia=-0.8, Is=Is, b = 0.1)
        elif self.hill == "rectangular":
            I0 = 1.0
            Ia = -0.8
            x0 = self.Lx / 2
            y0 = self.Ly * 3 / 4
            width = 0.6 * self.Lx
            height = 0.4 * self.Ly
            return self.rectangularHill(x,y,x0,y0,width,height,I0,Ia)
    
    def rectangularHill(self,x,y,x0,y0,width,height,I0,Ia):
        result = I0 + Ia * logical_and(logical_and(x > x0 - width / 2, x < x0 + width / 2), logical_and(y > x0 - height / 2, y < x0 + height / 2))
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
    
    def fileName():
        return self.hill + "-" + self.intial_wave + "-" + self.dx + "-" + self.dy

problem = None        
surfaceHill = None
surfFig = None
angle = 45
frame = 0
doSave = False

def plot_u_with_hill(u,x,y,t):
    global surfaceHill, problem, surfFig, angle, frame
    if surfFig:
        surfFig.scene.disable_render = True
        
    wm.plot_u_mayavi(u,x,y,t,z_scale=0.4,disable_render=False,opacity=0.8,doSleep=False)
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
    mlab.view(azimuth=angle, elevation=55)
    surfFig.scene.reset_zoom()
    surfFig.scene.disable_render = False
    angle += 0.2
    #if t == 0:
    #    time.sleep(0.1)
    #time.sleep(0.01)
    if doSave:
        mlab.savefig("../export/" + problem.fileName() + "/%05d.png" % frame)
    frame += 1

def runTsunamiProblem():
    global problem, filename, doSave
    dt=0.005; T = 1; Lx=1.0; Ly=1.0; dx=0.01; dy=0.01
    b=0.0
    BC = "neumann"
    versions = ["vec"] #, "scalar"]

    doSave = False
    
    problem = TsunamiProblem(b=b, Lx=Lx, Ly=Ly, dx=dx, dy=dy, dt=dt, hill="rectangular", initial_wave="gaussian_sphere")
               
    u, x, y, t, cpu = wm.solver(problem, Lx, Ly, dx, dy, dt, T, BC, "vec",
                        user_action=plot_u_with_hill)
    
    #problem = TsunamiProblem(b=b, Lx=Lx, Ly=Ly, dx=dx, dy=dy, dt=dt, hill="rectangular", intial_wave="gaussian_wall")                 
        
        #mlab.savefig("../export/test.vrml")
         
            
if __name__ == "__main__":
    runTsunamiProblem()