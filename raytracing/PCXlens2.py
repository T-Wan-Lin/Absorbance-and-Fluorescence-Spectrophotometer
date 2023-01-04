import CSG
import Elements
import scipy

import matplotlib as mpl
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D

#from CSG import Ray, SphericalLens, Sphere, HalfSpace, Cylinder
#from Elements import LightRay, Sellmeier, Component

# define a PCX lens, Edmund optics #32-477

def PCXlensshape(radius, thickness):
    center = CSG.Vector([0, 0, 0])
    normal = CSG.Vector([0, 0, -1])
    halfspace = CSG.HalfSpace(center, normal)
    spherecenter = CSG.Vector([0, 0, -radius+thickness])
    sphere = CSG.Sphere(spherecenter, radius)
    lensshape = CSG.Intersection(halfspace, sphere)
    return lensshape

EdmundOptics32_477 = PCXlensshape(25.84e-3, 4.90e-3)

BK7 = Elements.Material(1.5167)

lens = Elements.Component(EdmundOptics32_477, BK7)
blocker = Elements.Component(CSG.HalfSpace(CSG.Vector([0,0,10]),
                                           CSG.Vector([0,0,-1])),
                             BK7)
system = [lens, blocker]



for x in scipy.linspace(-15e-3, 15e-3, 15):
    incomingray = Elements.LightRay(CSG.Vector([x, 0, -20e-3]),
                            CSG.Vector([0, 0, 1]),
                           589e-3)
    points = []
    ray = incomingray
    while ray:
        points.append(ray.anchor)
        ray = ray.propagate(system)

    xcoords = [point[0] for point in points]
    zcoords = [point[2] for point in points]

    pyplot.plot(zcoords, xcoords, "o-")
pyplot.show()
