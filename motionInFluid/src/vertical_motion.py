# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 09:10:51 2013

@author: Milad H. Mobarhan
"""
from pylab import*


def CNQuadratic_Integrator(u,a,b,dt):
    """
    Computes u(t_n+1) from u(t_n), by using a Crank-Nicolson scheme
    for ODE of the type:
        
        u'(t) = -a*|u(t)|u(t)+b,
    """  
    dt   = float(dt)     # avoid integer division 
    uNew = (u + dt*b)/(1+dt*a*abs(u))
    
    return uNew
    
    
def thetaRule_Integrator(u,a,b,dt,theta):
    """
    Computes u(t_n+1) from u(t_n), by using a Crank-Nicolson scheme
    for ODE of the type:
        
        u'(t) = -a*u(t)+b.
    
    theta=1 corresponds to the Backward Euler scheme, theta=0
    to the Forward Euler scheme, and theta=0.5 to the CrankNicolson
    """   
    dt   = float(dt)     # avoid integer division                 
    uNew = (u*(1 - (1-theta)*a*dt)+b*dt)/(1 + theta*dt*a)
    
    return uNew

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
class Solver(Parameters):
    """
    Physical parameters for the problem u'=-a*u, u(0)=I,
    with t in [0,T].
    """
    def __init__(self):
        self.prms  = dict(I=1, dt=0.1, T=10, theta=0.5)
        self.types = dict(I=float, dt=float, T=float,theta=float )
        self.help  = dict(I='initial condition, u(0)',
                          dt='time step',
                          T='end time of simulation',
                          theta='time discretization parameter')
    
    def solve(self):
        """
        Solve
        
            u'(t) = -a*u(t)+b,       if Re < 1
            
            u'(t) = -a*|u(t)|u(t)+b, if Re > 1

        with initial condition u(0)=I, for t in the time interval
        (0,T]. The time interval is divided into time steps of
        length dt.
        """
        
        
        dt = float(self.get("dt"))             # avoid integer division
        Nt = int(round(self.get("T")/dt))      # no of time intervals
        T = Nt*dt                  # adjust T to fit time step dt
        
        
        #Constants:
        Cd = 0.45
        g = 9.81  #m/s^2
        r = 0.11  # m
        m = 0.43  #kg 
           
        
        
        mu    = 8.9e-4   #Pa s
        rho   = 1000     #kg/m^3
        
        
        V = 4.0/3*pi*r**3
        A = pi*r**2
        rhoBody = float(m/V)
        
        b = g*(rho/rhoBody - 1)
        
        
        #initializing
        u = zeros(Nt+1)            # array of u[n] values
        t = linspace(0, T, Nt+1)   # time mesh
        u[0] = self.get("I")                  # assign initial condition
        
        #solve
        for n in range(0, Nt): 
            Re = 2*r*abs(u[n])/mu   
            print Re
            
            if Re < 1:
                a = 0.5*Cd*A/m
                u[n+1] = thetaRule_Integrator(u[n],a,b,dt,0.5)
            else:
                a = 6*pi*r*mu/m
                u[n+1] = CNQuadratic_Integrator(u[n],a,b,dt)
                
        plot(t,u, 'o')
        xlabel("Time [s]")
        ylabel("Velocity [m/s]")


def main():

    solver = Solver()

    # Read input from the command line
    parser = solver.define_command_line_options()
    args = parser.parse_args()
    solver.init_from_command_line(args)

    # Solve and plot
    solver.solve()


if __name__ == '__main__':
    main()











