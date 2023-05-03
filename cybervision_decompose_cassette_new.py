# Options: 
# -a (float): set amplitude_threshold
# -w (float): set u26b_width
# -g (float): set gap_threshold
# -q: set initial value of u25b to 1
# -f (float): apply high-pass filter with a highpass_factor
#   larger highpass_factor gives lower cutoff frequency
#   1-4 might be reasonable values

import sys
import wave
import math

# constants
amplitude_threshold = 0.05
u26b_width = 1/6000
gap_threshold = 0.1
u25a_q = 0
u25b_q = 0
u26b_q = 0
highpass = False

dc = 0
dc_coeff = 0

arg_i = 0

while arg_i < len(sys.argv):
    if sys.argv[arg_i] == "-a":
        arg_i += 1
        amplitude_threshold = float(sys.argv[arg_i])
    if sys.argv[arg_i] == "-w":
        arg_i += 1
        u26b_width = float(sys.argv[arg_i])
    if sys.argv[arg_i] == "-g":
        arg_i += 1
        gap_threshold = float(sys.argv[arg_i])
    if sys.argv[arg_i] == "-q":
        u25b_q = 1
    if sys.argv[arg_i] == "-f":
        highpass = True
        arg_i += 1
        highpass_factor = float(sys.argv[arg_i])
    else:
        basename = sys.argv[arg_i]
    arg_i += 1

wav_read = wave.open(basename + ".wav", "rb")
cfg_file = open(basename + "_out.cfg", "w")
nchannels = wav_read.getnchannels()

framerate = wav_read.getframerate()
nframes = wav_read.getnframes()
sampwidth = wav_read.getsampwidth()

if highpass:
    dc_coeff = 2000/highpass_factor/framerate


print("C", nchannels, file = cfg_file)

if nchannels == 2:
    audiotrack_name = basename + "_audio.wav"
    wav_write = wave.open(audiotrack_name, "wb")
    wav_write.setframerate(framerate)
    wav_write.setsampwidth(sampwidth)
    wav_write.setnchannels(1)
    print("A", audiotrack_name, file = cfg_file)
else:
    print("F", framerate, file = cfg_file)
    print("W", sampwidth, file = cfg_file)

# if the last value (after highpass filter) was negative
was_negative = True
# the time u26b rose
u26b_t = 0
# the max of the abs of amplitude in this wave
amp_max = 0

# the end of the last block. negative if never set. 
last_end_t = -1

# whether in a block of consecutive bits
is_in_block = False
# the beginning of the block
start_block_t = 0

# the number of blocks already written
block_count = 0

def write_bit(b):
    global t, last_end_t, is_in_block, start_block_t, framerate, cfg_file, block_count, serial_file
    if (t - last_end_t)/framerate > 1/1000:
        is_in_block = False
    if not is_in_block:
        if block_count > 0:
            serial_file.close()
        s = basename + "_{:0>3}".format(block_count) + ".txt"
        if last_end_t >= 0:
            print(last_end_t / framerate, file = cfg_file)
        if (start_block_t - last_end_t)/framerate < gap_threshold:
            print("Warning: short gap before block", block_count, flush = True)
        print("T", start_block_t / framerate, file = cfg_file)
        print("S", s, end = " ", file = cfg_file)
        serial_file = open(s, "w")
        is_in_block = True
        block_count = block_count + 1
    if b == 0:
        serial_file.write('0')
    else:
        serial_file.write('1')
    last_end_t = t

first_transition = True

for t in range(0, nframes):
    c = wav_read.readframes(1)
    value = 0
# assuming little endian
    for i in range(0, sampwidth):
        value = value + (c[(nchannels-1)*sampwidth+i] << (8*i))
    if (value & (1 << (8*sampwidth - 1))) != 0 :
        value = value - (1 << (8*sampwidth))
    if nchannels == 2:
        wav_write.writeframes(c[0: sampwidth])
    amp = value / (1 << (8*sampwidth - 1))
    if highpass:
        dc = (1 - dc_coeff) * dc + dc_coeff * amp
        amp = amp - dc
    if abs(amp) > amp_max:
        amp_max = abs(amp)
    if u26b_q == 0:
        u25a_q = 0
    if (was_negative and (amp >= 0)) or ((not was_negative) and (amp < 0)):
        if first_transition:
            last_t = t 
            first_transition = False
        if (amp_max >= amplitude_threshold): 
            if u26b_q == 1:
                u25a_q = 1 - u25a_q
            else:
                u26b_q = 1
                u26b_t = t
        else:
            is_in_block = False
            first_transition = True
        amp_max = 0
    if (u26b_q == 1) and ((t - u26b_t)/framerate >= u26b_width):
        u26b_q = 0
        u25b_q = 1 - u25b_q
        if u25b_q == 1:
            if not is_in_block:
                start_block_t = last_t
            write_bit(1 - u25a_q)
            first_transition = True
    was_negative = (amp < 0)

if last_end_t >= 0:
    print(last_end_t / framerate, file = cfg_file)
print("T", nframes / framerate, file = cfg_file)

wav_read.close()
if nchannels == 2:
    wav_write.close()

if block_count > 0:
    serial_file.close()
