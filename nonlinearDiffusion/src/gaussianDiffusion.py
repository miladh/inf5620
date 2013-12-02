# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 14:34:00 2013

@author: milad
"""
from pylab import *
from dolfin import *
import nonlinearDiffusion as nld

class gaussianDiffusion(nld.Problem):
    
    def __init__(self, beta,sigma):
        self.beta = beta
        self.sigma = sigma
        
        
    def a(self,u):        
        return 1 + self.beta * u * u
      
    def ue(self):   
        return Expression('exp(-1./(2*sigma*sigma)*(x[0]*x[0]+ x[1]*x[1]))', 
                          sigma=self.sigma)

    def f(self):
        return Expression('0', t = 0)
        
    def p(self,t=0):        
        return 1.0


def main():
    beta =1.0; sigma = 0.01
    T = 10.0; dt = 0.01; 
    domain = [10, 10]
    makePlot = True
    
    problem = gaussianDiffusion(beta, sigma)
    u_e, u = nld.runSolver(problem,T, dt, domain,makePlot)
    
if __name__ == '__main__':
    main()