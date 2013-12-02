# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 10:51:16 2013

@author: milad
"""
from pylab import *
from dolfin import *
from math import log as ln
import nose.tools as nt
import nonlinearDiffusion as nld



class manufactoredSolution(nld.Problem):
    def a(self,u):        
        return 1 + u*u
      
    def ue(self):   
        return Expression('t * x[0] * x[0] * (0.5 - x[0]/3.0)', t= 0)

    def f(self):
        return Expression('-p*pow(x[0], 3)/3 + p*pow(x[0], 2)/2 \
                           + 8*pow(t, 3)*pow(x[0], 7)/9 \
                           - 28*pow(t, 3)*pow(x[0], 6)/9 \
                           + 7*pow(t, 3)*pow(x[0], 5)/2 \
                           - 5*pow(t, 3)*pow(x[0], 4)/4 + 2*t*x[0] - t',
                            p = self.p(), t = 0)
        
    def p(self,t=0):        
        return 1.0




def test_manufactoredSolution():

        problem = manufactoredSolution()
        dt = 0.01
        xnodes = 30
        time = [0.1 , 0.5, 1.0, 2.0, 3.0]
        for T in time:
                u_e, u = nld.runSolver(problem,T, dt, [xnodes])
                e = u_e.vector().array() - u.vector().array()
                E = np.sqrt(np.sum(e**2)/u.vector().array().size)
                
                print "T = ",T, " E = ", E
                nt.assert_almost_equal(0, E, places=3)
        
        print "test_manufactoredSolution succeeded!"
        
if __name__ == '__main__':
    test_manufactoredSolution()
