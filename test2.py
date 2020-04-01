import time


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
data = [0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 1, 1, 0]

with open("USB6009-Messung.csv", "w") as f:
    f.write("Header")
    f.write("Spalteninhalt")

    for i in range(0, len(data), 1):
        f.write("{}" .format(data[i]))
        f.write(",{:.4f}" .format(data[i]))
        f.write(",{:.4f}" .format(data[i]))
        f.write("\n")
    f.close()
