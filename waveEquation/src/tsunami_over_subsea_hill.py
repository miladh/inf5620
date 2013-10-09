from pylab import *
import nose.tools as nt
import waveMotion as wm
import mayavi.mlab as mlab

class TsunamiProblem(wm.Problem):
    def __init__(self, b, Lx, Ly):
        self.b = b
        self.Lx = Lx
        self.Ly = Ly
           
    def I(self,x,y):  
        x0 = self.Lx / 4
        y0 = self.Ly / 3
        I0 = 0
        Ia = 0.5
        Is = 0.1
        r2 = (x - x0)**2 + (y - y0)**2
        return I0 + Ia * exp(-r2 / Is**2)
      
    def V(self,x,y):
        return 0 * x + 0 * y

    def f(self,x,y,t):
        return 0 * x + 0 * y

    def q(self,x,y):
        return self.rectangularHill(x,y,0.95)
    
    def rectangularHill(self,x,y,b):
        Lx = self.Lx
        Ly = self.Ly
        result = 1 - logical_and(logical_and(x > Lx * 0.2, x < Lx * 0.8), logical_and(y > 0.2 * Ly, y < 0.8 * Ly)) * b
        return result
    
    def linearHill(self,x,y,b):
        Lx = self.Lx
        Ly = self.Ly
        result = 1 - b * (Lx - x)
        return result
    
    def gaussian2D(self,x,y,Ia,b):
        x0 = self.Lx / 2
        y0 = self.Ly / 2
        I0 = 1
        Is = 0.5
        r2 = (x - x0)**2 + (y - y0)**2 / b
        return I0 - Ia * exp(-r2 / Is**2)        

    def p(self,x,y):
        return 1.0
def runTsunamiProblem():
    dt=0.01; T = 20.0; Lx=1.0; Ly=1.0; Nx=40; Ny=40
    b=0.0
    BC = "neumann"
    versions = ["vec"] #, "scalar"]
    
    for version in versions:
        problem = TsunamiProblem(b=b, Lx=Lx, Ly=Ly)
        
        #Run solver and visualize u at each time level
        u, x, y, t = wm.viz(problem, Lx=Lx, Ly=Ly, Nx=Nx, Ny=Ny, dt=dt, T=T, 
                   BC = BC, version=version, animate=True)
        
        mlab.savefig("test.vrml")
         
            
if __name__ == "__main__":
    runTsunamiProblem()