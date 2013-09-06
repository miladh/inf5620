# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 09:10:51 2013

@author: Milad H. Mobarhan
"""
from pylab import*

"*****************************************************************************"
class Parameters:
    def set(self, **parameters):
        for name in parameters:
            self.prms[name] = parameters[name]

    def get(self, name):
        return self.prms[name]

    def define_command_line_options(self, parser=None):
        if parser is None:
            import argparse
            parser = argparse.ArgumentParser()

        for name in self.prms:
            tp = self.types[name] if name in self.types else str
            help = self.help[name] if name in self.help else None
            parser.add_argument(
                '--' + name, default=self.get(name), metavar=name,
                type=tp, help=help)

        return parser

    def init_from_command_line(self, args):
        for name in self.prms:
            self.prms[name] = getattr(args, name)
            
"*****************************************************************************"
class Integrator(Parameters):
    def __init__(self):
        self.prms  = dict(dt=0.1)
        self.types = dict(dt=float)
        self.help  = dict(dt='time step')
    
"*****************************************************************************"
class CNQuadratic(Integrator):
    """
    Computes u(t_n+1) from u(t_n), by using a Crank-Nicolson scheme
    for ODE of the type:
        
        u'(t) = -a(t)*|u(t)|u(t)+b(t),
    """ 
    def __call__(self,u,a,b):
        dt = self.get("dt")       
        tmp = (b - u*a*abs(u))/(1+dt*a*abs(u))       
        uNew = u + dt*tmp
                
        return uNew

"*****************************************************************************"       
class thetaRule(Integrator):
    """
    Computes u(t_n+1) from u(t_n) for ODE of the type:
        
        u'(t) = -a(t)*u(t)+b(t).
    
    theta=1 corresponds to the Backward Euler scheme, theta=0
    to the Forward Euler scheme, and theta=0.5 to the CrankNicolson
    """  
    def __init__(self):
        Integrator.__init__(self)
        self.prms.update(dict(theta=0.5))
        self.types.update(dict(theta=float))
        self.help.update(dict(theta='time discretization parameter'))
        

    def __call__(self,u,a,b):
        dt = self.get("dt")
        theta = self.get("theta") 
              
        uNew = ((1 - dt*(1-theta)*a)*u + \
        dt*(theta*b + (1-theta)*b))/\
        (1 + dt*theta*a)
        
        return uNew
"*****************************************************************************"
class ODESolver(Parameters):
    """
    Superclass for numerical methods solving scalar and vector ODEs

      du/dt = f(u, t)

    Attributes:
    t: array of time values
    u: array of solution values (at time points t)
    k: step number of the most recently computed solution
    """
    def __init__(self):
        self.prms  = dict(u0=0.0, dt=0.1, T=10)
        self.types = dict(u0=float, dt=float, T=float)
        self.help  = dict(u0='initial condition, u(0)',
                          dt='time step',
                          T='end time of simulation')        
    
    def advance(self):
        """Advance solution one time step."""
        raise NotImplementedError
        
        
    def solve(self):
       """
       Advance solution in time until t < T.
       """
       self.u = []
       self.t = []
       
       self.u.append(float(self.get("u0")))
       self.t.append(0)
       self.k = 0
       tNew = 0
       
       while tNew <= self.get("T"):
           uNew = self.advance()
           self.u.append(uNew)
           tNew = self.t[-1] + self.get("dt")
           self.t.append(tNew)
           self.k += 1
           
       return array(self.u), array(self.t)
       
"*****************************************************************************"
class Problem(ODESolver):
    """
    Solve
    
        u'(t) = -a*u(t)+b,       if Re < 1
        
        u'(t) = -a*|u(t)|u(t)+b, if Re > 1

    with initial condition u(0)=I, for t in the time interval
    (0,T]. The time interval is divided into time steps of
    length dt.
    """
    def __init__(self):
        ODESolver.__init__(self)
        self.prms.update(dict(r=0.11, m = 0.43, mu=8.9e-4, rho=1000, Cd=0.45))
        self.types.update(dict(r=float, m=float, mu=float, rho=float, Cd=float))
        self.help.update(dict(r='radius of the body',
                          m   ='mass of the body',
                          mu  ='dynamic viscosity of the fluid',
                          rho ='density of the fluid',
                          Cd  ="drag coefficient" ))
                 
    def advance(self):
        u,k,t = \
        self.u[-1], self.k, self.t[-1]
        
        Re = self.ReynoldsNumber(u)
        
        if Re < 1: 
            integrator = thetaRule() 
            return integrator(u,self.a(Re,t),self.b(t))
        else:
            integrator = CNQuadratic() 
            return integrator(u,self.a(Re,t),self.b(t))
            
    
    def a(self,Re,t):
        
        #Constants:
        r = self.get("r")            
        m = self.get("m") 
        mu = self.get("mu") 
        Cd = self.get("Cd")
        
        A = pi*r**2
            
        if Re < 1:  
            return 0.5*Cd*A/m
        else:
            return 6*pi*r*mu/m
        
    def b(self,t):
        
        #Constants:
        g = 9.81         #m/s^2 
        r = self.get("r")            
        m = self.get("m")   
        rho = self.get("rho")
        
        V = 4.0/3*pi*r**3
        rhoBody = float(m/V)
                 
        return g*(rho/rhoBody - 1)
        
    def ReynoldsNumber(self,u):
        #Constants:
        r = self.get("r")            
        mu = self.get("mu") 
        
        return 2*r*abs(u)/mu 
        
        
#    def f(self,u,t,Re):
#        Re = ReynoldsNumber(u)
#        a  = a(Re,t)
#        b  = b(t) 
#        
#        return -a*u*abs(u) + b
        
"*****************************************************************************"
class Visualizer:
    def __init__(self, problem):
        self.problem = problem

    def plot(self, include_exact=True, plt=None):
        """
        Add solver.u curve to the plotting object plt,
        and include the exact solution if include_exact is True.
        This plot function can be called several times (if
        the solver object has computed new solutions).
        """
        if plt is None:
            import matplotlib.pyplot as plt

        plt.plot(self.problem.t, self.problem.u, '--o')
        plt.hold('on')
#        theta2name = {0: 'FE', 1: 'BE', 0.5: 'CN'}
#        name = theta2name.get(self.solver.theta, '')
#        legends = ['numerical %s' % name]
#        if include_exact:
#            t_e = linspace(0, self.problem.T, 1001)
#            u_e = self.problem.exact_solution(t_e)
#            plt.plot(t_e, u_e, 'b-')
#            legends.append('exact')
#        plt.legend(legends)
        plt.xlabel('t')
        plt.ylabel('u')
#        plt.title('theta=%g, dt=%g' %
#                  (self.solver.theta, self.solver.dt))
#        plt.savefig('%s_%g.png' % (name, self.solver.dt))
        return plt
"*****************************************************************************"
def main():
    
    problem = Problem()
    viz = Visualizer(problem)

    # Read input from the command line
    parser = problem.define_command_line_options()
    args = parser.parse_args()
    problem.init_from_command_line(args)

    # Solve and plot
    u,t = problem.solve()  
    viz.plot()    
"*****************************************************************************"

if __name__ == '__main__':
    main()