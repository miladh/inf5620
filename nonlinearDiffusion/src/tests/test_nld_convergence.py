# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 09:08:49 2013

@author: milad
"""

from pylab import *
from dolfin import *
from math import log as ln
import nose.tools as nt
import nonlinearDiffusion as nld



class trigonometricSolution(nld.Problem):
    def a(self,u):        
        return 1.0
      
    def ue(self):    
        return Expression('exp(-pi*pi*t) * cos(pi * x[0])', pi = pi, t= 0)

    def f(self):
        return Expression("0")
        
    def p(self):        
        return 1.0




def test_convergenceRate():

        problem = trigonometricSolution()
        h = 0.1
        T = 1.0
        hValues = []
        errorValues = []
        for i in range(7):
                dt = h
                xnodes = ynodes = int(1/sqrt(dt))
                u_e, u = nld.runSolver(problem,T, dt, [xnodes,ynodes])
                e = u_e.vector().array() - u.vector().array()
                E = np.sqrt(np.sum(e**2)/u.vector().array().size)
                hValues.append(h)
                errorValues.append(E)
                h/=2
        
        
        r = zeros((len(hValues)))
        for i in range(1, len(hValues)):    
            r[i] = ln(errorValues[i-1]/errorValues[i])/ ln(hValues[i-1]/hValues[i])
            print "h = ",hValues[i-1], " E = ", errorValues[i-1], " r = ", r[i]
        
        if not nt.assert_almost_equal(1,r[-1],places=1):
            print "test_convergenceRate succeeded!"
        
if __name__ == '__main__':
    test_convergenceRate()