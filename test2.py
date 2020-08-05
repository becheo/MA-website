# import time

# def funktion():
#     for i in range(10):
#         print("Skritp 2 {}" .format(i))
#         time.sleep(1)
# number = [0, 1, 0, 1, 0]

# data = list(range(len(number)))
# print(data)

# if 'files' in locals():
#     print("Dateien vorhande")
# else:
#     print("keine Dateien vorhanden")
# data = [0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 1, 1, 0]

# with open("USB6009-Messung.csv", "w") as f:
#     f.write("Header")
#     f.write("Spalteninhalt")

#     for i in range(0, len(data), 1):
#         f.write("{}" .format(data[i]))
#         f.write(",{:.4f}" .format(data[i]))
#         f.write(",{:.4f}" .format(data[i]))
#         f.write("\n")
#     f.close()

# class Dog():
#     legs = 4

#     def __init__(self, name):
#         self.name = name


# sam = Dog('Sam')

# print("name: {};    legs: {}" .format(sam.name, sam.legs))


# import matplotlib.pyplot as plt

# x = range(10)
# y = range(10)

# dates = ['01.02.2020', '01.02.2016', '01.04.2015', '01.02.2016', '01.02.2017']

# plt.plot(x, y)
# plt.xticks(range(1, 11, 2), dates)
# plt.show()

# testlist = ['-'] * 10
# print(testlist)

# import pandas

# data = pandas.read_csv('project/static/uploads/34-Spannungsverlauf.csv')

# data_time = data['time']
# data_voltage = data['voltage']

# print(data_time.iloc[-1])

# import os

# print(os.urandom(16))


# import cv2  # Import openCV
# import sys  # import Sys. Sys will be used for reading from the command line. We give Image name parameter with extension when we will run python script

# import numpy as np
# from matplotlib import pyplot as plt


# Read the image. The first Command line argument is the image
# The function to read from an image into OpenCv is imread()
# cap = cv2.VideoCapture(0)
# while(True):
#     ret, frame = cap.read()
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     cv2.imshow('frame', gray)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# cap.release()

# ret, frame = cap.read()
# # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# histogram = cv2.calcHist([frame], [0], None, [256], [0, 256])

# plt.hist(frame.ravel(), 256, [0, 256])
# plt.show()

# brightness = np.ndarray.mean(frame.ravel())

# print(brightness)

# while(True):
#     cv2.imshow('frame', gray)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# cap.release()

import pandas
import numpy as np

data = pandas.read_csv(
    'C:/Users/Oliver/Desktop/Masterarbeit/03_Software/Website/project/static/uploads/49-Spannungsverlauf_3V_test.csv')

data_time = data['time']

print(data_time[4])

# print(np.where(data.applymap(lambda x: x == '')))
print(np.where(pandas.isnull(data_time)))
