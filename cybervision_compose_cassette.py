import sys
import wave
import math

# constants
amplitude_max = 0.5
amplitude_tail = 0.2
freq0 = 4000
freq1 = 2000
period = 1/freq1

# default values
nchannels = 1
nframes = 0
sampwidth = 2

cfg_file = open(sys.argv[1] + ".cfg", "r")

lines = cfg_file.readlines()
cfg_file.close()

write_started = False

data_written = False

# t: the number of frames from the beginning of the file.

t = 0

def write_sample(x):
    global t, wav_write, wav_read, nframes_r, nchannels, write_buf, write_started

    if not write_started:
        wav_write = wave.open(sys.argv[1] + "_out.wav", "wb")
        wav_write.setnchannels(nchannels)
        wav_write.setframerate(framerate)
        wav_write.setsampwidth(sampwidth)
        write_started = True
        write_buf = bytearray(sampwidth * nchannels)

    if nchannels == 2:
        if t < nframes_r:
            write_buf[0: sampwidth] = wav_read.readframes(1)
        else:
            for i in range(0, sampwidth):
                write_buf[i] = 0
    y = int(x * (1 << (8*sampwidth - 1)))
    for i in range(0, sampwidth):
        write_buf[(nchannels-1)*sampwidth + i] = ((y >> (8*i)) & 0xFF)
    wav_write.writeframes(write_buf)

for line in lines:
    print(line, end = "", flush = True)
    words = line.split()
    if words[0] == "C":
        nchannels = int(words[1])
    if words[0] == "F":
        framerate = int(words[1])
    if words[0] == "W":
        sampwidth = int(words[1])
    if words[0] == "A":
# nchannels, framerate, sampwidth, write_buf overridden.
        nchannels = 2
        audiotrack_name = words[1]
        wav_read = wave.open(audiotrack_name, "rb")
        framerate = wav_read.getframerate()
        sampwidth = wav_read.getsampwidth()
        nframes_r = wav_read.getnframes()

        if wav_read.getnchannels() != 1:
            print("Audio file must be mono.")
            exit()
    if words[0] == "T":
        next_time = float(words[1])
        if data_written:
            t_beginning = t
            while((t - t_beginning)/framerate < period/2):
                write_sample(amplitude_tail * math.sin(2 * freq1 * math.pi*((t - t_beginning)/framerate - j * period)))
                t = t + 1
            data_written = False
        while(t / framerate < next_time):
            write_sample(0)
            t = t + 1
    if words[0] == "S":
        serial_file = open(words[1], "r")
        s = serial_file.read()
        serial_file.close()

# i: the number of characters read from the file.
        i = 0
# j: the number of bits written in this block.
        j = 0
        t_beginning = t
        while(i < len(s)):
            if s[i] == '0':
                freq = freq0
                i = i + 1
            elif s[i] == '1':
                freq = freq1
                i = i + 1
            else:
                i = i + 1
                continue
            while((t - t_beginning)/framerate < (j+1) * period):
                write_sample(amplitude_max * math.sin(2 * freq * math.pi*((t - t_beginning)/framerate - j * period)))
                t = t + 1
            j = j + 1
        data_written = True
    if words[0] == "B":
        bin_file = open(words[1], "rb")
        s = bin_file.read()
        bin_file.close()

# j: the number of bits written in this block.
        j = 0
        t_beginning = t
# i: the number of bytes read from the file.
        for i in range(0, len(s)):
            for b in range(0, 10):
                if b == 0:
                    freq = freq1
                elif b == 9:
                    freq = freq0
                else:
                    if (s[i] & (1 << (8 - b))) == 0:
                        freq = freq0
                    else:
                        freq = freq1
                while((t - t_beginning)/framerate < (j+1) * period):
                    write_sample(amplitude_max * math.sin(2 * freq * math.pi*((t - t_beginning)/framerate - j * period)))
                    t = t + 1
                j = j + 1
        data_written = True


if nchannels == 2:
    if (t < nframes_r):
        while(t < nframes_r):
            write_sample(0)
            t = t + 1
    wav_read.close()

wav_write.close()
