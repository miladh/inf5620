# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 11:49:56 2013

@author: Milad H. Mobarhan
"""
import sys
sys.path.append("..")
sys.path.append(".")

from pylab import *
import nose.tools as nt
import waveMotion as wm
import time

def convergence_rates(h, E):
    r = [log(E[i-1]/E[i])/log(h[i-1]/h[i])
    for i in range(1, len(h))]
    return r
"*****************************************************************************" 
def plot_truncationError(h,E):
    plt.figure(figsize=(8, 6))
    plt.loglog(h, E)
    plt.xlabel("$\log_{10}(h)$",fontsize=20)
    plt.ylabel("$\log_{10}(E)$",fontsize=20)
    plt.title("Estimated truncation error",fontsize=16)
    plt.tight_layout()
    
"*****************************************************************************"
def test_constantSolution():
    """
    Test problem where u=I is the exact solution, to be
    reproduced (to machine precision) by ady relevant method.
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
    "*************************************************************************"
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


"*****************************************************************************"
def test_plugwaveSolution():
    """
    Verification: Plug wave solution, constant velocity, no damping,
            I(x) is constant in some region of  the domain and 
            zero elsewhere. Check that an initial plug is correct 
            back after one period.
    """
    "*************************************************************************"
    class case_plugwaveSolution(wm.Problem):
        """
        Case:
            Plug wave solution, constant velocity, no damping,
            I(x) is constant in some region of  the domain and 
            zero elsewhere.            
        """
        def __init__(self, b, sigma, Lx, Ly, plug=None):    
            self.b = b; self.plug = plug
            self.Lx, self.Ly = Lx, Ly
            self.c = Lx/2.0

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
                    if abs(x[i,0]-c) > sigma:
                        I[i,:] = 0.0
                    else:
                        I[i,:] = 1.0
                return I  
            else:
                return 0 if abs(x-self.c) > sigma else 1
        
        def Iy(self,x,y,c):
            if isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
                I = zeros((y.shape[0],y.shape[1]))
                for i in range(1,y.shape[1]):
                    if abs(y[0,i]-c) > sigma:
                        I[:,i] = 0.0
                    else:
                        I[:,i] = 1.0
                return I  
            else:
                return 0 if abs(y-self.c) > sigma else 1
    
            
        def V(self,x,y): 
            return 0.0
    
        def f(self,x,y,t):     
            return 0.0
            
        def q(self,x,y):
            return 1
    
        def p(self,x,y):
            return 1.0
    "*************************************************************************"
    def assert_no_error(u, x, y, t):
        xv = x[:,newaxis]      # for vectorized function evaluations
        yv = y[newaxis,:]
        u0 = 0*u
        u0 = problem.I(xv,yv)
        diff = abs(u - u0).max()   
        nt.assert_almost_equal(diff, 0, places=14)

    print "--------------test plug wave solution---------------"   
    
    dt = dx = dy = 0.1; T = Lx = Ly = 1; 
    b=0; sigma = 0.05; plugs = ["x","y"]
    BC = "neumann" ; 
    versions = ["vec","scalar"]
    
    for version in versions:
        for plug in plugs:
            problem = case_plugwaveSolution(b,sigma,Lx,Ly,plug=plug)
            
            #Run solver and visualize u at each time level
            u, x, y, t, cpu = wm.solver(problem, Lx=Lx, Ly=Ly, dx=dx, dy=dy, 
                     dt=dt, T=T,BC = BC, version=version, 
                     user_action=None)   
            
            assert_no_error(u,x,y,t)

            print version + "-" + plug + ":","test_plugwaveSolution succeeded!"
            
"*****************************************************************************"
def test_standingUndamped():
    """
    Verification: standing, undamped waves, constant velocity, no source term.
    Controling the convergence  rate, using standing, undamped waves.
    
    """
    "*************************************************************************"
    class case_standingUndamped(wm.Problem):
        """
        Case:
            standing, undamped waves,
            
            ue = A*cos(kx*x)*cos(ky*y)*cos(w*t)
        """
        def __init__(self, A, w, kx,ky):    
            self.b = 0.0
            self.A = A ; self.w = w
            self.kx, self.ky = kx, ky
            self.e_max =0.0

            
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
    def max_error(u, x, y, t, n):
        xv = x[:,newaxis]      # for vectorized function evaluations
        yv = y[newaxis,:]
        ue = 0*u

        ue[:,:] = problem.exactSolution(xv,yv,t[n])                             
