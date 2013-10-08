#!/usr/bin/env python
"""
2D wave equation solved by finite differences::

  dt, cpu_time = solver(I, V, f, c, Lx, Ly, Nx, Ny, dt, T,
                        user_action=None, version='scalar',
                        dt_safety_factor=1)

Solve the 2D wave equation u_tt = u_xx + u_yy + f(x,t) on (0,L) with
u=0 on the boundary and initial condition du/dt=0.

Nx and Ny are the total number of mesh cells in the x and y
directions. The mesh points are numbered as (0,0), (1,0), (2,0),
..., (Nx,0), (0,1), (1,1), ..., (Nx, Ny).

dt is the time step. If dt<=0, an optimal time step is used.
T is the stop time for the simulation.

I, V, f are functions: I(x,y), V(x,y), f(x,y,t). V and f
can be specified as None or 0, resulting in V=0 and f=0.

user_action: function of (u, x, y, t, n) called at each time
level (x and y are one-dimensional coordinate vectors).
This function allows the calling code to plot the solution,
compute errors, etc.
"""
import time
#from scitools.std import *
from pylab import *
from mayavi.mlab import *

class Problem:    
    def I(self,x,y):
        return 0 * x + 0 * y
    def f(self,x,y,t):
        return 0 * x + 0 * y + 0 * t
    def V(self,x,y):
        return 0 * x + 0 * y
    def L(self):
        return (10,10)
    def N(self):
        return (40,40)
    def dt(self):
        return 0.01
    def T(self):
        return 10
    def c(self):
        return 1
    def boundary_condition(self,x,y):
        return 0 * x + 0 * y
        
class GaussianProblem(Problem):
    def I(self, x,y):
        Lx,Ly = self.L()
        return exp(-0.5*(x-Lx/2.0)**2 - 0.5*(y-Ly/2.0)**2)
    def boundary_condition(self,x,y):
        return 0 * x + 0 * y
        
class PeriodicBoundary(Problem):
    def I(self, x,y):
        Lx,Ly = self.L()
        return cos(x) + sin(y)
    def boundary_condition(self,x,y):
        return cos(x) + sin(y)

