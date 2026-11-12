import struct
def rec(f, ch): return 20 + 20 * ch
def setb(f, ch, i, v): f[rec(f, ch) + i] = v
def setw(f, ch, i, v): f[rec(f, ch) + i:rec(f, ch) + i + 2] = struct.pack('>h', v)
def edit(frames):
    base = frames[1]
    del frames[2:]
    for n in range(3):
        frames.append(bytearray(base))
    for f in frames[1:]:
        f[16:18] = struct.pack('>H', 3)
    # frame 2: sprite 3 not moveable; frame 3: only the moveable bit changes;
    # frame 4: cleared again; frame 5: unchanged copy of 4
    setb(frames[2], 3, 18, 0x80)
