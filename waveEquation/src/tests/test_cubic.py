import sys
sys.path.append("..")
sys.path.append(".")

from pylab import *
import nose.tools as nt
import waveMotion as wm

def test_cubicSolution():
    """
    Test problem where u=I is the exact solution, to be
    reproduced (to machine precision) by any relevant method.
    """
    "*************************************************************************"
    class testProblem_cubicSolution(wm.Problem):
        """
        Problem:
            Simple wave motion
        """
        def __init__(self, b, Lx, Ly):
            self.b = b
            self.Lx = Lx
            self.Ly = Ly
            
        def X(self,x):
            Lx = self.Lx
            return (2*x**3 - 3 * Lx * x**2)
            
        def Y(self,y):
            Ly = self.Ly
            return (2*y**3 - 3 * Ly * y**2)
            
        def T(self,t):
            return t
            
        def exactSolution(self,x,y,t):
            X = self.X
            Y = self.Y
            T = self.T
            return X(x) * Y(y) * T(t)
               
        def I(self,x,y):        
            return self.exactSolution(x,y,0);
          
        def V(self,x,y):
            X = self.X
            Y = self.Y
            return X(x)*Y(y)
    
        def f(self,x,y,t):
            X = self.X
            Y = self.Y
            T = self.T
            q = self.q
            Lx = self.Lx
            Ly = self.Ly
            return X(x) * Y(y) * 0 - q(x,y) * (12*x - 6 * Lx) * Y(y) * T(t) - q(x,y) * X(x) *(12*y - 6 * Ly) * T(t)
    
        def q(self,x,y):
            return 1.0
    
        def p(self,x,y):
            return 1.0
    "*************************************************************************"
    dt=0.01; T = 0.1; Lx=1; Ly=1; Nx=10; Ny=10
    b=0.0
    BC = "neumann"
    versions = ["vec", "scalar"]
    
    for version in versions:
        problem = testProblem_cubicSolution(b=b, Lx=Lx, Ly=Ly)
        
        #Run solver and visualize u at each time level
        u, x, y, t = wm.viz(problem, Lx=Lx, Ly=Ly, Nx=Nx, Ny=Ny, dt=dt, T=T, 
                   BC = BC, version=version, animate=True)
         
        print "Calculating ue"
        xv = x[:,newaxis]          # for vectorized function evaluations
        yv = y[newaxis,:]
        ue  = problem.exactSolution(xv,yv,t[-1])
        print u
        difference = abs(ue - u).max()  # max deviation
        
        
        if not nt.assert_almost_equal(difference, 0, places=14):
            print version + ": ", "test_cubicSolution succeeded!"
            
if __name__ == "__main__":
    test_cubicSolution()