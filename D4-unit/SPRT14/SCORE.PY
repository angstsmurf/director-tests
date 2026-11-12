import struct
def rec(ch): return 20 + 20 * ch
def setb(f, ch, i, v): f[rec(ch) + i] = v
def setx(f, ch, x): f[rec(ch) + 10:rec(ch) + 12] = struct.pack('>h', x)
def edit(frames):
    base = frames[1]
    del frames[2:]
    for n in range(5):
        frames.append(bytearray(base))
    for f in frames[1:]:
        f[16:18] = struct.pack('>H', 3)
    # channels 2 and 4 moveable, 3 not; the score moves them every frame
    for f in frames[1:]:
        setb(f, 4, 18, 0x80)
    xs = {2: [61, 200, 260, 300, 340, 380], 3: [61, 200, 260, 300, 340, 380], 4: [61, 120, 180, 240, 300, 360]}
    for ch, l in xs.items():
        for k, x in enumerate(l):
            setx(frames[1 + k], ch, x)
    # frame 3 also changes the blend byte (unused with copy ink), so the
    # sprites differ in more than their location
    for ch in (2, 3, 4):
        setb(frames[2], ch, 19, 50)
    # frame 5: channels 2 and 4 stop being moveable; frame 6 moveable again
    setb(frames[4], 2, 18, 0)
    setb(frames[4], 4, 18, 0)
