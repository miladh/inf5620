# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 09:10:51 2013

@author: Milad H. Mobarhan
"""
from pylab import*
from dolfin import *
close("all")
            
"*****************************************************************************"
class Problem():
    """
    Superclass for nonlinear diffusion problems:
            
        p * u_t = -grad (a * grad(u)) + f(x,t)  

    with initial condition u(x,0)=u0, for t in the time interval
    (0,T]. The time interval is divided into time steps of
    length dt.
    """
                     
    def a(self,u):        
        raise NotImplementedError
      
    def ue(self):     
        raise NotImplementedError

    def f(self,x,t):
        raise NotImplementedError 
        
    def p(self,t = 0):        
        raise NotImplementedError
        
              
            
"*****************************************************************************"
def runSolver(problem, T, dt, domain, makePlot = False):
    
    # Space and basis funcntion:
    domainType = [UnitIntervalMesh, UnitSquareMesh, UnitCubeMesh] 
    
    if(len(domain)==1):
        mesh = domainType[0](domain[0])
        
    elif(len(domain)==2):
        mesh = domainType[1](domain[0],domain[1])
        
    elif(len(domain)==3):
        mesh = domainType[2](domain[0],domain[1],domain[2]) 
        
    else:
        raise ValueError
    
    V = FunctionSpace(mesh, 'Lagrange', 1)
    
    
    #Problem
    alpha = problem.a   
    p = problem.p()
    
    
    #Initial condition
    u0 = problem.ue()
    u_1 = interpolate(u0, V)

    
    # Define variational problem
    u = TrialFunction(V)
    v = TestFunction(V)
    f = problem.f()
    
    a = u*v*dx + dt/p*alpha(u_1)*inner(nabla_grad(u), nabla_grad(v))*dx
    L = (u_1 + dt/p*f)*v*dx
    
    u = Function(V)  # the unknown at a new time level
    u_e =  Function(V)
    b = None
    t = dt

    while t <= T:
            f.t = t
            u0.t = t
            A = assemble(a)
            b = assemble(L, tensor = b)
            solve(A, u.vector(), b)
            
            u_1.assign(u)
            u_e = interpolate(u0,V)

            if(makePlot):
                plot(u)
#                interactive()
                
            
            t += dt
        
    return u_e, u
    
"*****************************************************************************"
def define_command_line_options(parser=None):
    if parser is None:
        import argparse
        parser = argparse.ArgumentParser()
  
    parser.add_argument(
        '--dt', '--time_step_value', type=float, default=0.1, 
        help='time step value', metavar='dt')
              
    parser.add_argument(
        '--T', '--stop_time', type=float, default=10.0,
        help='end time of simulation', metavar='T')    
       
    parser.add_argument('--runtests', action='store_true', default=True,
                        help='run nosetests')
        
        
    return parser                           
"*****************************************************************************"
def main():
            
    # Read input from the command line
    parser = define_command_line_options()
    args = parser.parse_args()


    # Run nosetests
    if(args.runtests):
        import subprocess
        subprocess.call(["nosetests", "-s"])


if __name__ == '__main__':
    main()