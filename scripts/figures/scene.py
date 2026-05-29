"""Shared polygon scene used across all winding-number blog figures."""
import numpy as np

angles   = np.deg2rad([0, 50, 100, 145, 185, 230, 270, 320])
radii    = np.array(  [2.0, 1.7, 2.1, 1.4, 0.9, 1.8, 2.2, 1.8])
CENTER   = np.array([2.5, 2.0])
VERTICES = CENTER + np.column_stack([radii * np.cos(angles), radii * np.sin(angles)])

POINT_A = np.array([2.5, 2.0])  # inside  — rightward ray hits polygon once  (odd)
POINT_B = np.array([0.3, 0.4])  # outside — rightward ray hits polygon twice (even)

XLIM  = (-0.3, 5.5)
YLIM  = (-0.6, 4.6)

# All figures in this set share the same canvas: FIGSIZE is derived from the
# canvas bounds and SCALE so the data aspect ratio is exact — no tight-crop
# variance between figures.
SCALE   = 0.60  # inches per data unit
FIGSIZE = ((XLIM[1] - XLIM[0]) * SCALE, (YLIM[1] - YLIM[0]) * SCALE)