def solver(problem,
           user_action=None, version='scalar'):
    I = problem.I
    V = problem.V
    f = problem.f
    c = problem.c()
    Lx, Ly = problem.L()
    Nx, Ny = problem.N()
    dt = problem.dt()
    T = problem.T()
    if version == 'vectorized':
        advance = advance_vectorized
    elif version == 'scalar':
        advance = advance_scalar

    x = linspace(0, Lx, Nx+1)  # mesh points in x dir
    y = linspace(0, Ly, Ny+1)  # mesh points in y dir
    dx = x[1] - x[0]
    dy = y[1] - y[0]

    xv = x[:,newaxis]          # for vectorized function evaluations
    yv = y[newaxis,:]
    
    print "1"

    stability_limit = (1/float(c))*(1/sqrt(1/dx**2 + 1/dy**2))
    if dt <= 0:                # max time step?
        safety_factor = -dt    # use negative dt as safety factor
        dt = safety_factor*stability_limit
    elif dt > stability_limit:
        print 'error: dt=%g exceeds the stability limit %g' % \
              (dt, stability_limit)
    Nt = int(round(T/float(dt)))
    t = linspace(0, Nt*dt, Nt+1)    # mesh points in time
    Cx2 = (c*dt/dx)**2;  Cy2 = (c*dt/dy)**2    # help variables

    # Allow f and V to be None or 0
    if f is None or f == 0:
        f = (lambda x, y, t: 0) if version == 'scalar' else \
            lambda x, y, t: zeros((x.shape[0], y.shape[1]))
        # or simpler: x*y*0
    if V is None or V == 0:
        V = (lambda x, y: 0) if version == 'scalar' else \
            lambda x, y: zeros((x.shape[0], y.shape[1]))
    print "2"


    order = 'Fortran' if version == 'f77' else 'C'
    u   = zeros((Nx+1,Ny+1), order=order)   # solution array
    u_1 = zeros((Nx+1,Ny+1), order=order)   # solution at t-dt
    u_2 = zeros((Nx+1,Ny+1), order=order)   # solution at t-2*dt
    f_a = zeros((Nx+1,Ny+1), order=order)   # for compiled loops

    Ix = range(0, u.shape[0])
    Iy = range(0, u.shape[1])
    It = range(0, t.shape[0])

    import time; t0 = time.clock()          # for measuring CPU time

    # Load initial condition into u_1
    if version == 'scalar':
        for i in Ix:
            for j in Iy:
                u_1[i,j] = I(x[i], y[j])
    else: # use vectorized version
        u_1[:,:] = I(xv, yv)

    if user_action is not None:
        user_action(u_1, x, xv, y, yv, t, 0)
    print "3"

    # Special formula for first time step
    n = 0
    # Can use advance function with adjusted parameters (note: u_2=0)
    if version == 'scalar':
        u = advance(problem, u, u_1, u_2, f, x, y, t, n,
                    Cx2, Cy2, dt, V, step1=True)

    else:  # use vectorized version
        f_a[:,:] = f(xv, yv, t[n])  # precompute, size as u
        V_a = V(xv, yv)
        u = advance(problem, x,y, u, u_1, u_2, f_a, Cx2, Cy2, dt, V_a, step1=True)

    if user_action is not None:
        user_action(u, x, xv, y, yv, t, 1)

    u_2[:,:] = u_1; u_1[:,:] = u
    print "33"

    for n in It[1:-1]:
        print "n=", n
        if version == 'scalar':
            # use f(x,y,t) function
            u = advance(problem, u, u_1, u_2, f, x, y, t, n, Cx2, Cy2, dt)
        else:
            f_a[:,:] = f(xv, yv, t[n])  # precompute, size as u
            u = advance(problem, x,y,u, u_1, u_2, f_a, Cx2, Cy2, dt)

        if version == 'f77':
            for a in 'u', 'u_1', 'u_2', 'f_a':
                if not isfortran(eval(a)):
                    print '%s: not Fortran storage!' % a

        if user_action is not None:
            if user_action(u, x, xv, y, yv, t, n+1):
                break

        u_2[:,:], u_1[:,:] = u_1, u

    t1 = time.clock()
    print "4"
    # dt might be computed in this function so return the value
    return dt, t1 - t0

def advance_scalar(problem, u, u_1, u_2, f, x, y, t, n, Cx2, Cy2, dt,
                   V=None, step1=False):
    Ix = range(0, u.shape[0])
    Iy = range(0, u.shape[1])
    dt2 = dt**2
    if step1:
        Cx2 = 0.5*Cx2;  Cy2 = 0.5*Cy2; dt2 = 0.5*dt2
        D1 = 1;  D2 = 0
    else:
        D1 = 2;  D2 = 1
    for i in Ix[1:-1]:
        for j in Iy[1:-1]:
            u_xx = u_1[i-1,j] - 2*u_1[i,j] + u_1[i+1,j]
            u_yy = u_1[i,j-1] - 2*u_1[i,j] + u_1[i,j+1]
            u[i,j] = D1*u_1[i,j] - D2*u_2[i,j] + \
                     Cx2*u_xx + Cy2*u_yy + dt2*f(x[i], y[j], t[n])
            if step1:
                u[i,j] += dt*V(x[i], y[j])
    # Boundary condition u=0
    j = Iy[0]
    for i in Ix: 
        u[i,j] = problem.boundary_condition(x[i], y[j])
    j = Iy[-1]
    for i in Ix: 
        u[i,j] = problem.boundary_condition(x[i], y[j])
    i = Ix[0]
    for j in Iy: 
        u[i,j] = problem.boundary_condition(x[i], y[j])
    i = Ix[-1]
    for j in Iy: 
        u[i,j] = problem.boundary_condition(x[i], y[j])
    return u

