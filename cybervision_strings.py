import sys

# default values
nchannels = 1
nframes = 0
sampwidth = 2

# option "-p": read header as a program and set address
# option "-a": print all strings of characters of length >=2 that do not end with 0x88
# option "-A": print all characters

read_header = False
arg_i = 1
print_all = False
print_all_char = False

while arg_i < len(sys.argv):
    if sys.argv[arg_i] == "-p":
        read_header = True
    elif sys.argv[arg_i] == "-a":
        print_all = True
    elif sys.argv[arg_i] == "-A":
        print_all = True
        print_all_char = True
    else:
        filename = sys.argv[arg_i]
    arg_i += 1

bin_file = open(filename, "rb")
s = bin_file.read()
bin_file.close()

# start_index: where in the file the data starts
# start_addr: the address to be loaded
start_index = 0
start_addr = 0
a5_count = 0

if read_header:
    for i in range(0, len(s)):
        if s[i] == 0xA5:
            if a5_count > 0:
                start_index = i + 7
                start_addr = (s[i + 2] << 8) + s[i + 3]
                break
            else:
                a5_count += 1
        else:
            a5_count = 0

# buf: string buffer
buf = ""

special_chars = ["?", "!", ".", " "]
# i: the number of bytes read from the file.
for i in range(start_index, len(s)):
    if (s[i] >= 0) and (s[i] < 0x50) and (s[i] % 2 == 0):
        if buf == "":
            str_addr = i - start_index + start_addr
        if s[i] < 20: 
            buf += chr(s[i]//2 + 48) # 0 to 9
        elif s[i] < 72:
            buf += chr(s[i]//2 - 10 + 65) # A to Z
        else:
            buf += special_chars[s[i]//2 - 36]
    else:
        if (((s[i] == 0x88) or print_all_char) and len(buf) >= 1) or (print_all and (len(buf) >= 2)):
            print(hex(str_addr), buf)
        buf = ""
if (((s[i] == 0x88) or print_all_char) and len(buf) >= 1) or (print_all and (len(buf) >= 2)):
    print(hex(str_addr), buf)

