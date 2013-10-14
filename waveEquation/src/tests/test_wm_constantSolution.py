# -*- coding: utf-8 -*-
from pylab import *
import nose.tools as nt
import waveMotion as wm

class case_constantSolution(wm.Problem):
        """
        Case:
            constant solution, 
            
            ue = c
        """
        def __init__(self, b, c):    
            self.b = b
            self.c = c
            
        def exactSolution(self,x,y,t):
            return self.c
               
        def I(self,x,y):        
            return self.exactSolution(0,x,y);
          
        def V(self,x,y):     
            return 0.0
    
        def f(self,x,y,t):
            return 0.0
    
        def q(self,x,y):
            return 1.0
    
        def p(self,x,y):
            return 1.0

def test_constantSolution():
    """
    Test problem where u=I is the exact solution, to be
    reproduced (to machine precision) by ady relevant method.
    """
    def assert_no_error(u, x, y, t, n):        
        xv = x[:,newaxis]      # for vectorized function evaluations
        yv = y[newaxis,:]
        ue = 0*u
        ue = problem.exactSolution(xv,yv,t[1])
        diff = abs(u - ue).max()   
        nt.assert_almost_equal(diff, 0, places=14)

    print "------------------test constant solution----------------"    
    
    dt=0.01; T = 0.3; Lx=1; Ly=1; dx=0.1; dy=0.1 
    b=2; c=0.05
    BC = "neumann";
    versions = ["vec","scalar"]
    
    for version in versions:
        problem = case_constantSolution(b=b,c=c)
        
        #Run solver and visualize u at each time level
        u, x, y, t, cpu = wm.solver(problem, Lx=Lx, Ly=Ly, dx=dx, dy=dy, 
                     dt=dt, T=T,BC = BC, version=version, 
                     user_action=assert_no_error)     
        
        print version + ": ", "test_constantSolution succeeded!"
        
if __name__ == '__main__':
    test_constantSolution()
    