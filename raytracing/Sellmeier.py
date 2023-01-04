from matplotlib import pyplot
import scipy

BK7_coefficients = [1.03961212,0.231792344,1.0106945,
                    0.00600069867,0.0200179144,103.560653]
SF18_coefficients = [
    1.56441436,0.291413580,0.960307888,0.0121863935,0.0535567966,111.451201]

def Sellmeier_n(lam, coefficients):
    # wavelength lam is in micrometers!
    B1, B2, B3, C1, C2, C3 = coefficients
    n2 = 1 + (B1*lam**2)/(lam**2-C1) \
         +(B2*lam**2)/(lam**2-C2) \
         +(B3*lam**2)/(lam**2-C3)
    n = n2**0.5
    return n

wavelengths = scipy.linspace(0.3, 0.8, 100)
refractive_indices_BK7 = [Sellmeier_n(lam, BK7_coefficients) for lam in wavelengths]
refractive_indices_SF18 = [Sellmeier_n(lam, SF18_coefficients) for lam in wavelengths]

pyplot.plot(wavelengths, refractive_indices_BK7, wavelengths, refractive_indices_SF18)
pyplot.show()
