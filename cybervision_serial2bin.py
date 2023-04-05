import sys

serial_file = open(sys.argv[1] + ".txt", "r")
bin_file = open(sys.argv[1] + ".bin", "wb")
serial_split_file = open(sys.argv[1] + "_split.txt", "w")

is_started = 0
is_stopped = 0

s = serial_file.read()
serial_file.close()

for i in range(0, len(s)):
    if is_started == 0:
        if s[i] == '1':
            if is_stopped != 0:
                is_started = 1
                current_bits = 0
                current_data = 0
                print(file=serial_split_file)
        else:
            is_stopped = 1
    else:
        if (current_bits >= 8) and (s[i] == '0'):
            is_stopped = 1
            is_started = 0
            bin_file.write(bytes([current_data]))
        else:
            if s[i] == '0':
                current_bits = current_bits + 1
                current_data = ((current_data << 1) & 0xFF)
            if s[i] == '1':
                current_bits = current_bits + 1
                current_data = (((current_data << 1) + 1) & 0xFF)
    serial_split_file.write(s[i])

bin_file.close()