def advance_vectorized(problem, x,y, u, u_1, u_2, f_a, Cx2, Cy2, dt,
                       V=None, step1=False):
    dt2 = dt**2
    if step1:
        Cx2 = 0.5*Cx2;  Cy2 = 0.5*Cy2; dt2 = 0.5*dt2
        D1 = 1;  D2 = 0
    else:
        D1 = 2;  D2 = 1
    u_xx = u_1[:-2,1:-1] - 2*u_1[1:-1,1:-1] + u_1[2:,1:-1]
    u_yy = u_1[1:-1,:-2] - 2*u_1[1:-1,1:-1] + u_1[1:-1,2:]
    u[1:-1,1:-1] = D1*u_1[1:-1,1:-1] - D2*u_2[1:-1,1:-1] + \
                   Cx2*u_xx + Cy2*u_yy + dt2*f_a[1:-1,1:-1]
    if step1:
        u[1:-1,1:-1] += dt*V[1:-1, 1:-1]
        
    # Boundary condition u=0
    j = 0
    u[:,j] = problem.boundary_condition(x,y[0])
    j = u.shape[1]-1
    u[:,j] = problem.boundary_condition(x,y[-1])
    i = 0
    u[i,:] = problem.boundary_condition(x[0],y)
    i = u.shape[0]-1
    u[i,:] = problem.boundary_condition(x[-1],y)
    return u

import nose.tools as nt

def test_quadratic(Nx=4, Ny=5):
    def exact_solution(x, y, t):
        return x*(Lx - x)*y*(Ly - y)*(1 + 0.5*t)

    def I(x, y):
        return exact_solution(x, y, 0)

    def V(x, y):
        return 0.5*exact_solution(x, y, 0)

    def f(x, y, t):
        return 2*c**2*(1 + 0.5*t)*(y*(Ly - y) + x*(Lx - x))

    Lx = 3;  Ly = 3
    c = 1.5
    dt = -1 # use longest possible steps
    T = 18

    def assert_no_error(u, x, xv, y, yv, t, n):
        u_e = exact_solution(xv, yv, t[n])
        diff = abs(u - u_e).max()
        #print n, version, diff
        nt.assert_almost_equal(diff, 0, places=12)

    for version in 'scalar', 'vectorized', 'cython', 'f77', 'c_cy', 'c_f2py':
        print 'testing', version
        dt, cpu = solver(I, V, f, c, Lx, Ly, Nx, Ny, dt, T,
                         user_action=assert_no_error,
                         version=version)

def run_problem(problem, version='vectorized', save_plot=True):
    global isFirst
    """
    Initial Gaussian bell in the middle of the domain.
    plot_method=1 applies mesh function, =2 means surf, =0 means no plot.
    """
    from glob import glob
    # Clean up plot files
    for name in glob('tmp_*.png'):
        os.remove(name)

    # Initial dummy plot
    x = linspace(0,10,100)
    y = linspace(0,10,100)
    X,Y = meshgrid(x,y)
    Z = sin(X) + cos(Y)
    fig = figure(size=(1024,768))
    fig.scene.anti_aliasing_frames = 0
    
    mySurf = surf(x,y,Z,warp_scale="auto")
    isFirst = True

    def plot_u(u, x, xv, y, yv, t, n):
        fig.scene.disable_render = True
        global isFirst
        mySurf.mlab_source.reset(x = x, y = y, scalars = u)
        if isFirst:
            fig.scene.reset_zoom()
        isFirst = False
        fig.scene.disable_render = False
        time.sleep(0.02)
    
    Nx = 40; Ny = 40; T = 20
    dt, cpu = solver(problem, user_action=plot_u, version=version)


if __name__ == '__main__':
#    import sys
#    from scitools.misc import function_UI
#    cmd = function_UI([test_quadratic, run_efficiency_tests,
#                       run_Gaussian, ], sys.argv)
#    eval(cmd)
#    run_Gaussian()
    problem = PeriodicBoundary()
    run_problem(problem)
    #problem = GaussianProblem()
    #solver(problem)