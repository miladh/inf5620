import nose.tools as nt
import skydiving as skyDiv



"*****************************************************************************"
def test_linearSolution():
    """
    Test problem where u=c*t+I is the exact solution, to be
    reproduced (to machine precision) by any relevant method.
    """

    u0 = 0.1; dt = 0.1; c = -0.5; T = 4
    Nt = int(T/dt)  # no of steps
    
    problem = testProblem(c,u0,dt)
    solver = skyDiv.CNQuadratic(problem, u0=u0, dt=dt, T= Nt*dt)
    u,t = solver.solve()  
    ue  = problem.exactSolution(t)
    
    difference = abs(ue - u).max()  # max deviation
    # No of decimal places for comparison depend on size of c
    
    print "test_linearSolution succeeded!"
    nt.assert_almost_equal(difference, 0, places=14)

"*****************************************************************************"
class testProblem(skyDiv.Problem):
    def __init__(self, c, u0, dt):
        self.c, self.u0, self.dt  = c, u0, dt
          
    def exactSolution(self,t):
        return self.c*t + self.u0
    
    def a(self,t):
        return t**0.5  # can be arbitrary

    def b(self, t):
        return self.c + self.a(t)\
        *abs(self.exactSolution(t))*self.exactSolution(t+self.dt)