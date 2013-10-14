# -*- coding: utf-8 -*-

from pylab import*
import time

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
def solver(problem, Lx, Ly, dx, dy, dt, T,   BC = None, version = None,
            user_action=None, safetyFactor=1.0):
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
        raise ValueError('BC=%s' % BC)     
        
    
    if version == 'scalar':
        advance = advance_scalar
    elif version == 'vec': 
        advance = advance_vectorized
    else:
        raise ValueError('version=%s' % version)
        
    
    x = arange(-dx, Lx+2*dx, dx)  #mesh points, including ghost points
    y = arange(-dy, Ly+2*dy, dy)  
    Nx = len(x); Ny = len(y)
 
    xv = x[:,newaxis]          # for vectorized function evaluations
    yv = y[newaxis,:]
    
    u   = zeros((Nx,Ny))   # solution array
    u_1 = zeros((Nx,Ny))   # solution at t-dt
    u_2 = zeros((Nx,Ny))   # solution at t-2*dt
    
    Ix = range(1, u.shape[0]-1) #indices for the real physical points
    Iy = range(1, u.shape[1]-1)

    # Ensure that stability criterion is satisfied
    dt = stabilityCriterion(problem,xv,yv,dx,dy,dt,safetyFactor)
    Nt = int(round(T/float(dt)))
    t = linspace(0, Nt*dt, Nt+1)    # mesh points in time
    
    Cx2 = (dt/dx)**2     # help variable
    Cy2 = (dt/dy)**2     # help variable
        
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
        user_action(u_1[1:-1,1:-1], x[1:-1], y[1:-1], t,0)
        
        
    # Special formula for first time step
    if version == 'scalar':
        u = advance(problem, u, u_1, u_2, x, y, t[0], Cx2, Cy2, dt, 
                step1=True, setBC = BC_type)
    else:
        u = advance(problem, u, u_1, u_2, xv, yv, t[0], Cx2, Cy2, dt, 
                step1=True, setBC = BC_type)
        
        
    if user_action is not None:
        user_action(u[1:-1,1:-1], x[1:-1], y[1:-1], t, 1)

    u_2[:,:], u_1[:,:]= u_1, u 
    
    for n in It[1:-1]:
        if version == 'scalar':
            u = advance(problem, u, u_1, u_2, x, y, t[n],
                    Cx2, Cy2, dt, setBC = BC_type)
        else: 
            u = advance(problem, u, u_1, u_2, xv, yv, t[n],
                    Cx2, Cy2, dt, setBC = BC_type)
                            
        if user_action is not None:
            if user_action(u[1:-1,1:-1], x[1:-1], y[1:-1],t, n+1):
                break

        u_2[:,:], u_1[:,:] = u_1, u

    cpu_time = time.clock() - t0
    
    return u[1:-1,1:-1], x[1:-1], y[1:-1], t, cpu_time
    
"*****************************************************************************"
def stabilityCriterion(problem,xv,yv,dx,dy,dt,safetyFactor):
    q = zeros((xv.shape[0],yv.shape[1]))
    q[:,:] = problem.q(xv, yv)
    c = abs(q).max()    
    if c < 1e-12:
        return dt
     
    dt_max = float(safetyFactor)/c*(1.0/dx**2 + 1.0/dy**2)**(-0.5)
    if dt < dt_max:
        return dt
    else:
        return dt_max  
"*****************************************************************************"
def advance_scalar(problem, u, u_1, u_2, x, y, t, 
            Cx2, Cy2, dt, step1=False, setBC = None):
                      
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
                 Cx2/pij * u_x + Cy2/pij * u_y
    
    if step1:
        u[1:-1,1:-1] /= 2
    else:
        u[1:-1,1:-1] /= (1+fac)

    # Set Boundary conditions
    u = setBC(u,Ix,Iy)   

    return u
"*****************************************************************************"
def advance_vectorized(problem, u, u_1, u_2, x, y, t, 
            Cx2, Cy2, dt, step1=False, setBC = None):
       
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
         Cx2/pij * u_x + Cy2/pij * u_y
                      
    if step1:
        u[1:-1,1:-1] /= 2
    else:
        u[1:-1,1:-1] /= (1+fac)
    
    # Set Boundary conditions
    u = setBC(u,Ix,Iy)   

    return u
    
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
        '--safetyFactor', '--dt_safetyFactor', type=float, default=1.0, 
        help='safety factor for time step', metavar='safetyFactor')
        
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
        
"*****************************************************************************"

if __name__ == '__main__':
    main()
