from pylab import*
import nose.tools as nt
import skydiving as skyDiv


def test_linearSolution():
    """
    Test problem where u=c*t+u0 is the exact solution, to be
    reproduced (to machine precision) by any relevant method.
    """
    
    class testProblem_linearSolution(skyDiv.Problem):
        """
        Problem with ODE of type:
                
                u'(t) = f(u, t)  
    
        where
    
            f(u, t) = -a(t)*|u(t)|u(t) + b(t),
        """
        def __init__(self, c, u0, dt):
            self.c, self.u0, self.dt  = c, u0, float(dt)
            
              
        def exactSolution(self,t):
            return self.c*t + self.u0
        
        def a(self,t):
            return t**0.5  # can be arbitrary
    
        def b(self, t):
            b = self.c + self.a(t)*abs(self.exactSolution(t-self.dt*0.5))\
                *self.exactSolution(t+self.dt*0.5)
            return b
    
    u0 = 0.1; dt = 0.1; c = -0.5; T = 4
  
    problem = testProblem_linearSolution(c, u0=u0, dt=dt)
    solver = skyDiv.CNQuadratic(problem, u0=u0, dt=dt, T=T)
    u,t = solver.solve()  
    ue  = problem.exactSolution(t)

    difference = abs(ue - u).max()  # max deviation
    
    print "test_linearSolution succeeded!"
    nt.assert_almost_equal(difference, 0, places=14)


"*****************************************************************************"
def test_convergenceRate():
    """
    Compare the calculated convergence rate, using linear function of t,
    with the exact one.
    """
    class testProblem_convergenceRate(skyDiv.Problem):
        """
        Problem with ODE of type:
                
                u'(t) = f(u, t)  
    
        where
    
            f(u, t) = -a(t)*|u(t)|u(t) + b(t),
        """
        def __init__(self, c, u0, dt):
            self.c, self.u0, self.dt  = c, u0, float(dt)
            
              
        def exactSolution(self,t):
            return self.c*t + self.u0
        
        def a(self,t):
            return t**0.5  # can be arbitrary
    
        def b(self, t):
            b = self.c + self.a(t)*abs(self.exactSolution(t))*self.exactSolution(t)
            return b
            
            
    u0 = 0.1; c = -0.5; T = 4
    dtValues = array([0.5, 0.25, 0.1, 0.05, 0.025, 0.01])
    EValues  = [] 
    m = len(dtValues)

    for dt in dtValues:
        problem = testProblem_convergenceRate(c,u0=u0,dt=dt)
        solver = skyDiv.CNQuadratic(problem, u0=u0, dt=dt, T= T)
        u,t = solver.solve()  
        ue  = problem.exactSolution(t)
        E = sqrt(dt * sum( (ue - u)**2 ))
        EValues.append(E)
    
    r = []   
    for i in range(1, m, 1):    
        r.append(log(EValues[i-1]/EValues[i])/ log(dtValues[i-1]/dtValues[i])) 
        
    expectedRate = 2.0
    calculatedRate = r[-1]

    nt.assert_almost_equal(expectedRate,calculatedRate,places=1)
    print "test_convergenceRate succeeded!"
    
"*****************************************************************************"    
if __name__ == '__main__':
    test_linearSolution()
    test_convergenceRate()