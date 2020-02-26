import os
import cv2

# if os.environ.get('OPENCV_CAMERA_SOURCE'):
#     print(os.environ.get('OPENCV_CAMERA_SOURCE'))
# else:
#     print("keine Kamera gefunden")

# image = cv2.imread("USB6009_Messung.png")
# cv2.imshow("Messung", image)
# cv2.waitKey(0)


cv2.namedWindow("preview")
webcam = cv2.VideoCapture(1)  # 0: integrierte Kamera, 1: externe Kamera

if webcam.isOpened():  # try to get the first frame
    rval, frame = webcam.read()  # true if read corretly
else:
    rval = False

while rval:
    cv2.imshow("preview", frame)
    rval, frame = webcam.read()
    key = cv2.waitKey(20)
    if key == 27:  # exit on ESC
        break
webcam.release()
cv2.destroyWindow("preview")


# import socket
# print(socket.gethostname())
# print(socket.gethostbyname(socket.gethostname()))


# import os
# import time
# import matplotlib.pyplot as plt

# import test2

# print(time.time())
# # os.startfile("C:/battery_report2.html")
# # os.startfile: asynchronous -> Befehl wird ausgeführt und Programm fährt
# # fort ohne auf return zu warten
# os.startfile("C:/test2.py")
# # test2.funktion()
# print(time.time())
# print(time.time())
# print(time.time())


# mypath = os.listdir('Uploads')
# print(mypath)
# voltage = range(11)
# print(voltage)
# plt.plot(voltage)
# plt.xlabel('Zeit in s')
# plt.ylabel('Spannung in V')
# plt.show()
# plt.savefig("static/plots/USB6009_Messung.png", bbox_inches='tight')


###############################################################################
# class entryExit(object):

#     def __init__(self, f):
#         self.f = f

#     def __call__(self):
#         print("Entering", self.f.__name__)
#         self.f()
#         print("Exited", self.f.__name__)


# @entryExit
# def func1():
#     print("inside func1()")


# @entryExit
# def func2():
#     print("inside func2()")

# # func1()
# # func2()


###############################################################################
# def smart_divide(func):
#     def inner(a, b):
#         print("I am going to divide", a, "and", b)
#         if b == 0:
#             print("Whoops! cannot divide")
#             return

#         return func(a, b)
#     return inner


# @smart_divide
# def divide(a, b):
#     return a/b


# result1 = divide(10, 5)
# result2 = divide(10, 0)

# print("result 1: ", result1)
# print("result 2: ", result2)
