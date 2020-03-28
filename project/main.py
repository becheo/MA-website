import subprocess
import time
import datetime

# child = subprocess.Popen([create_voltage_curve.py])
# child = subprocess.Popen(
#     ['C:/Users/Oliver/Desktop/Masterarbeit/03_Software/z_Tutorials_Beispielprogramme/test-exe/build/create_voltage_curve/create_voltage_curve.exe'])
# child = subprocess.Popen(
# ['/build/create_voltage_curve/create_voltage_curve.exe'])

# C:\Users\Oliver\Desktop\Masterarbeit\03_Software\z_Tutorials_Beispielprogramme\test-exe


def count():
    for i in range(1, 11):
        print("Dauer: {}" .format(i), end='\r')
        time.sleep(1)


def create_file(filename, id):
    # dies ersetzt zum testen die testbench-contorl function

    filename = 'results-' + filename
    path_results = 'C:/Users/Oliver/Desktop/Masterarbeit/03_Software/Website/project/static/results/' + filename

    with open(path_results, "w") as f:
        f.write("Created On {}\n\n" .format(datetime.datetime.now()))
        f.close()


# Kommunikation mit ZeroMq testen
# while True:

#     # Wenn ZeroMq:
#     count()
#     create_file()

#     break

# print("Programm Ende")
