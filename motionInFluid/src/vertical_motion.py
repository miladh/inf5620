# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 09:10:51 2013

@author: Milad H. Mobarhan
"""
from numpy import *
close("all")
"""
Solve
    v'(t) = -a*v(t) + b,

with initial condition v(0)=v0, for t in the time interval
(0,T]. The time interval is divided into time steps of
length dt.
"""

#input
dt = 0.1
T = 10
v0 = 0.0


dt = float(dt)             # avoid integer division
Nt = int(round(T/dt))      # no of time intervals
T = Nt*dt                  # adjust T to fit time step dt


#Constants:
Cd = 0.45
g = 9.81  #m/s^2
r = 0.11  # m
m = 0.43  #kg 
   


mu    = 8.9e-4   #Pa s
rho   = 1000     #kg/m^3


V = 4.0/3*pi*r**3
A = pi*r**2
rhoBody = float(m/V)

b = g*(rho/rhoBody - 1)


#initializing
v = zeros(Nt+1)            # array of u[n] values
z = zeros(Nt+1)            # array of u[n] values
t = linspace(0, T, Nt+1)   # time mesh
v[0] = v0                  # assign initial condition

#solve
for n in range(0, Nt): 
    Re = 2*r*abs(v[n])/mu   
    print Re
    
    if Re < 1:
        a = 0.5*Cd*A/m
        v[n+1] =((v[n]*(2 + dt*a))+ 2*b*dt)/ (2 + a*dt)
    else:
        a = 6*pi*r*mu/m
        v[n+1] =( v[n] + dt*b)/ (1 + dt*a*abs(v[n]))
    
    z[n+1] = z[n] + v[n+1]*dt

    
#plot    
plot(t,v, 'o')
xlabel("Time [s]")
ylabel("Velocity [m/s]")
