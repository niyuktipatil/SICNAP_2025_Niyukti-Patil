import numpy as np
import matplotlib.pyplot as plt

#For earth
G = 6.67 * 10**(-11) # m^3/kg*sec
M = 5.97 * 10**24 #kg
v = 7.29 * 10**(-5) # rad/s
r = 0

T = (2*np.pi*r)/v
while r < 1.5 * 10**(11):
    r =+ 0.1 * 10**(11)
    
plt.plot(r, T)
plt.xlabel("Distance")
plt.ylabel("Time for one revolution")