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
    print "------------------test constant solution----------------"    
    
    dt=0.01; T = 0.3; Lx=1; Ly=1; dx=0.1; dy=0.1 
    b=2; c=0.05
    BC = "neumann" ; pltool="mayavi"
    versions = ["vec","scalar"]
    animate_ue = False
    
    for version in versions:
        problem = case_constantSolution(b=b,c=c)
        
        #Run solver and visualize u at each time level
        u, x, y, t = wm.viz(problem, Lx=Lx, Ly=Ly, dx=dx, dy=dy, dt=dt, T=T, 
                   BC = BC, version=version, animate=False, pltool=pltool)
        
        xv = x[:,newaxis]          # for vectorized function evaluations
        yv = y[newaxis,:]
        ue = 0*u

        for t in t:
            ue[:,:]  = problem.exactSolution(xv,yv,t)
            if animate_ue:
                wm.plot_u(ue,x,y,t)
        difference = abs(ue - u).max()  # max deviation
        
        
        if not nt.assert_almost_equal(difference, 0, places=14):
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
    print "------------------test cubic solution-------------------"       
        
    dt = 0.01; T = 0.1; Lx=1; Ly=1; dx=0.1; dy=0.1
    b = 0.0;
    BC = "neumann"
    versions = ["vec", "scalar" ]
    animate_ue = False
    
 
    for version in versions:
        problem = case_cubicSolution(b,Lx,Ly,dx,dy)
        
        #Run solver and visualize u at each time level
        u, x, y, t = wm.viz(problem, Lx=Lx, Ly=Ly, dx=dx, dy=dy,
                            dt=dt, T=T, BC = BC, version=version, 
                            animate=False)
        
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
    print "--------------test plug wave solution---------------"   
    dt = dx = dy = 0.1; T = Lx = Ly = 1; 
    b=0; sigma = 0.05; plugs = ["x","y"]
    BC = "neumann" ; pltool="mayavi"
    versions = ["vec","scalar"]
    
    for version in versions:
        for plug in plugs:
            problem = case_plugwaveSolution(b,sigma,Lx,Ly,plug=plug)
            
            #Run solver and visualize u at each time level
            u, x, y, t = wm.viz(problem, Lx=Lx, Ly=Ly, dx=dx, dy=dy, dt=dt, T=T, 
                       BC = BC, version=version, animate=False, pltool=pltool)
            
            xv = x[:,newaxis]          # for vectorized function evaluations
            yv = y[newaxis,:]
            ue = 0*u
 
            ue[:,:]  = problem.exactSolution(xv,yv,t)        
            difference = abs(ue - u).max()  # max deviation
                       
            if not nt.assert_almost_equal(difference, 0, places=14):
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
    print "------------------test standing undamped----------------"   
    
    dt_0=0.5; T = 3; Lx=10; Ly=10; dx_0=1.0; dy_0=1.0
    b = 0.0; A = 0.05; w=100.0; kx=1.0*pi/Lx; ky= 1.0*pi/Ly
    BC = "neumann" ; pltool="mayavi"
    versions = ["vec","scalar"]
    animate_ue = False

    for version in versions:
        problem = case_standingUndamped(b,A,w,kx,ky)
        
        for i in range(0,4):
            r  = 2**(-i)
            dt = r*dt_0; 
            dx = r*dx_0; dy = r*dy_0
            u, x, y, t = wm.viz(problem, Lx=Lx, Ly=Ly, dx=dx, dy=dy, 
                                 dt=dt, T=T,BC = BC, version=version, 
                                 animate=False,pltool =pltool)
                                 
            xv = x[:,newaxis]      # for vectorized function evaluations
            yv = y[newaxis,:]
            ue = 0*u
        
            for tn in t:
                ue[:,:]  = problem.exactSolution(xv,yv,tn)
                if animate_ue: wm.plot_u(ue,x,y,tn)
            
            e = abs(u-ue).max()
            
        #        print "dt=", dt, " dx=", dx, " dy=", dy
            print version , "error= ", e/(dt/dx)**2


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
            return 1.0
    
        def p(self,x,y):
            return 1.0
    "*************************************************************************"
    print "------------------test standing damped----------------"   
    
    dt_0=0.01; T = 10; Lx=10; Ly=10; dx_0=0.1; dy_0=0.1
    b = 0.1; A = 0.05; kx=1.0*pi/Lx; ky= 1.0*pi/Ly
    BC = "neumann" ; pltool="mayavi"
#    versions = ["vec","scalar"]
    versions = ["vec"]
    animate_ue = True
    
    for version in versions:
        problem = case_standingDamped(b,A,kx,ky)
        for i in range(0,1):
            r  = 2**(-i)
            dt = r*dt_0; 
            dx = r*dx_0; dy = r*dy_0
            u, x, y, t = wm.viz(problem, Lx=Lx, Ly=Ly, dx=dx, dy=dy, 
                                 dt=dt, T=T,BC = BC, version=version, 
                                 animate=False,pltool =pltool)
                                 
            xv = x[:,newaxis]      # for vectorized function evaluations
            yv = y[newaxis,:]
            ue = 0*u
        
            for tn in t:
                ue[:,:]  = problem.exactSolution(xv,yv,tn)
                print ue.max()
                if animate_ue: wm.plot_u_mayavi(ue,x,y,tn,z_scale=0.05)
            
            e = abs(u-ue).max()
            
    #        print "dt=", dt, " dx=", dx, " dy=", dy
            print "error= ", e
  
if __name__ == '__main__':
#    test_constantSolution()
#    test_cubicSolution()
#    test_plugwaveSolution()
#    test_standingUndamped()
    test_standingDamped()
