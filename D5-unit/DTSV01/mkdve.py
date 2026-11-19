#!/usr/bin/env python3
# mkdve.py DVB.MOV out.MOV : a 256x192 video that shows whether it is playing.
# Two blue frames, then 98 yellow ones, at 10 fps (all key frames, so a
# direct-to-stage video keeps redrawing over sprites in front of it). A video
# that was never started stays blue; a playing one is yellow from 0.2 s to 10 s.
# Colours are 0/31 per channel so nothing gets dithered on an 8-bit screen.
# The samples from ffmpeg are grafted into DVB.MOV's atoms, which QuickTime for
# Windows is known to accept.
import struct, subprocess, sys, tempfile, os
src, out = sys.argv[1:3]
N_A, N_B, D_A, D_B = 2, 98, 60, 60            # durations in 1/600 s
tmp = os.path.join(tempfile.mkdtemp(), 'x.mov')
subprocess.check_call(['ffmpeg', '-v', 'error', '-y',
    '-f', 'lavfi', '-i', 'color=c=0x0000FF:s=256x192:r=10:d=%g' % (N_A / 10),
    '-f', 'lavfi', '-i', 'color=c=0xFFFF00:s=256x192:r=10:d=%g' % (N_B / 10),
    '-filter_complex', '[0][1]concat=n=2', '-c:v', 'qtrle', '-pix_fmt', 'rgb555be', '-g', '1', tmp])

def atoms(d, o, e):
    while o < e:
        n, t = struct.unpack('>I4s', d[o:o + 8])
        yield t, o, n
        o += n
def find(d, path, o=0, e=None):
    e = len(d) if e is None else e
    for t, a, n in atoms(d, o, e):
        if t == path[0]:
            return (a, n) if len(path) == 1 else find(d, path[1:], a + 8, a + n)
STBL = [b'moov', b'trak', b'mdia', b'minf', b'stbl']
f = open(tmp, 'rb').read()
a, n = find(f, STBL + [b'stsz']); cnt = struct.unpack('>I', f[a + 16:a + 20])[0]
uni = struct.unpack('>I', f[a + 12:a + 16])[0]
sizes = (uni,) * cnt if uni else struct.unpack('>%dI' % cnt, f[a + 20:a + 20 + 4 * cnt])
a, n = find(f, STBL + [b'stco']); off = struct.unpack('>I', f[a + 16:a + 20])[0]
assert cnt == N_A + N_B
data = f[off:off + sum(sizes)]

def box(t, body): return struct.pack('>I4s', len(body) + 8, t) + body
d = open(src, 'rb').read()
def rebuild(o, e, depth):
    res = b''
    for t, a, n in atoms(d, o, e):
        body = d[a + 8:a + n]
        if t in (b'moov', b'trak', b'mdia', b'minf', b'stbl', b'edts'):
            body = rebuild(a + 8, a + n, depth + 1)
        elif t == b'mvhd':
            body = body[:16] + struct.pack('>I', dur * 1000 // 600) + body[20:]
        elif t == b'tkhd':
            body = body[:20] + struct.pack('>I', dur * 1000 // 600) + body[24:]
        elif t == b'elst':
            body = body[:8] + struct.pack('>I', dur * 1000 // 600) + body[12:]
        elif t == b'mdhd':
            assert struct.unpack('>I', body[12:16])[0] == 600
            body = body[:16] + struct.pack('>I', dur) + body[20:]
        elif t == b'stts':
            body = struct.pack('>IIIIII', 0, 2, N_A, D_A, N_B, D_B)
        elif t == b'stss':
            body = struct.pack('>II', 0, cnt) + struct.pack('>%dI' % cnt, *range(1, cnt + 1))
        elif t == b'stsc':
            body = struct.pack('>IIIII', 0, 1, 1, cnt, 1)
        elif t == b'stsz':
            body = struct.pack('>III', 0, 0, cnt) + struct.pack('>%dI' % cnt, *sizes)
        elif t == b'stco':
            body = struct.pack('>III', 0, 1, 0xdeadbeef)
        elif t == b'mdat':
            body = data
        res += box(t, body)
    return res
dur = N_A * D_A + N_B * D_B
r = rebuild(0, len(d), 0)
r = r.replace(struct.pack('>I', 0xdeadbeef), struct.pack('>I', r.index(b'mdat') + 4))
open(out, 'wb').write(r)
print(out, len(r), 'bytes', dur / 600, 's')
