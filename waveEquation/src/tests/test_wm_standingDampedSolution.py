# -*- coding: utf-8 -*-
from pylab import *
import nose.tools as nt
import waveMotion as wm
import verificationUtilities as vu

class case_standingDamped(wm.Problem):
    """
    Case:
        standing, damped waves,
        
        ue = [A*cos(w*t)+Bsin(w*t)]*exp(-d*t)*cos(kx*x)*cos(ky*y)
    """
    def __init__(self,b,c,A,kx,ky):    
        self.b = b; self.c=c; self.d = self.b*0.5; 
        self.A = A
        self.kx, self.ky = kx, ky
        self.e_max = 0.0
        
        q = self.q(0,0)       
        self.w = sqrt(self.kx**2 * q + self.ky**2 * q - self.d**2)
        self.B = self.A*self.b/self.w

        
    def exactSolution(self,x,y,t):
        d = self.d; A = self.A; B=self.B; w=self.w; kx=self.kx; ky=self.ky
        ue = (A*cos(t*w) + B*sin(t*w))*exp(-d*t)*cos(kx*x)*cos(ky*y)
        return ue
           
    def I(self,x,y):        
        return  self.exactSolution(x,y,0)
      
    def V(self,x,y):     
        d = self.d; A = self.A; B=self.B; w=self.w; kx=self.kx; ky=self.ky
        return (-A*d + B*w)*cos(kx*x)*cos(ky*y)

    def f(self,x,y,t):
        return 0.0

    def q(self,x,y):
        return self.c**2

    def p(self,x,y):
        return 1.0


def test_standingDamped():
    """
    Verification: standing, damped waves, constant velocity, no source term.
    Controlling the convergence  rate, using standing, damped waves.
    
    """
    def max_error(u, x, y, t, n):        
        xv = x[:,newaxis]      # for vectorized function evaluations
        yv = y[newaxis,:]
        ue = 0*u
        ue[:,:] = problem.exactSolution(xv,yv,t[n])                       
        problem.e_max = max(problem.e_max,abs(u[:,:] - ue[:,:]).max())
  
    print "------------------test standing damped----------------"   
    dt_0 = 0.5; h0 = 1.0
    b = 0.01; T = 1.0; Lx = 10.0; Ly = 10.0;
    A = 1.0; kx=1.*pi/Lx; ky= 1.*pi/Ly
    c = 1.1; 
    BC = "neumann"; makePlot = 0
    versions = ["vec","scalar"]

    
    for version in versions:
        eValues  = []
        hValues  = []

        for i in range(0,4):
            p = 2**(-i)             
            h  = p*h0; dt = p*dt_0;
            problem = case_standingDamped(b,c,A,kx,ky)
            u, x, y, t, cpu = wm.solver(problem, Lx=Lx, Ly=Ly, dx=h, dy=h, 
                     dt=dt, T=T,BC = BC, version=version, 
                     user_action=max_error,safetyFactor=1.0)                     
           

            eValues.append(problem.e_max)
            hValues.append(dt)
            
        r = vu.convergence_rates(hValues, eValues)
        if makePlot: vu.plot_truncationError(hValues, eValues)        
        if not nt.assert_almost_equal(2,r[-1],places=1):
                    print version + ":","test_standingDampedSolution succeeded!"
                
                
    
if __name__ == '__main__':
    test_standingDamped()
    

