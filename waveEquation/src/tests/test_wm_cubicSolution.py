# -*- coding: utf-8 -*-
from pylab import *
import nose.tools as nt
import waveMotion as wm

class case_cubicSolution(wm.Problem):
        """
        Case:
            Cubic solution
            
            ue = X(x) Y(y) T(t)
        where
            X(x) = 2*x^3 -3*Lx*x^2
            Y(y) = 2*y^3 -3*Ly*y^2
            T(t) = t
            
        """
        def __init__(self, b, Lx,Ly, dx,dy):    
            self.b = b
            self.Lx, self.Ly = Lx, Ly
            self.dx, self.dy = dx, dy

        def X(self,x):
           Lx = self.Lx
           return (2*x**3 - 3 * Lx * x**2)
         
        def Y(self, y):
           Ly = self.Ly
           return (2*y**3 - 3 * Ly * y**2)
           
        def T(self,t):
            return t
            
        def exactSolution(self,x,y,t):
            return self.X(x)*self.Y(y)*self.T(t)
               
        def I(self,x,y):        
            return self.exactSolution(x,y,0)
          
        def V(self,x,y): 
            return self.X(x)*self.Y(y)
    
        def f(self,x,y,t):     
            q = self.q(x,y)
            Lx = self.Lx; Ly = self.Ly
            fx = (12 * x - 6 * Lx)*self.Y(y)
            fy = (12 * y - 6 * Ly)*self.X(x)
            # evaluate the f that fits the PDE
            f = -q*(fx + fy)*self.T(t)
        
            
            if isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
                # Array evaluation
                # Modify boundary values
                f[0,:]  -= 4*self.dx*self.T(t)*self.Y(y[0,:])*q # x=0
                f[-1,:] += 4*self.dx*self.T(t)*self.Y(y[0,:])*q # x=Lx
                f[:,0]  -= 4*self.dy*self.T(t)*self.X(x[:,0])*q # y=0
                f[:,-1] += 4*self.dy*self.T(t)*self.X(x[:,0])*q # x=Ly
            else:
                # Assume pointwise evaluation
                # Modify boundary values
                if x==0.0:
                    f-=4*self.dx*self.T(t)*self.Y(y)*q
                elif x==Lx:
                    f+=4*self.dx*self.T(t)*self.Y(y)*q
                if y==0.0:
                    f-=4*self.dy*self.T(t)*self.X(x)*q
                elif y==Ly:
                    f+=4*self.dy*self.T(t)*self.X(x)*q              
            return f
            
        def q(self,x,y):
            return 1.2
    
        def p(self,x,y):
            return 1.0

def test_cubicSolution():
    """
    Verification: cubic solution, constant velocity, with source term.
    Check that computed values equals ue within machine precision
    
    """

    def assert_no_error(u, x, y, t, n):
        xv = x[:,newaxis]      # for vectorized function evaluations
        yv = y[newaxis,:]
        ue = 0*u
        ue = problem.exactSolution(xv,yv,t[n])
        diff = abs(u - ue).max()   
        nt.assert_almost_equal(diff, 0, places=14)
   
    print "------------------test cubic solution-------------------"       
   
    dt = 0.01; T = 0.1; Lx=1; Ly=1; dx=0.1; dy=0.1
    b = 0.0;
    BC = "neumann"
    versions = ["vec", "scalar" ]

    
 
    for version in versions:
        problem = case_cubicSolution(b,Lx,Ly,dx,dy)
        
        #Run solver and visualize u at each time level
        u, x, y, t, cpu = wm.solver(problem, Lx=Lx, Ly=Ly, dx=dx, dy=dy, 
                     dt=dt, T=T,BC = BC, version=version, 
                     user_action=assert_no_error)    
                
                 
        print version + ": ", "test_cubicSolution succeeded!"
    
if __name__ == '__main__':
    test_cubicSolution()
    