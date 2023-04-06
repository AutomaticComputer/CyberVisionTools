import sys
import wave
import math

# constants
amplitude_threshold = 0.05
width0_threshold = 1/5000
width1_threshold = 1/3000
width2_threshold = 1/1000
gap_threshold = 0.1

is_inverse = False

last_end_t = -1

if sys.argv[1] == "-i":
    is_inverse = True
    basename = sys.argv[2]
else:
    basename = sys.argv[1]

wav_read = wave.open(basename + ".wav", "rb")
cfg_file = open(basename + "_out.cfg", "w")
nchannels = wav_read.getnchannels()

framerate = wav_read.getframerate()
nframes = wav_read.getnframes()
sampwidth = wav_read.getsampwidth()

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

is_negative = True
last_t = 0
wave_count = 0
amp_max = 0
is_in_bit0 = False

is_in_block = False
start_block_t = 0

block_count = 0

def write_bit(b):
    global last_end_t, is_in_block, start_block_t, framerate, cfg_file, block_count, serial_file
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
    if is_inverse:
        amp = -amp
    if abs(amp) > amp_max:
        amp_max = abs(amp)
    if is_negative and (amp > 0):
        if (amp_max > amplitude_threshold): 
            if ((t - last_t)/framerate >= width0_threshold) and ((t - last_t)/framerate < width1_threshold):
                if is_in_bit0:
                    write_bit(0)
                    is_in_bit0 = False
                else:
                    if not is_in_block:
                        start_block_t = last_t
                    is_in_bit0 = True
            elif ((t - last_t)/framerate >= width1_threshold) and ((t - last_t)/framerate < width2_threshold):
                if not is_in_bit0:
                    if not is_in_block:
                        start_block_t = last_t
                    write_bit(1)
                else:
                    is_in_block = False
                is_in_bit0 = False
            else:
                is_in_block = False
        else:
            is_in_block = False
        last_t = t
        is_negative = False
        amp_max = 0
    if amp < 0:
        is_negative = True        

if last_end_t >= 0:
    print(last_end_t / framerate, file = cfg_file)
print("T", nframes / framerate, file = cfg_file)

wav_read.close()
if nchannels == 2:
    wav_write.close()

if block_count > 0:
    serial_file.close()
