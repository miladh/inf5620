# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 11:49:56 2013

@author: Milad H. Mobarhan
"""
from pylab import*
import nose.tools as nt
import waveMotion as wm


def test_constantSolution():
    """
    Test problem where u=I is the exact solution, to be
    reproduced (to machine precision) by any relevant method.
    """
    "*************************************************************************"
    class testProblem_constantSolution(wm.Problem):
        """
        Problem:
            Simple wave motion
        """
        def __init__(self, b, c):    
            self.b = b
            self.c = c
            
        def exactSolution(self,t):
            return self.c
               
        def I(self,x,y):        
            return self.exactSolution(0);
          
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
        problem = testProblem_constantSolution(b=b,c=c)
        
        #Run solver and visualize u at each time level
        u, x, y, t = wm.viz(problem, Lx=Lx, Ly=Ly, Nx=Nx, Ny=Ny, dt=dt, T=T, 
                   BC = BC, version=version, animate=False)
         
        ue  = problem.exactSolution(t)
        difference = abs(ue - u).max()  # max deviation
        
        
        if not nt.assert_almost_equal(difference, 0, places=14):
            print version + ": ", "test_constantSolution succeeded!"
"*****************************************************************************"

def test_standingUndamped():
    """
    Test problem where u=I is the exact solution, to be
    reproduced (to machine precision) by any relevant method.
    """
    "*************************************************************************"
    class testProblem_constantSolution(wm.Problem):
        """
        Problem:
            Simple wave motion
        """
        def __init__(self, b, A,w, kx,ky):    
            self.b = b
            self.A = A ; self.w = w
            self.kx, self.ky = kx, ky

            
        def exactSolution(self,x,y,t):
            ue = A*cos(kx*x)*cos(ky*x)*cos(w*t)
            return ue
               
        def I(self,x,y):        
            return  self.exactSolution(x,y,0)
          
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
    b = 0.0; A = 0.05; w=100.0; kx=1.0*pi/Lx; ky= 1.0*pi/Ly
    BC = "neumann"
    version = "vec"
     
    dtValues = array([0.5, 0.25, 0.1, 0.05, 0.025, 0.01])
    e_max=.0
    
    
    problem = testProblem_constantSolution(b,A,w,kx,ky)
    
    for dt in dtValues:
        u, x, y, t = wm.viz(problem, Lx=Lx, Ly=Ly, Nx=Nx, Ny=Ny, 
                             dt=dt, T=T,BC = BC, version=version, 
                             animate=False)
        ue = u*0                     
        for i in range(0,ue.shape[0]-1):
            for j in (0,ue.shape[1]-1):
                ue[i,j] = problem.exactSolution(x[i],y[j],t[-1]) 
        e = abs(u-ue)
        e_max = max(e_max, e.max())
       
        print e_max
"*****************************************************************************"    
if __name__ == '__main__':
    test_constantSolution()
    test_standingUndamped()