from packages.simulation.CO.datatypes import MeasuredState
def J(targ:MeasuredState, real:MeasuredState, x_alpha:float = 0.01):
    return ((targ.theta1 - real.theta1) ** 2 + x_alpha * (targ.x - real.x) ** 2)