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
        def __init__(self, b, c):    
            self.b = b
            self.c = c
            
        def exactSolution(self,x,y,t):
            Lx = x[-1] - x[0]
            Ly = y[-1] - y[0]
            return (2*x**3 - 3 * Lx * x**2)*(2*y**3 - 3 * Ly * y**2)*t
               
        def I(self,x,y):        
            return self.exactSolution(x,y,0);
          
        def V(self,x,y):
            return 0.0
    
        def f(self,x,y,t):
            return 0.0
    
        def q(self,x,y):
            return 1.0
    
        def p(self,x,y):
            return 1.0
    "*************************************************************************"
    dt=0.01; T = 0.3; Lx=1; Ly=1; Nx=10; Ny=10 
    b=2; c=0.05
    BC = "neumann"
    versions = ["vec", "scalar" ]
    
    for version in versions:
        problem = testProblem_cubicSolution(b=b,c=c)
        
        #Run solver and visualize u at each time level
        u, x, y, t = wm.viz(problem, Lx=Lx, Ly=Ly, Nx=Nx, Ny=Ny, dt=dt, T=T, 
                   BC = BC, version=version, animate=True)
         
        ue  = problem.exactSolution(x,y,t)
        difference = abs(ue - u).max()  # max deviation
        
        
        if not nt.assert_almost_equal(difference, 0, places=14):
            print version + ": ", "test_cubicSolution succeeded!"
            
if __name__ == "__main__":
    test_cubicSolution()            