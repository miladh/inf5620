# -*- coding: utf-8 -*-
from pylab import *
import nose.tools as nt
import waveMotion as wm
import verificationUtilities as vu

class case_manufacturedSolution(wm.Problem):
    """
    Case:
        standing, damped waves,
        
        ue = [A*cos(w*t)+Bsin(w*t)]*exp(-d*t)*cos(kx*x)*cos(ky*y)
        
        with source term.
    """
    def __init__(self, b,d,w,A,B,kx,ky):    
        self.b = b; self.A = A; self.B=B
        self.w = w; self.d = d
        self.kx, self.ky = kx, ky
        self.e_max = 0.0
        
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
        b = self.b; A = self.A; B=self.B; w=self.w; kx=self.kx; ky=self.ky
        d = self.d; cx = cos(kx*x); cy = cos(ky*y); sx = sin(kx*x)
        ct = cos(t*w); st = sin(t*w)
        
        return ((A*ct + B*st)*(kx*(kx*x*cx + sx)\
        + ky**2*x*cx) -((A*b*d - A*d**2 + A*w**2 - B*b*w + 2*B*d*w)\
        *ct + (A*b*w - 2*A*d*w + B*b*d - B*d**2 + B*w**2)*st)\
        *cx)*exp(-d*t)*cy
        

    def q(self,x,y):
        return x

    def p(self,x,y):
        return 1.0

def test_manufacturedSolution():
    """
    Verification: standing, damped waves, variable velocity, manufactured 
    source term. Controlling the convergence  rate, using standing, damped waves.
    
    """

    def max_error(u, x, y, t, n):
        xv = x[:,newaxis]      # for vectorized function evaluations
        yv = y[newaxis,:]
        ue = 0*u
        ue = problem.exactSolution(xv,yv,t[n])
        problem.e_max = max(problem.e_max,abs(u - ue).max())
        
    print "---------------test manufactured solution----------------"   
    
    dt_0 = 0.5; h0 = 1.0; w = 1.1
    b = 0.01; d =0.007; T = 1.0; Lx = 10.0; Ly = 10.0;
    A = 1.1; B = 1.2; kx=1.*pi/Lx; ky= 1.*pi/Ly
    BC = "neumann"; makePlot = 0
    versions = ["vec","scalar"] 
  
    for version in versions:
        eValues  = []
        hValues  = []
        for i in range(0,4):
            p = 2**(-i)             
            h  = p*h0; dt = p*dt_0;
            problem = case_manufacturedSolution(b,d,w,A,B,kx,ky)
            u, x, y, t, cpu = wm.solver(problem, Lx=Lx, Ly=Ly, dx=h, dy=h, 
                     dt=dt, T=T,BC = BC, version=version, 
                     user_action=max_error)                     
           

            eValues.append(problem.e_max)
            hValues.append(dt)
            
        r = vu.convergence_rates(hValues, eValues)
        if makePlot: vu.plot_truncationError(hValues, eValues)        
        
        if not nt.assert_almost_equal(2,r[-1],places=1):
            print version + ":","test_manufacturedSolution succeeded!"
            
if __name__ == '__main__':
    test_manufacturedSolution()