"""
An evolving package for raytracing in geometrical optics design
Initial development focuses on constructive solid geometry for description of refractive/reflective elements
(C) Wulf Hofbauer 2014, 2015
"""

import math
import scipy

class Vector:
	"An Euclidean vector (i.e., a vector with a dot product and a norm)"
	def __init__(self, components): self.components = tuple(components)
	def __repr__(self): return "Vector%s" % repr(self.components)
	def __getitem__(self, i): return self.components[i]
	def __len__(self): return len(self.components)
	def smul(self, s): return Vector(x * s for x in self)
	def dot(self, y):
		if len(self) != len(y): raise Exception("dimension mismatch in dot product")
		return sum(self[i] * y[i] for i in range(len(self)))
	def __mul__(self, b):
		if isinstance(b, Vector): return self.dot(b)
		else: return self.smul(b)
	def __div__(self, s): return Vector(x / s for x in self)
	def __add__(self, b):
		if len(self) != len(b): raise Exception("dimension mismatch in vector addition")
		return Vector(self[i] + b[i] for i in range(len(self)))
	def __sub__(self, b):
		return self + (-b)
	def __neg__(self):
		return Vector(-x for x in self)
	def __xor__(self, b):	# cross product, only applicable for 3D vectors
		if len(self) != len(b):
			raise Exception("dimension mismatch in cross product")
		if len(self) != 3:
			raise Exception("cross product only defined for 3D vector")
		return Vector((
				self.components[1]*b.components[2] - self.components[2]*b.components[1],
				self.components[2]*b.components[0] - self.components[0]*b.components[2],
				self.components[0]*b.components[1] - self.components[1]*b.components[0]
			))
	def normsquared(self): return sum([abs(x)**2 for x in self])
	def norm(self): return math.sqrt(self.normsquared())
	def normalize(self): return self/self.norm()

class AnchoredVector:
	"An AnchoredVector is a direction vector tagged to a position"
	def __init__(self, location, direction):
		self.location = location
		self.direction = direction
	def __repr__(self): return "%s@%s" % (self.direction, self.location)
	def __neg__(self): return AnchoredVector(self.location, -self.direction)

class NormalizedAnchoredVector(AnchoredVector):
	"A special case of an AnchoredVector that is normalized"
	def __init__(self, location, vector):
		AnchoredVector.__init__(self, location, vector.normalize())

class Ray(NormalizedAnchoredVector):
	"A Ray is a half-line starting at an origin and extending to infinity "\
	"along its direction, represented as an AnchoredVector."
	def __init__(self, origin, direction):
		NormalizedAnchoredVector.__init__(self, origin, direction.normalize())
	def __repr__(self):
		return "Ray: origin %s, direction %s" % (self.location, self.direction)
	def __call__(self, t):
		return self.location + self.direction * t

class Shape:
	"A Shape is a 3-dimensional object with orientable surfaces (i.e., inside and outside)"
	def __repr__(self): return "unspecified shape"
	def __contains__(self, x):
		"Return True if the point x is inside the shape"
		return False
	def intersections(self, ray):
		"Given a ray, return list of intersections and surface normals,"\
		"oriented towards the outside, represented as NormalizedAnchorVectors"
		return list()
	def firstintersection(self, ray):
		"Return the intersection with a ray nearest to its origin"
		intersects = self.intersections(ray)
		# only consider intersections in the forward direction of the ray
		intersects = [i for i in intersects if (i.location - ray.location) * ray.direction > 1e-5]
		# pick the closest one
		if len(intersects):
			return min(intersects, key=lambda x: (x.location - ray.location).norm())
		else:
			return None

class BinaryShapeOp(Shape):
	"A binary shape operation constructs a new shape by combining two given shapes"
	def opname(): return "BinaryShapeOp"
	def __init__(self, shape1, shape2):
		self.shape1 = shape1
		self.shape2 = shape2
	def __repr__(self): return "%s(%s,%s)" % (self.opname(), self.shape1, self.shape2)
	def __contains__(self, point): return False
	def intersections(self, ray):
		return list()

