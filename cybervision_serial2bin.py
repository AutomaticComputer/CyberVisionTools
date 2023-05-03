# 2023/04/22 modified to match the hardware (hopefully)
import sys

serial_file = open(sys.argv[1] + ".txt", "r")
bin_file = open(sys.argv[1] + ".bin", "wb")
serial_split_file = open(sys.argv[1] + "_split.txt", "w")


current_data = 0

s = serial_file.read()
serial_file.close()

for i in range(0, len(s)):
    if s[i] == '0':
        current_data = (current_data << 1)
    if s[i] == '1':
        current_data = (current_data << 1) + 1
    serial_split_file.write(s[i])
    if (current_data & 0x100) != 0:
        bin_file.write(bytes([current_data & 0xFF]))
        current_data = 0
        print(file=serial_split_file)

bin_file.close()
