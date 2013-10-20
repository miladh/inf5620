# -*- coding: utf-8 -*-
from pylab import *
import nose.tools as nt
import waveMotion as wm

class case_plugwaveSolution(wm.Problem):
        """
        Case:
            Plug wave solution, constant velocity, no damping,
            I(x) is constant in some region of  the domain and 
            zero elsewhere.            
        """
        def __init__(self, b, sigma, Lx, Ly, plug=None):    
            self.b = b; self.sigma = sigma; self.plug = plug
            self.Lx, self.Ly = Lx, Ly
            if plug=="x":            
                self.c = Lx/2.0
            elif plug=="y":
                self.c = Ly/2.0
            else:
                raise ValueError('plug=%s' % plug)  

        def exactSolution(self,x,y,t):
            return self.I(x,y)
            
        def I(self,x,y):     
            if self.plug == "x":
                return self.Ix(x,y,self.c)
            elif self.plug=="y":
                return self.Iy(x,y,self.c)
            else:
                raise NotImplementedError 
        
        def Ix(self,x,y,c):
            if isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
                I = zeros((x.shape[0],y.shape[1]))     
                for i in range(1,x.shape[0]):
                    if abs(x[i,0]-c) > self.sigma:
                        I[i,:] = 0.0
                    else:
                        I[i,:] = 1.0
                return I  
            else:
                return 0 if abs(x-self.c) > self.sigma else 1
        
        def Iy(self,x,y,c):
            if isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
                I = zeros((y.shape[0],y.shape[1]))
                for i in range(1,y.shape[1]):
                    if abs(y[0,i]-c) > self.sigma:
                        I[:,i] = 0.0
                    else:
                        I[:,i] = 1.0
                return I  
            else:
                return 0 if abs(y-self.c) > self.sigma else 1
    
            
        def V(self,x,y): 
            return 0.0
    
        def f(self,x,y,t):     
            return 0.0
            
        def q(self,x,y):
            return 1.0
    
        def p(self,x,y):
            return 1.0

def test_plugwaveSolution():
    """
    Verification: Plug wave solution, constant velocity, no damping,
            I(x) is constant in some region of  the domain and 
            zero elsewhere. Check that an initial plug is correct 
            back after one period.
    """
    def assert_no_error(u, x, y, t):
        xv = x[:,newaxis]      # for vectorized function evaluations
        yv = y[newaxis,:]
        u0 = 0*u
        u0 = problem.I(xv,yv)
        diff = abs(u - u0).max()   
        nt.assert_almost_equal(diff, 0, places=14)

    print "--------------test plug wave solution---------------"   
    
    dt = dx = dy = 1.0; T = Lx = Ly = 10; 
    b=0; sigma = 0.05; plugs = ["x","y"]
    BC = "neumann" ; 
    versions = ["vec","scalar"]
    
    for version in versions:
        for plug in plugs:
            problem = case_plugwaveSolution(b,sigma,Lx,Ly,plug=plug)
            
            #Run solver and visualize u at each time level
            u, x, y, t, cpu = wm.solver(problem, Lx=Lx, Ly=Ly, dx=dx, dy=dy, 
                     dt=dt, T=T,BC = BC, version=version, 
                     user_action=None,safetyFactor=2.0)   
                                          
            assert_no_error(u,x,y,t) 
            print version + "-" + plug + ":","test_plugwaveSolution succeeded!"
            
if __name__ == '__main__':
    test_plugwaveSolution()