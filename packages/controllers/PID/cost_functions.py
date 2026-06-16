import numpy as np
def J(targ:np.ndarray, real:np.ndarray, x_alpha:float = 1):
    return ((targ[1] - real[1]) ** 2 + x_alpha * (targ[0] - real[0]) ** 2)