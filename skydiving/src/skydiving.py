# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 09:10:51 2013

@author: Milad H. Mobarhan
"""
from pylab import*
close("all")
            
"*****************************************************************************"
class ODESolver():
    """
    Superclass for numerical methods solving scalar ODEs

      du/dt = f(u, t)
    """
    def __init__(self,problem, u0, dt, T):  
        self.problem, self.u0, self.dt, self.T = \
                                                problem, u0, dt ,T
   
    def advance(self):
        """Advance solution one time step."""
        raise NotImplementedError
        
        
    def solve(self):
       """
       Advance solution in time until t < T.
       """
       self.u = []
       self.t = []
       
       self.u.append(float(self.u0))
       self.t.append(0)
       self.dt = float(self.dt)            # avoid integer division
       Nt = int(round(self.T/self.dt))     # no of time intervals
       self.T = Nt*self.dt                 # adjust T to fit time step dt
       
       tNew = 0
       while tNew <= self.T:
           uNew = self.advance()
           self.u.append(uNew)
           tNew = self.t[-1] + self.dt
           self.t.append(tNew)
           
       return array(self.u), array(self.t)
       
"*****************************************************************************"
class Problem():
    """
    Superclass for problems with ODEs of the type
            
        u'(t) = f(u, t)  

    with initial condition u(0)=u0, for t in the time interval
    (0,T]. The time interval is divided into time steps of
    length dt.
    """
                     
    def a(self,t):        
        raise NotImplementedError
      
    def b(self):     
        raise NotImplementedError

    def f(self,u,t):
        raise NotImplementedError 
        
    def forces(self,u,t):
        raise NotImplementedError
              
              
"*****************************************************************************"
class skydiving(Problem):
    """
    Problem:
        Simulate parachuting- vertical motion of a body subject 
        to three different types of forces: 
        the gravity force, the drag force, and the buoyancy force. 
        ODE type:
            
            u'(t) = f(u, t)  

    where

        f(u, t) = -a(t)*|u(t)|u(t) + b(t),
    """
    def __init__(self, A, Ap, dt, dtp, m,  rho, Cd, Cdp, tp):
        self.g  = 9.81
        self.V  = 0.0664
        self.A, self.Ap, self.dt, self.dtp = \
                                            A, Ap, dt, dtp
        self.m, self.rho, self.Cd, self.Cdp, self.tp = \
                                                m, rho, Cd,Cdp, tp

        self.dA = (Ap-A)/(dtp/dt)
                            
    def a(self,t):        
        m, rho, Cd =  self.m, self.rho, self.Cd  
        
        if(t > self.tp):
            if(t < self.tp + self.dtp):
                self.A = self.A + self.dA
            Cd = self.Cdp
            A = self.A            
        else:
            A = self.A
                            
        return 0.5*Cd*rho*A/m

        
    def b(self,t):     
        A, m, rho, V, g =  self.A, self.m, self.rho, self.V, self.g
        rhoBody = float(m/V)  
        return -g*(rho/rhoBody - 1)

    def f(self,u,t):
        a  = a(t)
        b  = b(t) 
        
        return -a*u*abs(u) + b
        
    def forces(self,u,t):
        A, m, V,g, rho, Cd =  self.A, self.m, self.V,self.g, self.rho, self.Cd     
        Fg = 0 *array(t)+ m*g
        A = 0.5
        
        Fd = 0 *array(t)+ 0.5*Cd*rho*A*absolute(u)*u
        Fb = 0 *array(t)+ rho*g*V
        return Fg,Fd,Fb
"*****************************************************************************"
class CNQuadratic(ODESolver):
    """
    Computes u(t_n+1) from u(t_n), by using a Crank-Nicolson scheme with 
    geometeric average approximation,  for ODE of the type:
        
        u'(t) = -a(t)*|u(t)|u(t)+b(t).
        
    """ 

    def advance(self):
        u, dt  = self.u[-1], self.dt     
        
        a = self.problem.a(self.t[-1]+dt*0.5)
        b = self.problem.b(self.t[-1]+dt*0.5)
            
                
        uNew = (u + dt*b)/(1+dt*a*abs(u))
                
        return uNew
        

        
        
"*****************************************************************************"       
class Visualizer:
    def __init__(self, solver):
        self.solver = solver

    def plot(self, plt=None):
        """
        Add solver.u curve to the plotting object plt,
        and include the exact solution if include_exact is True.
        This plot function can be called several times (if
        the solver object has computed new solutions).
        """
        if plt is None:
            import matplotlib.pyplot as plt

        plt.plot(self.solver.t[::5], self.solver.u[::5], '--o')

        plt.xlabel('t')
        plt.ylabel('u')
        xlim(min(self.solver.t),max(self.solver.t))
        return plt    
        
    def plotForces(self, plt=None): 
        """
        Plot forces
        """
        if plt is None:
            import matplotlib.pyplot as plt
            
        forces = self.solver.problem.forces(self.solver.u,self.solver.t)

      
        plt.plot(self.solver.t[::5], forces[0][::5], label = "Gravity force")
        plt.plot(self.solver.t[::5], forces[1][::5], label = "Drag force")
        plt.plot(self.solver.t[::5], forces[2][::5], label = "Buoyancy force")
        plt.legend()
        plt.xlabel('time')
        plt.ylabel('Force')
        xlim(min(self.solver.t),max(self.solver.t))      
        return plt        

"*****************************************************************************"
def define_command_line_options(parser=None):
    if parser is None:
        import argparse
        parser = argparse.ArgumentParser()

    parser.add_argument(
        '--u0', '--initial_condition', type=float,default=0.0, 
        help='initial condition, u(0)',metavar='u0')
        
    parser.add_argument(
        '--dt', '--time_step_value', type=float,default=0.1, 
        help='time step value', metavar='dt')
        
    parser.add_argument(
        '--T', '--stop_time', type=float, default=80.0,
        help='end time of simulation', metavar='T')    
        
    parser.add_argument(
        '--m', '--mass', type=float, default=100.0,
        help='mass of the body', metavar='m')
        
    parser.add_argument(
        '--A', '--areal', type=float, default=0.5,
        help='cross-section areal of the body', metavar='A')
        
    parser.add_argument(
        '--Ap', '--arealp', type=float, default=44.0,
        help='cross-section areal when parachute is open', metavar='Ap')
          
    parser.add_argument(
        '--rho', '--density', type=float, default=1.0,
        help=' density of the fluid ', metavar='rho')    
        
    parser.add_argument(
        '--Cd', '--dragCoff', type=float, default=1.2,
        help='drag coefficient', metavar='Cd')
        
    parser.add_argument(
        '--Cdp', '--dragCoffp', type=float, default=1.8,
        help='drag coefficient, when parachute is open', metavar='Cdp')
        
    parser.add_argument(
        '--tp', '--parachuteOpens', type=float, default=60.0,
        help='the time where the parachute opens', metavar='tp')
        
    parser.add_argument(
        '--dtp', '--time_to_open_parachute', type=float, default=5.0,
        help='Time it takes to open the parachute', metavar='dtp')
        
        
    return parser
       
"*****************************************************************************"

def main():
        
    # Read input from the command line
    parser = define_command_line_options()
    args = parser.parse_args()
    
    #Set up problem solver, problem and vizualizer
    problem    = skydiving(args.A,args.Ap,args.dt,args.dtp,
                           args.m, args.rho, args.Cd,args.Cdp, args.tp)
    solver     = CNQuadratic(problem,args.u0, args.dt, args.T)
    viz        = Visualizer(solver)
    
    # Solve and plot
    u,t = solver.solve()  
    plt = viz.plot()
    plt.show()
    figure()
    pltforce = viz.plotForces()
    pltforce.show()
    
    
"*****************************************************************************"

if __name__ == '__main__':
    main()
    
    
    
    

