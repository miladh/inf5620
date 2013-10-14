# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from pylab import *
import nose.tools as nt
import waveMotion as wm
import verificationUtilities as vu

class case_standingUndamped(wm.Problem):
        """
        Case:
            standing, undamped waves,
            
            ue = A*cos(kx*x)*cos(ky*y)*cos(w*t)
        """
        def __init__(self, A,c, kx,ky):    
            self.b = 0.0
            self.A = A; self.c=c
            self.kx, self.ky = kx, ky
            self.e_max =0.0

            
        def exactSolution(self,x,y,t):
            w = sqrt(self.q(x,y)*(self.kx**2+self.ky**2))
            ue = self.A*cos(self.kx*x)*cos(self.ky*y)*cos(w*t)
            return ue
               
        def I(self,x,y):        
            return  self.exactSolution(x,y,0)
          
        def V(self,x,y):     
            return 0.0
    
        def f(self,x,y,t):
            return 0.0
    
        def q(self,x,y):
            return self.c**2

        def p(self,x,y):
            return 1.0


def test_standingUndamped():
    """
    Verification: standing, undamped waves, constant velocity, no source term.
    Controling the convergence  rate, using standing, undamped waves.
    
    """

    def max_error(u, x, y, t, n):
        xv = x[:,newaxis]      # for vectorized function evaluations
        yv = y[newaxis,:]
        ue = 0*u
        ue[:,:] = problem.exactSolution(xv,yv,t[n])                          
        problem.e_max = max(problem.e_max,abs(u[:,:] - ue[:,:]).max())

    print "------------------test standing undamped----------------"   
    
    dt_0 = 0.5; h0 = 1.0
    T = 1.0; Lx = 10.0; Ly = 10.0;
    A = 1.0; kx=1.*pi/Lx; ky= 1.*pi/Ly
    c = 1.1
    BC = "neumann"; makePlot = 1
    versions = ["vec","scalar"]

    for version in versions:  
        eValues  = []
        hValues  = []
        for i in range(0,4):
            p = 2**(-i)             
            h  = p*h0; dt = p*dt_0;
            problem = case_standingUndamped(A,c,kx,ky)
            u, x, y, t, cpu = wm.solver(problem, Lx=Lx, Ly=Ly, dx=h, dy=h, 
                     dt=dt, T=T,BC = BC, version=version, 
                     user_action=max_error,safetyFactor=1.0)
                     
            eValues.append(problem.e_max)
            hValues.append(h)  
           
        r = vu.convergence_rates(hValues, eValues)
        if makePlot: vu.plot_truncationError(hValues, eValues)        
        if not nt.assert_almost_equal(2,r[-1],places=1):
            print version + ":","test_standingUndampedSolution succeeded!"

    
if __name__ == '__main__':
    test_standingUndamped()
    