#        print abs(u - ue).max()
#        time.sleep(2)
#        wm.plot_u(ue,x,y,t,n)
#        wm.plot_u(u,x,y,t,n)
        problem.e_max = max(problem.e_max,abs(u - ue).max())

    print "------------------test standing undamped----------------"   
    dt_0=0.5; h0 = 1.0
    T = 50; Lx=20.0; Ly=20.0;
    A = 1.0; kx=1*pi/Lx; ky= 1.0*pi/Ly
    BC = "neumann"; makePlot = 1
#    versions = ["vec","scalar"]
    versions = ["vec"]

    for version in versions:  
        eValues  = []
        hValues  = []
        for i in range(0,4):
            p = 2**(-i)             
            h  = p*h0; dt = p*dt_0;
            w = 2*pi/dt/30.0
            problem = case_standingUndamped(A,w,kx,ky)
            u, x, y, t, cpu = wm.solver(problem, Lx=Lx, Ly=Ly, dx=h, dy=h, 
                     dt=dt, T=T,BC = BC, version=version, 
                     user_action=max_error,safetyFactor=1.0)
                     
            eValues.append(problem.e_max)
            hValues.append(h)
           
#            print "dt=", dt, " dx=", dx, " dy=", dy
            print version , "error= ", problem.e_max           
           
        r = convergence_rates(hValues, eValues)
        if makePlot: plot_truncationError(hValues, eValues)        
#        if not nt.assert_almost_equal(2,r[-1],places=1):
#            print version + ":","test_standingUndampedSolution succeeded!"

        
"*****************************************************************************" 
def test_standingDamped():
    """
    Verification: standing, damped waves, constant velocity, no source term.
    Controling the convergence  rate, using standing, damped waves.
    
    """
    "*************************************************************************"
    class case_standingDamped(wm.Problem):
        """
        Case:
            standing, damped waves,
            
            ue = [A*cos(w*t)+Bsin(w*t)]*exp(-b*t)*cos(kx*x)*cos(ky*y)
        """
        def __init__(self, b, A,kx,ky):    
            self.b = b; self.A = A;
            self.kx, self.ky = kx, ky
            self.e_max = 0.0
            
            q = self.q(0,0)       
            self.w = sqrt(self.kx**2 * q + self.ky**2 * q - self.b**2)
            self.B = self.A*self.b/self.w

            
        def exactSolution(self,x,y,t):
            b = self.b; A = self.A; B=self.B; w=self.w; kx=self.kx; ky=self.ky
            ue = (A*cos(t*w) + B*sin(t*w))*exp(-b*t)*cos(kx*x)*cos(ky*y)
            return ue
               
        def I(self,x,y):        
            return  self.exactSolution(x,y,0)
          
        def V(self,x,y):     
            b = self.b; A = self.A; B=self.B; w=self.w; kx=self.kx; ky=self.ky
            return (-A*b + B*w)*cos(kx*x)*cos(ky*y)
    
        def f(self,x,y,t):
            return 0.0
    
        def q(self,x,y):
            return 10.0
    
        def p(self,x,y):
            return 1.0
    "*************************************************************************"
    def max_error(u, x, y, t, n):
        xv = x[:,newaxis]      # for vectorized function evaluations
        yv = y[newaxis,:]
        ue = 0*u
        ue = problem.exactSolution(xv,yv,t[n])
        problem.e_max = max(problem.e_max,abs(u - ue).max())
  
    print "------------------test standing damped----------------"   
    dt_0=0.5; h0 = 5.0
    T = 50; Lx=20.0; Ly=20.0; b = 1.0
    A = 1.0; kx=10*pi/Lx; ky= 10.0*pi/Ly
    BC = "neumann"; makePlot = 1
