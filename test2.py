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

import os

print(os.urandom(16))
