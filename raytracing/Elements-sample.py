import CSG
import scipy
import math

class Material:
	"Properties of an optical material"
	def __init__(self, refractiveindex):
		self.n = refractiveindex
	def refractiveindex(self, wavelength): return self.n


class LightRay(CSG.Ray):
	"An optical ray"
	def __init__(self, origin, direction, wavelength):
		CSG.Ray.__init__(self,origin, direction)
		self.wavelength = wavelength
	def propagate(self, components):
		# find the nearest intersecting component
		intersects = [(co, co.intersect(self)) for co in components]
		intersects = [x for x in intersects if x[1] is not None]
		if len(intersects) is 0: return None
		intersectingcomponent = min(intersects, key=lambda i: (self.anchor - i[1].anchor).norm())[0]
		# interact at the surface
		return intersectingcomponent.interact(self)

class Component:
	"An optical component"
	def __init__(self, shape, material):
		self.shape = shape
		self.material = material
	def intersect(self, lightray):
		return self.shape.intersect(lightray)
	def interact(self, lightray):
		"Return the resulting ray after interaction with a surface"
		intersection = self.intersect(lightray)
		n = intersection.vector
		k = lightray.vector
		nk = n*k
		k_perp = n * nk
		k_par = k - k_perp
		l_par = k_par
		if nk < 0: l = self.material.refractiveindex(lightray.wavelength)
		else: l = 1.0/self.material.refractiveindex(lightray.wavelength)
		lp2 = l**2 - l_par*l_par
		if lp2 < 0: return None
		if nk < 0: l_perp = -n * math.sqrt(lp2)
		else: l_perp = n * math.sqrt(lp2)
		l = (l_par + l_perp).normalize()
		return LightRay(intersection.anchor + l*1e-3, l, lightray.wavelength)
		#~ return LightRay(intersection.anchor, l, lightray.wavelength)


glass = Material(1.57)

#~ lensshape = CSG.Intersection(
	#~ CSG.Sphere(CSG.Vector((0,0,7.7)), 8.0),
	#~ CSG.HalfSpace(CSG.Vector((0,0,0)), CSG.Vector((0,0,1)))
	#~ )
#~
#~ lensshape = CSG.Intersection(
	#~ CSG.Sphere(CSG.Vector((0,0,15.85)), 16),
	#~ CSG.Sphere(CSG.Vector((0,0,-15.85)), 16)
	#~ )
#~
lensshape = CSG.Intersection(
	CSG.Sphere(CSG.Vector((0,0,27)), 30.0),
	CSG.HalfSpace(CSG.Vector((0,0,0)), CSG.Vector((0,0,1)))
	)

#~ lensshape = CSG.Intersection(
	#~ lensshape,
	#~ CSG.Cylinder(CSG.Vector((0,0,0)), CSG.Vector((0,0,1)), 1.0)
	#~ )

lens = Component(lensshape, glass)

system = [lens]

#~ print lens.shape


import matplotlib.pyplot as pyplot

for i in range(8):
	angle = scipy.pi/180*5*i
	color = ["black", "brown", "red", "orange", "yellow", "green", "blue", "violet", "gray", "lightgray"][i]
	#~ color = "gray"
	for x0 in scipy.linspace(-6, 6, 9):
		direction = CSG.Vector((scipy.sin(angle), 0, scipy.cos(angle)))
		origin = CSG.Vector((x0, 0, 0)) - direction * 20
		coords=[]
		ray = LightRay(origin, direction, 589e-9)
		coords.append(ray.anchor)
		#~ print ray
		while ray.propagate(system) is not None:
			ray = ray.propagate(system)
			coords.append(ray.anchor)
			#~ print ray
		coords.append(ray.anchor + ray.vector*55)
		#~ a = ray.anchor; v = ray.vector
		#~ print -a[0]*v[2]/v[0]+a[2]
		pyplot.plot([v[2] for v in coords], [v[0] for v in coords], color)

pyplot.show()
