import csv
import scipy
from scipy.stats import linregress
from matplotlib import pyplot

data = []
wldata = []
times = 0,25,50,100,125
for t in times:
    filename = "Experimentation 1 Cyan Raw %d concen final.csv"%t
    with open(filename, "r") as fd:
        reader = csv.reader(fd)
        intensities = []
        wavelengths = []
        for line in reader:
            if len(line) >= 3:
                intensities.append(float(line[2]))
                wavelengths.append(float(line[1]))
    data.append(intensities)
    wldata.append(wavelengths)

data = scipy.array(data)
wldata = scipy.array(wldata)

abort()


slopes = []
intercepts = []
for i in range(len(data[0])):
    slope, intercept, *rest = linregress(times, data[:,i])
    slopes.append(slope)
    intercepts.append(intercept)

slopes = scipy.array(slopes)
intercepts = scipy.array(intercepts)

for i in range(len(slopes)):
    x = [-100, 10]
    y = [slopes[i]*xx+intercepts[i] for xx in x]
    pyplot.plot(x, y, "o-")
pyplot.show()
        
