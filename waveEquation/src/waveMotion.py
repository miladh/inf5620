# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 11:46:19 2013

@author: Milad H. Mobarhan
"""
from pylab import*
from mpl_toolkits.mplot3d import axes3d
ion()
close("all")
    
"*****************************************************************************"
def solver(problem, Lx, Ly, Nx, Ny, dt, T, user_action=None):
    """
    Solve 
    
        p*u_tt + b *u_t = div(q div(u) ) + f 
        
    on (0,L_x)x(0,L_y) in time domain (0,T].
    """
    x = linspace(0, Lx, Nx+1)  # mesh points in x dir
    y = linspace(0, Ly, Ny+1)  # mesh points in y dir
    dx = x[1] - x[0]           # mesh spacing in x dir
    dy = y[1] - y[0]           # mesh spacing in y dir
    
    
    Nt = int(round(T/float(dt)))
    t = linspace(0, Nt*dt, Nt+1)    # mesh points in time
    
    
    dtdx2 = (dt/dx)**2     # help variable
    dtdy2 = (dt/dy)**2     # help variable
        

    u   = zeros((Nx+1,Ny+1))   # solution array
    u_1 = zeros((Nx+1,Ny+1))   # solution at t-dt
    u_2 = zeros((Nx+1,Ny+1))   # solution at t-2*dt

    Ix = range(0, u.shape[0])
    Iy = range(0, u.shape[1])
    It = range(0, t.shape[0])    
    
    import time; t0 = time.clock()          # for measuring CPU time    
    
    # Load initial condition into u_1
    for i in Ix:
        for j in Iy: 
            u_1[i,j] = problem.I(x[i], y[j])    
            
    if user_action is not None:
        user_action(u_1, x, xv, y, yv, t, 0)
        
        
        
    # Special formula for first time step
    n = 0
    # Can use advance function with adjusted parameters (note: u_2=0)
    u = advance(problem, u, u_1, u_2, x, y, t, n,
                    dtdx2, dtdy2, dt,step1=True)

    if user_action is not None:
        user_action(problem,u, x, xv, y, yv, t, 1)

    u_2[:,:] = u_1; u_1[:,:] = u    
    
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    X, Y = np.meshgrid(x, y)
    for n in It[1:-1]:
        # use f(x,y,t) function
        u = advance(problem, u, u_1, u_2, x, y, t, n,
                    dtdx2, dtdy2, dt)
                    
        # Make a first plot  
        fig.clf()
        ax = fig.gca(projection='3d')
        ax.plot_surface(X, Y, u,rstride=1, cstride=1, cmap=cm.jet,
                        linewidth=0, antialiased=False)
#        ax.set_zlim3d(0, 10)              
        plt.draw()
        
        if user_action is not None:
            if user_action(u, x, xv, y, yv, t, n+1):
                break

        u_2[:,:], u_1[:,:] = u_1, u


    t1 = time.clock()    
    return dt, t1-t0
"*****************************************************************************"

def advance(problem,u, u_1, u_2, x, y, t, n, dtdx2, dtdy2, dt,
                   step1=False):
                       
    Ix = range(0, u.shape[0]);  
    Iy = range(0, u.shape[1])
    dt2 = dt**2
             
    for i in Ix[1:-1]:
        for j in Iy[1:-1]:
            qij = problem.q(x[i], y[j])
            qpi = (problem.q(x[i+1], y[j]) + qij)*0.5
            qmi = (qij + problem.q(x[i-1], y[j]))*0.5
            qpj = (problem.q(x[i], y[j+1]) + qij)*0.5
            qmj = (qij + problem.q(x[i], y[j-1]))*0.5
                        
            uij = u_1[i,j]
            u_x = qpi*(u_1[i+1,j] - uij) - qmi*(uij - u_1[i-1,j])
            u_y = qpj*(u_1[i,j+1] - uij) - qmj*(uij - u_1[i,j-1])
            
            pij = problem.p(x[i], y[j])
            fac = problem.b*dt / (2*pij)

            u[i,j] = 2*u_1[i,j] - u_2[i,j]*(fac-1) + \
                     dt2/pij *problem.f(x[i], y[j], t[n]) +\
                     + dtdx2/pij * u_x + dtdy2/pij * u_y
            if step1:
                u[i,j] += 2*dt*problem.V(x[i], y[j])*(fac-1)
    if step1:
        u /= ((1+fac)*(2-fac))
    else:
        u /= (1+fac)
    
    # Boundary condition u=0
    j = Iy[0]
    for i in Ix: u[i,j] = 0
    j = Iy[-1]
    for i in Ix: u[i,j] = 0
    i = Ix[0]
    for j in Iy: u[i,j] = 0
    i = Ix[-1]
    for j in Iy: u[i,j] = 0
    return u

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
        return sin(x)*sin(y);
      
    def V(self,x,y):     
        return sin(x)*sin(y);

    def f(self,x,y,t):
        return 0.0;

    def q(self,x,y):
        return 1.0

    def p(self,x,y):
        return 1.0; 
"*****************************************************************************"
def define_command_line_options(parser=None):
    if parser is None:
        import argparse
        parser = argparse.ArgumentParser()

    parser.add_argument(
        '--Lx', '--upper_boundary_x', type=float, 
        default=5.0, help='upper boundary in x direction',metavar='Lx')
    
    parser.add_argument(
        '--Ly', '--upper_boundary_y', type=float, 
        default=5.0, help='upper boundary in y direction',metavar='Ly')
    
    parser.add_argument(
        '--Nx', '--num_mesh_cells_x', type=int, default=5.0,
        help='total number of mesh cells in the x direction',metavar='Lx')
    
    parser.add_argument(
        '--Ny', '--num_mesh_cells_y', type=int, default=5.0, 
        help='total number of mesh cells in the y direction',metavar='Ly')   
   
    parser.add_argument(
        '--dt', '--time_step_value', type=float, default=0.1, 
        help='time step value', metavar='dt')
        
    parser.add_argument(
        '--T', '--stop_time', type=float, default=10.0,
        help='end time of simulation', metavar='T')    
    
    parser.add_argument(
        '--b', '--damping_factor', type=float, default=0.0,
        help='damping factor', metavar='b')   
                
    parser.add_argument('--saveplot', action='store_true', default=False,
                        help='save plot or not')
                        
    parser.add_argument('--runtests', action='store_true', default=False,
                        help='run nosetests')
        
        
    return parser                           
"*****************************************************************************"
def main():
            
    # Read input from the command line
    parser = define_command_line_options()
    args = parser.parse_args()

    #Set up problem
    problem = SimpleWave(args.b)
    

    #Run solver
    dt, time = solver(problem, args.Lx, args.Ly, args.Nx, args.Ny,
           args.dt, args.T)
    
    print "CPU time: ",time
    
    # Run nosetests
    if(args.runtests):
        import subprocess
        subprocess.call(["nosetests", "-s"])
    
    
    
"*****************************************************************************"

if __name__ == '__main__':
    main()