class TransformOp(Shape):
	"A coordinate transformed version of a shape"
	def opname(): return "Null coordinate transformation"
	def __init__(self, shape):
		self.shape = shape
	def __repr__(self): return "%s (%s)" % (self.opname(), self.shape)
	def forwardtransform(self, locationedvector): return locationedvector
	def backwardtransform(self, locationedvector): return locationedvector
	def __contains__(self, point):
		transformed = self.backwardtransform(AnchoredVector(point, None))
		return self.shape.inside(transformed.location)
	def intersections(self, ray):
		transformed = self.backwardtransform(ray)
		intersects = self.shape.intersections(Ray(transformed.location, transformed.direction))
		return [self.forwardtransform(intersect) for intersect in intersects]

class Translation(TransformOp):
	"Translation"
	def opname(self): return "Translation(%s)" % self.offset
	def __init__(self, shape, offset):
		TransformOp.__init__(self, shape)
		self.offset = offset
	def forwardtransform(self, av): return AnchoredVector(av.location + self.offset, av.direction)
	def backwardtransform(self, av): return AnchoredVector(av.location - self.offset, av.direction)

class Rotation(TransformOp):
	def opname(self): return "Rotation(axis=%s, angle=%s degrees)" % (self.axis, self.angle*180/math.pi)
	def __init__(self, shape, axis, angle):
		TransformOp.__init__(self, shape)
		self.axis = axis.normalize()
		self.angle = angle
		self.cosphi = math.cos(angle)
		self.sinphi = math.sin(angle)
	def rotate_fw(self, r):
		n = self.axis
		return r * self.cosphi + n*(n*r)*(1-self.cosphi) + (r^n)*self.sinphi
	def rotate_bw(self, r):
		n = self.axis
		return r * self.cosphi + n*(n*r)*(1-self.cosphi) - (r^n)*self.sinphi
	def forwardtransform(self, av):
		return AnchoredVector(self.rotate_fw(av.location), self.rotate_fw(av.direction))
	def backwardtransform(self, av):
		return AnchoredVector(self.rotate_bw(av.location), self.rotate_bw(av.direction))

class Intersection(BinaryShapeOp):
	"The intersection of two shapes"
	def opname(self): return "Intersection"
	def __contains__(self, x):
		return (x in self.shape1) and (x in self.shape2)
	def intersections(self, ray):
		intersects = [x for x in self.shape1.intersections(ray) if x.location in self.shape2]
		intersects += [x for x in self.shape2.intersections(ray) if x.location in self.shape1]
		return intersects

class Union(BinaryShapeOp):
	"The union of two shapes"
	def opname(self): return "Union"
	def __contains__(self, x):
		return (x in self.shape1) or (x in self.shape2)
	def intersections(self, ray):
		intersects = [x for x in self.shape1.intersections(ray) if x.location not in self.shape2]
		intersects += [x for x in self.shape2.intersections(ray) if x.location not in self.shape1]
		return intersects

class Without(BinaryShapeOp):
	"The part of the first shape that is not inside the second"
	def opname(self): return "Without"
	def __contains__(self, x):
		return (x in self.shape1) and (x not in self.shape2)
	def intersections(self, ray):
		intersects = [x for x in self.shape1.intersections(ray) if x.location not in self.shape2]
		intersects += [-x for x in self.shape2.intersections(ray) if x.location in self.shape1]
		return intersects

class Difference(BinaryShapeOp):
	"The regions that are part of one shape, bot not the other"
	def opname(self): return "Difference"
	def __contains__(self, x):
		return (x in self.shape1) ^ (x in self.shape2)
	def intersections(self, ray):
		intersects = [-x if (x in self.shape2) else x for x.location in self.shape1.intersections(ray)]
		intersects += [-x if (x in self.shape1) else x for x.location in self.shape2.intersections(ray)]
		return intersects

