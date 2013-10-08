# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 11:46:19 2013

@author: Milad H. Mobarhan
"""
from pylab import*
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
plt.ion()  # interactive mode on
import time;
close("all")
    
"*****************************************************************************"
def solver(problem, Lx, Ly, dx, dy, dt, T,   BC = None, version = None,
            user_action=None):
    """
    Solve 
    
        p*u_tt + b *u_t = div(q div(u) ) + f 
        
    on (0,L_x)x(0,L_y) in time domain (0,T].
    """
    
    if BC == 'dirichlet':
        BC_type = dirichlet_BC
    elif BC == 'neumann': 
        BC_type = neumann_BC
    else:
        raise NotImplementedError     
        
    
    if version == 'scalar':
        advance = advance_scalar
    elif version == 'vec': 
        advance = advance_vectorized
    else:
        raise NotImplementedError 
        
    
    x = arange(-dx, Lx+2*dx, dx)
    y = arange(-dy, Ly+2*dy, dy)
    
    Nx = len(x)-3
    Ny = len(y)-3
 

    
    xv = x[:,newaxis]          # for vectorized function evaluations
    yv = y[newaxis,:]
    
    Nt = int(round(T/float(dt)))
    t = linspace(0, Nt*dt, Nt+1)    # mesh points in time
    
    
    hx2 = (dt/dx)**2     # help variable
    hy2 = (dt/dy)**2     # help variable
        

    u   = zeros((Nx+3,Ny+3))   # solution array
    u_1 = zeros((Nx+3,Ny+3))   # solution at t-dt
    u_2 = zeros((Nx+3,Ny+3))   # solution at t-2*dt
    
    Ix = range(1, u.shape[0]-1) #indices for the real physical points
    Iy = range(1, u.shape[1]-1)
    It = range(0, t.shape[0])    
    
    t0 = time.clock()          # for measuring CPU time    
    
    # Load initial condition into u_1
    if version == 'scalar':
        for i in Ix:
            for j in Iy:
               u_1[i,j] = problem.I(x[i], y[j])  
    else: # use vectorized version
        u_1[:,:] = problem.I(xv, yv)
    
    # set ghost values
    u_1 = BC_type(u_1, Ix, Iy)
           
      
    if user_action is not None:
        user_action(u_1[1:-1,1:-1], x[1:-1], y[1:-1], t[0])
        
        
    # Special formula for first time step
    if version == 'scalar':
        u = advance(problem, u, u_1, u_2, x, y, t[0], hx2, hy2, dt, 
                step1=True, setBC = BC_type)
    else:
        u = advance(problem, u, u_1, u_2, xv, yv, t[0], hx2, hy2, dt, 
                step1=True, setBC = BC_type)
        
        
    if user_action is not None:
        user_action(u[1:-1,1:-1], x[1:-1], y[1:-1], t[1])

    u_2[:,:], u_1[:,:]= u_1, u 
    
    for n in It[1:-1]:
        if version == 'scalar':
            u = advance(problem, u, u_1, u_2, x, y, t[n],
                    hx2, hy2, dt, setBC = BC_type)
        else: 
            u = advance(problem, u, u_1, u_2, xv, yv, t[n],
                    hx2, hy2, dt, setBC = BC_type)
                            
        if user_action is not None:
            if user_action(u[1:-1,1:-1], x[1:-1], y[1:-1],t[n+1]):
                break

        u_2[:,:], u_1[:,:] = u_1, u


    cpu_time = time.clock() - t0
    
    return u[1:-1,1:-1], x[1:-1], y[1:-1], t, cpu_time
    
"*****************************************************************************"
def neumann_BC(u,Ix,Iy):
    """
    Set Neumann boundary conditions
    """
    i = Ix[0]          # x=0 boundary
    for j in range(0,u.shape[1]): 
        u[i-1,j] = u[i+1,j]
    
    i = Ix[-1]         # x=Lx boundary
    for j in range(0,u.shape[1]): 
        u[i+1,j] = u[i-1,j]
    
    j = Iy[0]          # y=0 boundary
    for i in range(0,u.shape[0]): 
        u[i,j-1] = u[i,j+1]
    
    j = Iy[-1]         # y=Ly boundary
    for i in range(0,u.shape[0]): 
        u[i,j+1] = u[i,j-1]
    
    return u
"*****************************************************************************"
def dirichlet_BC(u,Ix,Iy):
    """
    Set Dirichlet boundary conditions
    """
    i = Ix[0]       # x=0 boundary
    for j in Iy: u[i,j] = 0

    i = Ix[-1]     # x=Lx boundary 
    for j in Iy: u[i,j] = 0
    
    j = Iy[0]      # y=0 boundary
    for i in Ix: u[i,j] = 0
    
    j = Iy[-1]    # y=Ly boundary
    for i in Ix: u[i,j] = 0
    
    return u

    
"*****************************************************************************"
def advance_scalar(problem, u, u_1, u_2, x, y, t, 
            hx2, hy2, dt, step1=False, setBC = None):
                      
    Ix = range(1, u.shape[0]-1)
    Iy = range(1, u.shape[1]-1)
    dt2 = dt**2
    
    if step1:
        D1 = 0.0; D2=1.0 
    else:
        D1 = 1.0; D2=0.0      
        
    for i in Ix:
        for j in Iy:
            qij = problem.q(x[i], y[j])
            qpi = (problem.q(x[i+1], y[j]) + qij)*0.5
            qmi = (qij + problem.q(x[i-1], y[j]))*0.5
            qpj = (problem.q(x[i], y[j+1]) + qij)*0.5
            qmj = (qij + problem.q(x[i], y[j-1]))*0.5
                        
            uij = u_1[i,j]
            u_x = qpi*(u_1[i+1,j] - uij) - qmi*(uij - u_1[i-1,j])
            u_y = qpj*(u_1[i,j+1] - uij) - qmj*(uij - u_1[i,j-1])
            
            pij = problem.p(x[i], y[j])
            fac = problem.b*float(dt) / (2*pij)

            
            u[i,j] = 2*u_1[i,j]+\
                 (D1*u_2[i,j] - D2*2*dt*problem.V(x[i], y[j]))*(fac-1) +\
                 dt2/pij *problem.f(x[i], y[j], t) +\
                 hx2/pij * u_x + hy2/pij * u_y
    
    if step1:
        u[1:-1,1:-1] /= 2
    else:
        u[1:-1,1:-1] /= (1+fac)

    # Set Boundary conditions
    u = setBC(u,Ix,Iy)   

    return u
"*****************************************************************************"
def advance_vectorized(problem, u, u_1, u_2, x, y, t, 
            hx2, hy2, dt, step1=False, setBC = None):
       
    Ix = range(1, u.shape[0]-1)
    Iy = range(1, u.shape[1]-1)               
    dt2 = dt**2
    
    if step1:
        D1 = 0.0; D2=1.0 
    else:
        D1 = 1.0; D2=0.0      
        
    qij = problem.q(x[1:-1,:], y[:,1:-1])
    qpi = (problem.q( x[2:,:], y[:,1:-1]) + qij)*0.5
    qmi = (qij + problem.q(x[:-2,:], y[:,1:-1]))*0.5
    qpj = (problem.q( x[1:-1,:], y[:,2:]) + qij)*0.5
    qmj = (qij + problem.q(x[1:-1,:], y[:,:-2]))*0.5
                
    uij = u_1[1:-1,1:-1] 
    u_x = qpi*(u_1[2:,1:-1] - uij) - qmi*(uij - u_1[:-2,1:-1])
    u_y = qpj*(u_1[1:-1,2:] - uij) - qmj*(uij - u_1[1:-1,:-2])
    
    pij = problem.p(x[1:-1,:], y[:,1:-1])
    fac = problem.b*float(dt)/(2*pij)
    
    
    u[1:-1,1:-1] = 2*u_1[1:-1,1:-1]+\
         (D1*u_2[1:-1,1:-1] - D2*2*dt*problem.V(x[1:-1,:], y[:,1:-1]))*\
         (fac-1) +dt2/pij *problem.f(x[1:-1,:], y[:,1:-1], t) +\
         hx2/pij * u_x + hy2/pij * u_y
                      
    if step1:
        u[1:-1,1:-1] /= 2
    else:
        u[1:-1,1:-1] /= (1+fac)
    
    # Set Boundary conditions
    u = setBC(u,Ix,Iy)   

    return u
"*****************************************************************************"
def plot_u(u, x, y, t):
    """
    user_action function for solver.
    """
    X, Y = meshgrid(x, y)
    clf()
    ax = gca(projection='3d')
    ax.plot_wireframe(X, Y, u,rstride=1, cstride=1, cmap=cm.jet,
                    linewidth=0.1, antialiased=False)
    
    ax.set_zlim(-0.1,0.1)
    ax.set_xlabel('$X$', fontsize=15)
    ax.set_ylabel('$Y$', fontsize=15)
    ax.set_zlabel('$u(x,y)$', fontsize=15)
    plt.tight_layout()
    plt.draw()       
             
    # Let the initial condition stay on the screen for 2
    # seconds, else insert a pause of 0.2 s between each plot
    time.sleep(2) if t == 0 else time.sleep(0.0)
    

"*****************************************************************************"
def viz(problem, Lx, Ly, dx, dy, dt, T, 
        version=None ,BC=None, animate=True):
    """
    Run solver and visualize u at each time level.
    """
    
    if animate:
        user_action = plot_u
    else: 
        user_action =  None
        
    u, x, y, t, cpu = solver(problem, Lx, Ly, dx, dy, dt, T, BC, version,
                            user_action)

#    print "CPU time: ", cpu ,"\n"
    
    return u, x, y, t
    
    

"*****************************************************************************"
class Problem():
    """
    Superclass for problems with PDEs of the type
            
        p*u_tt + b *u_t = div(q div(u) ) + f   

    where u is a function of x,y and t, with initial condition 
        
        u(x,y,0)   = I(x,y), 
        u_t(x,y,0) = V(x,y)

    for t in the time interval (0,T]. 
    """
                     
    def I(self,x,y):        
        raise NotImplementedError
      
    def V(self,x,y):     
        raise NotImplementedError

    def f(self,x,y,t):
        raise NotImplementedError 

    def q(self,x,y):
        raise NotImplementedError 

    def p(self,x,y):
        raise NotImplementedError 
        
"*****************************************************************************"
class SimpleWave(Problem):
    """
    Problem:
        Simple wave motion
    """
    def __init__(self, b):    
        self.b = b
           
    def I(self,x,y):  
        return 0.05*cos(pi*x)*cos(pi*y);
      
    def V(self,x,y):  
        return 0.0

    def f(self,x,y,t):
        return 0.0

    def q(self,x,y):
        return 1.0

    def p(self,x,y):
        return 1.0
        
"*****************************************************************************"
def define_command_line_options(parser=None):
    if parser is None:
        import argparse
        parser = argparse.ArgumentParser()

    parser.add_argument(
        '--Lx', '--upper_boundary_x', type=float, 
        default=1.0, help='upper boundary in x direction',metavar='Lx')
    
    parser.add_argument(
        '--Ly', '--upper_boundary_y', type=float, 
        default=1.0, help='upper boundary in y direction',metavar='Ly')
    
    parser.add_argument(
        '--dx', '--step_lenght_x', type=int, default=0.1,
        help='step length in the x direction',metavar='dx')
    
    parser.add_argument(
        '--dy', '--step_lenght_y', type=int, default=0.1, 
        help='step length in the y direction',metavar='dy')   
   
    parser.add_argument(
        '--dt', '--time_step_value', type=float, default=0.01, 
        help='time step value', metavar='dt')
        
    parser.add_argument(
        '--T', '--stop_time', type=float, default=10.0,
        help='end time of simulation', metavar='T')    
    
    parser.add_argument(
        '--b', '--damping_factor', type=float, default=0.0,
        help='damping factor', metavar='b')   
        
    parser.add_argument(
        '--version', '--version', type=str, default="vec",
        help='scalar or vectorized calculation', metavar='version')   
        
    parser.add_argument(
        '--BC', '--boundary_condition', type=str, default="neumann",
        help='type of boundary condition', metavar='BC')  
                
    parser.add_argument('--animate', action='store_true', default=True,
                        help='make animation')
                        
                        
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


    #Set up problem
#    problem = SimpleWave(args.b)
#
#    #Run solver and visualize u at each time level
#    viz(problem, args.Lx, args.Ly, args.dx, args.dy, args.dt, args.T, 
#        args.version,args.BC, args.animate)
 
    
    
    
"*****************************************************************************"

if __name__ == '__main__':
    main()