import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from date_manipulator import *

def main(dates, cases, country_name = ''):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(dates, cases, label=country_name)
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax1.xaxis.set_minor_locator(mdates.DayLocator())
    return fig

def TEST_GRAPH():
    testx = np.array([i for i in range(10)])
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(testx,testx**2)
    return fig