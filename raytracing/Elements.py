import CSG
import scipy
import math

class Material:
	"Properties of an optical material"
	def __init__(self):
		self.reflective = False
		self.transmissive = True
	def refractiveindex(self, wavelength): return 1.0

class Absorber(Material):
	def __init__(self):
		Material.__init__(self)
		self.reflective = False
		self.transmissive = True

class Mirror(Material):
	def __init__(self):
		Material.__init__(self)
		self.reflective = True
		self.transmissive = False

class Sellmeier(Material):
	"Sellmeier model for optical glass"
	def __init__(self, B1, B2, B3, C1, C2, C3):
		Material.__init__(self)
		self.B1 = B1
		self.B2 = B2
		self.B3 = B3
		self.C1 = C1
		self.C2 = C2
		self.C3 = C3
	def __repr__(self):
		return "Sellmeier glass, B1=%g, B2=%g, B3=%g, C1=%g, C2=%g, "\
				"C3=%g"%(self.B1, self.B2, self.B3, self.C1, self.C2, self.C3)
	def refractiveindex(self, wavelength):
		l2 = (wavelength*1e6)**2
		n2 = 1.0 + self.B1*l2/(l2-self.C1) + self.B2*l2/(l2-self.C2) + self.B3*l2/(l2-self.C3)
		return math.sqrt(n2)

class LightRay(CSG.Ray):
	"An optical ray"
	def __init__(self, origin, direction, wavelength):
		CSG.Ray.__init__(self,origin, direction)
		self.wavelength = wavelength
	def propagate(self, components):
		# find the nearest intersecting component
		intersects = [(co, co.firstintersection(self)) for co in components]
		intersects = [x for x in intersects if x[1] is not None]
		if len(intersects) is 0: return []
		intersectingcomponent = min(intersects, key=lambda i: (self.location - i[1].location).norm())[0]
		# interact at the surface
		return intersectingcomponent.interact(self)
	def trace(self, components, depth=5):
		if depth > 0:
			newrays = self.propagate(components)
			return (self.location, [nr.trace(components, depth=depth-1) for nr in newrays])
		else: return (self.location, [])

class Component:
	"An optical component"
	def __init__(self, shape, material):
		self.shape = shape
		self.material = material
	def __repr__(self):
		return "Component(shape: %s, material: %s)"%(self.shape, self.material);
	def firstintersection(self, lightray):
		return self.shape.firstintersection(lightray)
	def interact(self, lightray):
		"Return the resulting ray after interaction with a surface"
		result = []
		intersection = self.firstintersection(lightray)
		if intersection:
			result = []
			n = intersection.direction
			k = lightray.direction
			nk = n*k
			k_perp = n * nk
			k_par = k - k_perp
			l_par = k_par
			if nk < 0: l = self.material.refractiveindex(lightray.wavelength)
			else: l = 1.0/self.material.refractiveindex(lightray.wavelength)
			lp2 = l**2 - l_par*l_par
			if self.material.reflective:
				result.append(LightRay(intersection.location, k_par - k_perp, lightray.wavelength))
			if self.material.transmissive and lp2 > 0:
				if nk < 0: l_perp = -n * math.sqrt(lp2)
				else: l_perp = n * math.sqrt(lp2)
				l = (l_par + l_perp).normalize()
				result.append(LightRay(intersection.location, l, lightray.wavelength))
		return result

class Lens(Component):
	def __init__(self, curvature1, curvature2, thickness, diameter, material):
		
		cylinder = CSG.Cylinder(CSG.Vector((0,0,0)), CSG.Vector((0,0,1)), 0.5*diameter) 
		surface1 = CSG.Sphere(CSG.Vector((0, 0, radius1 - 0.5*thickness)), radius1)
		surface2 = CSG.Sphere(CSG.Vector((0, 0, -radius2 + 0.5*thickness)), radius2)
		shape = CSG.Intersection(cylinder, CSG.Intersection(surface1, surface2))
		Component.__init__(self, shape, material)