class HalfSpace(Shape):
	def __init__(self, center, normal):
		self.center = center
		self.normal = normal.normalize()
	def __repr__(self):
		return "HalfSpace (through %s, normal %s)" % (self.center, self.normal)
	def __contains__(self, x):
		return (x-self.center)*self.normal < 0
	def intersections(self, ray):
		c = self.center
		n = self.normal
		o = ray.location
		d = ray.direction
		dn = d*n
		if dn == 0: return list()
		t = (c-o)*n/dn
		x = ray(t)
		return [NormalizedAnchoredVector(x, n)]

class Sheet(Intersection):
	def __init__(self, center, normal, thickness):
		n = normal.normalize()
		Intersection.__init__(self, HalfSpace(center + normal * (0.5*thickness), normal),
									HalfSpace(center - normal * (0.5*thickness), -normal))

class Sphere(Shape):
	def __init__(self, center, radius):
		self.center = center
		self.radius = radius
	def __repr__(self):
		return "Sphere (center %s, radius %s)" % (self.center, self.radius)
	def __contains__(self, x):
		return (x - self.center).norm() < self.radius
	def intersections(self, ray):
		c = self.center
		r = self.radius
		o = ray.location
		d = ray.direction
		co = c-o
		cod = co*d
		# discriminant/4
		D4 = cod**2 + r**2 - co*co
		if D4 < 0: return list()
		d4 = math.sqrt(D4)
		if d4 >0: ts = [cod+d4, cod-d4]
		else: ts = [cod]
		xs = [ray(t) for t in ts]
		intersects = [NormalizedAnchoredVector(x, x-c) for x in xs]
		return intersects

class Cylinder(Shape):
	def __repr__(self):
		return "Cylinder (center %s, axis %s, radius %s)"%(self.center, self.axis, self.radius)
	def __init__(self, center, axis, radius):
		self.center = center
		self.axis = axis.normalize()
		self.radius = radius
	def __contains__(self, x):
		diff = x - self.center
		par = self.axis * (self.axis * diff)
		perp = diff - par
		dist = perp.norm()
		return dist < self.radius
	def intersections(self, ray):
		r = self.radius
		a = self.axis
		c = self.center
		o = ray.location
		d = ray.direction
		da = d * a
		oc = o - c
		oca = oc * a
		A = 1 - da**2
		B2 = d * oc - da * oca
		C = oc*oc - oca**2 - r**2
		D4 = B2**2 - A*C
		if D4 < 0 or A == 0: return list()
		rd = math.sqrt(D4)
		if rd > 0: ts = [(-B2+rd)/A, (-B2-rd)/A]
		else: ts = -B2+rd/A
		xs = [ray(t) for t in ts]
		intersects = [NormalizedAnchoredVector(x, x-c - a*((x-c)*a)) for x in xs]
		return intersects

def SphericalLens(center, axis, radius1, radius2, thickness, diameter):
	if radius1 == 0: radius1 = scipy.inf
	if radius2 == 0: radius2 = scipy.inf
	axis = axis.normalize()
	lens = Cylinder(center, axis, 0.5*diameter)
	if abs(radius1) == scipy.inf:
		lens = Intersection(lens, HalfSpace(center - axis*thickness/2, -axis))
	else:
		if radius1 > 0:
			lens = Intersection(lens, Sphere(center + axis*(radius1-thickness/2), radius1))
		else:
			ctr1 = center + axis*(radius1-0.5*thickness)
			lens = Intersection(lens, HalfSpace(ctr1, -axis))
			lens = Without(lens, Sphere(ctr1, -radius1))
	if abs(radius2) == scipy.inf:
		lens = Intersection(lens, HalfSpace(center + axis*thickness/2, axis))
	else:
		if radius2 > 0:
			lens = Intersection(lens, Sphere(center + axis*(thickness/2-radius2), radius2))
		else:
			ctr2 = center - axis*(radius2-0.5*thickness)
			lens = Intersection(lens, HalfSpace(ctr2, axis))
			lens = Without(lens, Sphere(ctr2, -radius2))
	return lens



