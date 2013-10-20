# -*- coding: utf-8 -*-
from pylab import *

def convergence_rates(h, E):
    r = [log(E[i-1]/E[i])/log(h[i-1]/h[i])
    for i in range(1, len(h))]
    return r
"*****************************************************************************" 
def plot_truncationError(h,E):
    plt.figure(figsize=(8, 6))
    plt.loglog(h, E)
    plt.xlabel("$\log_{10}(h)$",fontsize=20)
    plt.ylabel("$\log_{10}(E)$",fontsize=20)
    plt.title("Estimated truncation error",fontsize=16)
    plt.tight_layout()
