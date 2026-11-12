import struct
def rec(ch): return 20 + 20 * ch
def setb(f, ch, i, v): f[rec(ch) + i] = v
def setw(f, ch, i, v): f[rec(ch) + i:rec(ch) + i + 2] = struct.pack('>h', v)
def edit(frames):
    base = frames[1]
    del frames[2:]
    for n in range(5):
        frames.append(bytearray(base))
    for f in frames[1:]:
        f[16:18] = struct.pack('>H', 3)
        for ch in (1, 2, 3, 4):
            setb(f, ch, 18, 0)          # nothing moveable
    for k, f in enumerate(frames[1:]):
        setw(f, 2, 10, [61, 200, 260, 300, 340, 380][k])   # ch2: locH only
        setw(f, 3, 8, [137, 140, 143, 146, 149, 152][k])   # ch3: locV only
        setw(f, 4, 10, [61, 120, 180, 240, 300, 360][k])   # ch4: locH only
    for f in frames[3:]:
        setb(f, 4, 2, 35)               # frame 4 on: ch4 foreColor 35
    for f in frames[4:]:
        setb(f, 4, 5, 36)               # frame 5 on: ch4 ink 36
