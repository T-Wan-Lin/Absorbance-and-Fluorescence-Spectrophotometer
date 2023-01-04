import CSG
import Elements
import scipy
import math
import matplotlib.pyplot as pyplot

N_SF10 = Elements.Sellmeier(1.62153902, 0.256287842, 1.64447552, 0.0122241457, 0.0595736775, 147.468793)
SF18 = Elements.Sellmeier(1.56441436, 0.291413580, 0.960307888, 0.0121863935, 0.0535567966, 111.451201)
BK7 = Elements.Sellmeier(1.03961212, 0.231792344, 1.01096945, 0.00600069867, 0.0200179144, 103.560653)
N_SF11 = Elements.Sellmeier(1.73759695, 0.313747346, 1.89878101, 0.013188707, 0.0623068142, 155.23629)
Absorber = Elements.Absorber()
degrees = math.pi/180

def vec(x,y,z):
	return CSG.Vector((x,y,z))
def Sin(deg):
	return math.sin(deg*degrees)
def Cos(deg):
	return math.cos(deg*degrees)
def Atan2(y, x):
	return math.atan2(y, x)/degrees
def wlcolor(wl):
	wl = wl*1e9
	colortable = [(300, 0, 0, 0), (400, 255, 0, 255), (436, 0, 0, 255),
		(480, 0, 255, 255), (550, 0, 255, 0), (590, 255, 255, 0), 
		(635, 255, 0, 0), (900, 0, 0, 0), (1000, 0, 0, 0)]
	last = (0, 0, 0, 0)
	for current in colortable:
		if current[0] >= wl: break
		last = current
	wl1, r1, g1, b1 = last
	wl2, r2, g2, b2 = current
	t = float(wl-wl1)/float(wl2-wl1)
	r = (1-t)*r1 + t*r2
	g = (1-t)*g1 + t*g2
	b = (1-t)*b1 + t*b2
	return "#%02x%02x%02x"%(r, g, b)
def dumptrace(trace, level=0, color="red"):
	node, children = trace
	header = (level+1)*"|   "
	#~ print header + str(node)
	for child in children:
		childnode = child[0]
		x1 = node[2]
		y1 = node[0]
		x2 = childnode[2]
		y2 = childnode[0]
		pyplot.plot([x1, x2], [y1, y2], color)
		#~ print header + "angle: %g degrees"%(math.atan2(y2-y1, x2-x1)/degrees)
		dumptrace(child, level+1, color)

# generate an equilateral prism
baselen = 25.0
prismshape = None
prismoffset = vec(-11.8, 0, 0)
for angle in 0, 120, 240:
	normal = vec(-Cos(angle), 0, Sin(angle))
	surface = CSG.HalfSpace(normal*baselen/3+prismoffset, normal)
	if prismshape:
		prismshape = CSG.Intersection(prismshape, surface)
	else:
		prismshape = surface
prism = Elements.Component(prismshape, N_SF11)

# incident optical axis
incidentaxisangle = 30
incidentaxis = CSG.Ray(vec(0,0,0), vec(Sin(incidentaxisangle), 0, Cos(incidentaxisangle)))

# outgoing optical axis
outgoingaxisangle = -30
outgoingaxis = CSG.Ray(vec(0,0,0), vec(Sin(outgoingaxisangle), 0, Cos(outgoingaxisangle)))

# entrance aperture/light source
apos = incidentaxis(-70)
sourcerays = []
for da in scipy.linspace(-4.8, 4.8, 11):
	sourcerays.append(CSG.Ray(apos, vec(Sin(da+incidentaxisangle), 0, Cos(da+incidentaxisangle))))

# collimation lens - Edmund #47-346
clpos = CSG.AnchoredVector(incidentaxis(-22), incidentaxis.direction)
clshape = CSG.SphericalLens(clpos.location, clpos.direction,
						scipy.inf, 25.84,
						4.9, 24.0)
clens = Elements.Component(clshape, BK7)

### objective lens - Edmund #47-350
##olpos = outgoingaxis(20)
##olshape = CSG.SphericalLens(olpos, outgoingaxis.direction,
##						51.68, scipy.inf,
##						4.9, 24.0)
##olens = Elements.Component(olshape, BK7)

# objective lens - Edmund #47-887
olpos = outgoingaxis(30.0)
olshape = CSG.SphericalLens(olpos, outgoingaxis.direction,
						25.84, scipy.inf,
						4.9, 24.0 )
olens = Elements.Component(olshape, BK7)

#
boundary = Elements.Component(CSG.Sphere( CSG.Vector( (0, 0, 0)), 200), Absorber)
system = [boundary, clens, prism, olens]

# generate rays

rays = []
for wl in scipy.linspace(400e-9, 800e-9, 7):
	rays += [Elements.LightRay(ray.location, ray.direction, wl) for ray in sourcerays]

pyplot.subplot("111", axisbg="black")
pyplot.axis("equal")

for i in range(len(rays)):
	print "processing", i+1, "/", len(rays)
	ray = rays[i]
	trace = ray.trace(system, depth=8)
	dumptrace(trace, color = wlcolor(ray.wavelength))
	pyplot.show(block=False)
	pyplot.draw()
pyplot.show()
