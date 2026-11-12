import struct
def rec(ch): return 20 + 20 * ch
def edit(frames):
    base = frames[1]
    del frames[2:]
    frames.append(bytearray(base))
    frames.append(bytearray(base))
    for f in frames[1:]:
        f[16:18] = struct.pack('>H', 3)
    # frame 3: channel 3 becomes an outlined round rect (type 13) with line
    # size 0. Bytes 6-7 keep the 2 the bitmap's cast number left there,
    # which D4 reads as the shape's pattern.
    f = frames[2]
    f[rec(3) + 1] = 13
    f[rec(3) + 4] = 0
    frames[3] = bytearray(f)