#    versions = ["vec","scalar"]
    versions = ["vec"]

    
    for version in versions:
        eValues  = []
        hValues  = []

        for i in range(0,4):
            p = 2**(-i)             
            h  = p*h0; dt = p*dt_0;
            problem = case_standingDamped(b,A,kx,ky)
            u, x, y, t, cpu = wm.solver(problem, Lx=Lx, Ly=Ly, dx=h, dy=h, 
                     dt=dt, T=T,BC = BC, version=version, 
                     user_action=max_error)                     
           

            eValues.append(problem.e_max)
            hValues.append(dt)
            print version , "error= ", problem.e_max
            
        r = convergence_rates(hValues, eValues)
        if makePlot: plot_truncationError(hValues, eValues)        
        print r
#        if not nt.assert_almost_equal(2,r[-1],places=1):
#                    print version + ":","test_standingDampedSolution succeeded!"
                
                
"*****************************************************************************" 
def test_manufacturedSolution():
    """
    Verification: standing, damped waves, variable velocity, manufactured 
    source term. Controling the convergence  rate, using standing, damped waves.
    
    """
    "*************************************************************************"
    class case_manufacturedSolution(wm.Problem):
        """
        Case:
            standing, damped waves,
            
            ue = [A*cos(w*t)+Bsin(w*t)]*exp(-b*t)*cos(kx*x)*cos(ky*y)
        """
        def __init__(self, b,w,A,B,kx,ky):    
            self.b = b; self.A = A; self.B=B
            self.w = w
            self.kx, self.ky = kx, ky
            self.e_max = 0.0
            
        def exactSolution(self,x,y,t):
            b = self.b; A = self.A; B=self.B; w=self.w; kx=self.kx; ky=self.ky
            ue = (A*cos(t*w) + B*sin(t*w))*exp(-b*t)*cos(kx*x)*cos(ky*y)
            return ue
               
        def I(self,x,y):        
            return  self.exactSolution(x,y,0)
          
        def V(self,x,y):     
            b = self.b; A = self.A; B=self.B; w=self.w; kx=self.kx; ky=self.ky
            return (-A*b + B*w)*cos(kx*x)*cos(ky*y)
    
        def f(self,x,y,t):
            b = self.b; A = self.A; B=self.B; w=self.w; kx=self.kx; ky=self.ky
            cx = cos(kx*x); cy = cos(ky*y); sx = sin(kx*x)
            ct = cos(t*w); st = sin(t*w)
                        
            
            return exp(-b*t)*cy*(w*cx*((A*b - B*w)*st + (-A*w - B*b)*ct) \
                    + (A*ct + B*st)*(kx*(kx*x*cx + sx\
                    + ky**2*x*cx)))
    
        def q(self,x,y):
            return x
    
        def p(self,x,y):
            return 1.0
    "*************************************************************************"
    def max_error(u, x, y, t, n):
        xv = x[:,newaxis]      # for vectorized function evaluations
        yv = y[newaxis,:]
        ue = 0*u
        ue = problem.exactSolution(xv,yv,t[n])
        problem.e_max = max(problem.e_max,abs(u - ue).max())
    print "---------------test manufactured solution----------------"   
    dt_0=0.5; h0 = 1.0
    T = 50; Lx=20.0; Ly=20.0; b = 1.0
    A = 1.0; B = 1.0; kx=10.0*pi/Lx; ky= 10.0*pi/Ly
    BC = "neumann"; makePlot = 1
#    versions = ["vec","scalar"]
    versions = ["vec"]
    
    for version in versions:
        eValues  = []
        hValues  = []
        for i in range(0,4):
            p = 2**(-i)             
            h  = p*h0; dt = p*dt_0;
            w = 2*pi/dt/30.0
            problem = case_manufacturedSolution(b,w,A,B,kx,ky)
            u, x, y, t, cpu = wm.solver(problem, Lx=Lx, Ly=Ly, dx=h, dy=h, 
                     dt=dt, T=T,BC = BC, version=version, 
                     user_action=max_error)                     
           

            eValues.append(problem.e_max)
            hValues.append(dt)
            print version , "error= ", problem.e_max
            
        r = convergence_rates(hValues, eValues)
        if makePlot: plot_truncationError(hValues, eValues)        
        print r
        
#        if not nt.assert_almost_equal(2,r[-1],places=1):
#            print version + ":","test_manufacturedSolution succeeded!"
                
"*****************************************************************************"
if __name__ == '__main__':
#    test_constantSolution()
#    test_cubicSolution()
#    test_plugwaveSolution()
#    test_standingUndamped()
#    test_standingDamped()
#    test_manufacturedSolution()
