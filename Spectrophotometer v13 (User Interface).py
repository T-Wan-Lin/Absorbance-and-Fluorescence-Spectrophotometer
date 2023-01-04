import scipy
import matplotlib
from matplotlib import pyplot
import serial
import time
    
def pixelNumberToWavelength(pixelnumber):
    a = 379.092
    b = 1.00553
    c = -0.00786286
    d = 4.69722e-5
    x = pixelnumber
    wavelength = d*x**3 + c*x**2 + b*x + a
    return wavelength

def readSpectrum(arduino):
    arduino.write(b"R")
    arduino.flush()
    time.sleep(1)
    print(arduino.readline().decode())
    data = []
    for channel in range(256):
        response = arduino.readline().decode().split(",")
        #print(response)
        if channel != int(response[0]):
            print("warning - channel numbers do not match")
        value = float(response[1])
        data.append(value)
    channels = [i for i in range(len(data))]
    wavelengths = [pixelNumberToWavelength(x) for x in channels]
    wavelengths = scipy.array(wavelengths)
    data = scipy.array(data)
    return channels, wavelengths, data

def saveSpectrum(channels, wavelengths, intensities):
    filename = input("Enter the filename to save to:")
    with open(filename, "w") as fd:
        for i in range(len(channels)):
            fd.write("%d,%f,%f\n"%(channels[i], wavelengths[i], intensities[i]))
        print("successfully saved the file")

def absorptionMenu():
    referenceSpectrum = None
    while True:
        print("STEP 1: Ensure that sample has been put in the correct position for testing")
        print("STEP 2: LED Lamp on = Y, LED Lamp off = X")
        print("STEP 3: Set exposure: A = 1ms, B = 5ms, C = 10ms, D = 15ms, E = 20ms")
        print("STEP 4: Read spectrum: R")
        print("STEP 5: Save previous spectrum: S")
        print("STEP 6: Save spectrum as reference: r")
        print("STEP ?: Display absorbtion spectrum: a")
        print("QUIT = Q")
        command = input("Your choice:")
        if command in "ABCDEXY":
            arduino.write(command.encode("ascii"))
        elif command == "Q" : return
        elif command == "R":
            arduino.write("Y".encode("ascii")) # lamp on
            channels, wavelengths, intensities = readSpectrum(arduino) 
            arduino.write("X".encode("ascii")) # lamp off
            import time
            time.sleep(2)
            channels, wavelengths, background = readSpectrum(arduino)
            intensities -= background
            intensities = scipy.clip(intensities, 0.001, 1024)
            wavelengths  = scipy.clip(wavelengths, 300, 900) #visible wavelength range
            pyplot.plot(wavelengths, intensities)
            pyplot.show(block=True)
        elif command == "S":
            saveSpectrum(channels, wavelengths, intensities)
        elif command == "r":
            referenceSpectrum = intensities
        elif command == "a":
            absorption = scipy.log10(referenceSpectrum/intensities)
            pyplot.plot(wavelengths, absorption)
            pyplot.show(block=True)
        else: print("unknown command")

def fluorescenceMenu():
    while True:
        print("STEP 1: Ensure that sample has been put in the correct position for testing")
        print("STEP 2: UV Lamp on = U, UV Lamp off = V")
        print("STEP 3: Set exposure: F = 1000ms, G = 2000ms, H = 3000ms")
        print("STEP 4: Read spectrum: R")
        print("STEP 5: Save previous spectrum: S")
        print("QUIT = Q")
        command = input("Your choice:")
        if command in "FGHUV":
            arduino.write(command.encode("ascii"))
        elif command == "Q" : return
        elif command == "R":
            arduino.write("U".encode("ascii")) # lamp on
            channels, wavelengths, intensities = readSpectrum(arduino)
            arduino.write("V".encode("ascii")) # lamp off
            import time
            time.sleep(2)                                                                                                                                                                                                                                                       
            channels, wavelengths, background = readSpectrum(arduino)
            intensities -= background
            intensities = scipy.clip(intensities, 0.001, 1024)
            pyplot.plot(wavelengths, intensities)
            pyplot.show(block=True)
        elif command == "S":
            saveSpectrum(channels, wavelengths, intensities)
        elif command == "r":
            referenceSpectrum = intensities
        elif command == "a":
            fluorescence = scipy.log10(referenceSpectrum/intensities)
            pyplot.plot(wavelengths, absorption)
            pyplot.show(block=True)
        else: print("unknown command"); return

# Main program starts here

arduino = serial.Serial("/dev/ttyACM0", timeout = 1)
time.sleep(1)

while True:
    print("Absorbance = ab, Fluorescence = fl")
    command = input("Your chosen method:")
    if command == "ab": absorptionMenu()
    elif command == "fl": fluorescenceMenu()
    else: print("Help! I don't know what to do! Enter in the commands in the description!")



