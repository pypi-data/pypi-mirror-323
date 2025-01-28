from matplotlib.pyplot import cm
import numpy as np

def get_colors(size):
    return cm.rainbow(np.linspace(0, 1, size))