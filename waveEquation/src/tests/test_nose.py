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
    "*************************************************************************"
    dt=0.01; T = 0.3; Lx=1; Ly=1; Nx=10; Ny=10 
    b=2; c=0.05
    BC = "neumann"
    versions = ["vec", "scalar" ]
    animate_ue = False
    
    for version in versions:
        problem = case_constantSolution(b=b,c=c)
        
        #Run solver and visualize u at each time level
        u, x, y, t = wm.viz(problem, Lx=Lx, Ly=Ly, Nx=Nx, Ny=Ny, dt=dt, T=T, 
                   BC = BC, version=version, animate=False)
        
        xv = x[:,newaxis]          # for vectorized function evaluations
        yv = y[newaxis,:]
        ue = 0*u
        ue[:,:]  = problem.exactSolution(xv,yv,t)
        difference = abs(ue - u).max()  # max deviation
        
        
        if not nt.assert_almost_equal(difference, 0, places=14):
            print version + ": ", "test_constantSolution succeeded!"
    
    if animate_ue:
        for t in t:
            wm.plot_u(ue,x,y,t)
            
           
"*****************************************************************************"

def test_standingUndamped():
    """
    Verification: standing, undamped waves, constant velocity, no source term.
    Controling the convergence  rate, using standing, undamped waves.
    
    """
    "*************************************************************************"
    class case_constantSolution(wm.Problem):
        """
        Case:
            standing, undamped waves,
            
            ue = A*cos(kx*x)*cos(ky*y)*cos(w*t)
        """
        def __init__(self, b, A, w, kx,ky):    
            self.b = b
            self.A = A ; self.w = w
            self.kx, self.ky = kx, ky

            
        def exactSolution(self,x,y,t):
            ue = self.A*cos(self.kx*x)*cos(self.ky*y)*cos(self.w*t)
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
    dt=0.01; T = 3; Lx=1; Ly=1; Nx=10; Ny=10
    b = 0.0; A = 0.05; w=100.0; kx=1.0*pi/Lx; ky= 1.0*pi/Ly
    BC = "neumann"
    version = "vec"
    animate_ue = False
    
    
    
    dtValues = array([0.5, 0.25, 0.1, 0.05, 0.025, 0.01])
    problem = case_constantSolution(b,A,w,kx,ky)
    
    for dt in dtValues:
        e_max=.0
        u, x, y, t = wm.viz(problem, Lx=Lx, Ly=Ly, Nx=Nx, Ny=Ny, 
                             dt=dt, T=T,BC = BC, version=version, 
                             animate=False)
                             
        xv = x[:,newaxis]      # for vectorized function evaluations
        yv = y[newaxis,:]
        ue = 0*u
        
        for tn in t:
            ue[:,:]  = problem.exactSolution(xv,yv,tn)
            if animate_ue and dt==dtValues.min(): wm.plot_u(ue,x,y,tn)
        
        e = abs(u-ue)
        e_max = max(e_max, e.max())
       
#        print "dt= ", dt, "  ", e_max/dt**2

"*****************************************************************************"

def test_cubicSolution():
    """
    Verification: cubic solution, constant velocity, with source term.
    Check that computed values equals ue within machine precision
    
    """
    "*************************************************************************"
    class case_cubicSolution(wm.Problem):
        """
        Case:
            Cubic solution
            
            ue = X(x) Y(y) T(t)
        where
            X(x) = 2*x^3 -3*Lx*x^2
            Y(y) = 2*y^3 -3*Ly*y^2
            T(t) = sin(t)
            
        """
        def __init__(self, b, A,w, kx,ky):    
            self.b = b
            self.A = A ; self.w = w
            self.Lx, self.Ly = Lx, Ly

        def X(self,x):
           return (2*x**3 - 3*self.Lx*x**2)
         
        def Y(self, y):
           return (2*y**3 - 3*self.Ly*y**2)
            
        def exactSolution(self,x,y,t):
            return self.A*self.X(x)*self.Y(y)*sin(self.w*t)
               
        def I(self,x,y):        
            return self.exactSolution(x,y,0)
          
        def V(self,x,y): 
            return self.A*self.X(x)*self.Y(y)*self.w
    
        def f(self,x,y,t):          
            fx = (12*x-6*Lx)*self.Y(y)*sin(self.w*t)
            fy = (12*y-6*Ly)*self.X(x)*sin(self.w*t)
            return -self.q(x,y)*self.A*(fx+fy)
    
        def q(self,x,y):
            return 1.0
    
        def p(self,x,y):
            return 1.0
    "*************************************************************************"
    T = 3; Lx=1; Ly=1; Nx=10; Ny=10
    b = 0.0; A = 0.04; w=pi;
    BC = "neumann"
    versions = ["vec"]
#    versions = ["vec", "scalar" ]
    animate_ue = False
    
    
    
    dtValues = array([0.01])

    
    for dt in dtValues: 
        for version in versions:
            problem = case_cubicSolution(b,A,w,Lx,Ly)
            
            #Run solver and visualize u at each time level
            u, x, y, t = wm.viz(problem, Lx=Lx, Ly=Ly, Nx=Nx, Ny=Ny,
                                dt=dt, T=T, BC = BC, version=version, 
                                animate=True)
            
            xv = x[:,newaxis]          # for vectorized function evaluations
            yv = y[newaxis,:]
            ue = 0*u
            
            for tn in t:
                ue[:,:]  = problem.exactSolution(xv,yv,tn)
                if animate_ue and dt==dtValues.min(): wm.plot_u(ue,x,y,tn)
            
            difference = abs(ue - u).max()  # max deviation
                       
            if not nt.assert_almost_equal(difference, 0, places=14):
                print version + ": ", "test_cubicSolution succeeded!"
 
            
                    
"*****************************************************************************"    
if __name__ == '__main__':
    test_constantSolution()
    test_standingUndamped()
    test_cubicSolution()