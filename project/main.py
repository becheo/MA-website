import subprocess
import time
import datetime

# child = subprocess.Popen([create_voltage_curve.py])
# child = subprocess.Popen(
#     ['C:/Users/Oliver/Desktop/Masterarbeit/03_Software/z_Tutorials_Beispielprogramme/test-exe/build/create_voltage_curve/create_voltage_curve.exe'])
# child = subprocess.Popen(
# ['/build/create_voltage_curve/create_voltage_curve.exe'])

# C:\Users\Oliver\Desktop\Masterarbeit\03_Software\z_Tutorials_Beispielprogramme\test-exe


def count(filename):
    for i in range(1, 6):
        print(i)
        time.sleep(0.1)
    print(filename)


def create_file():
    with open("TESTFILE.txt", "w") as f:
        f.write("Created On {}\n\n" .format(datetime.datetime.now()))
        f.close()


# Kommunikation mit ZeroMq testen
# while True:

#     # Wenn ZeroMq:
#     count()
#     create_file()

#     break

# print("Programm Ende")
