# tabtdrive.py [port] : drive T_TABT01 in DOSBox-X over QMP. For each stage wait for
# the black marker at (620,460), then send the stage's input after its delay.
import json, socket, sys, time, os
from PIL import Image
# stage 5 and 6 run with the exitLock on; stage 8 clicks after the transition (control)
STAGES = [(None, 0), ("key", 0.4), ("click", 0.4), ("key", 2.3), ("key", 0.4), ("key", 2.3), ("click", 2.3), ("click", 4.2)]
P = "/private/tmp/claude-502/-Users-administrator-my-CM-fork-scummvm/02a04943-ee42-4028-94ad-37b6b6a82529/scratchpad/tabt.png"
def qmp():
    s = socket.create_connection(("127.0.0.1", 4444), timeout=10); f = s.makefile("rw"); f.readline()
    f.write(json.dumps({"execute": "qmp_capabilities"}) + "\n"); f.flush(); f.readline(); return f
def cmd(c, a=None):
    m = {"execute": c}
    if a is not None: m["arguments"] = a
    f.write(json.dumps(m) + "\n"); f.flush(); return f.readline()
def px():
    cmd("screendump", {"file": P})
    try:
        im = Image.open(P).convert("RGB"); return im.getpixel((620, 460)), im.getpixel((300, 200))
    except Exception: return None, None
def marker(n):
    cmd("screendump", {"file": P})
    try: return Image.open(P).convert("RGB").getpixel((620 - 40 * (n - 1), 460)) == (0, 0, 0)
    except Exception: return False
def key():
    for down in (True, False):
        cmd("input-send-event", {"events": [{"type": "key", "data": {"down": down, "key": {"type": "qcode", "data": "a"}}}]}); time.sleep(0.05)
def click():
    # NOTE: the button never registers in the D5 projector here (the pointer moves)
    cmd("input-send-event", {"events": [{"type": "abs", "data": {"axis": "x", "value": round(300 * 32767 / 639)}}, {"type": "abs", "data": {"axis": "y", "value": round(200 * 32767 / 479)}}]})
    time.sleep(0.1)
    for down in (True, False):
        cmd("input-send-event", {"events": [{"type": "btn", "data": {"down": down, "button": "left"}}]}); time.sleep(0.15)
t0 = time.time()
for i in range(600):
    try: f = qmp(); break
    except OSError: time.sleep(0.5)
# the boot screens are black: wait for the movie's own stage first
while True:
    c, m = px()
    if c == (255, 255, 255) and m not in (None, (0, 0, 0), (255, 255, 255)): break
    if time.time() - t0 > 150: sys.exit("movie never showed")
    time.sleep(0.2)
print("movie up at %.1f s" % (time.time() - t0), flush=True)
def seen_stage(lo):
    cmd("screendump", {"file": P})
    try: im = Image.open(P).convert("RGB")
    except Exception: return None
    for k in range(lo, len(STAGES) + 1):
        if im.getpixel((620 - 40 * (k - 1), 460)) == (0, 0, 0): return k
    return None
n = 1
while n <= len(STAGES):
    k = seen_stage(n)
    if k is None:
        if time.time() - t0 > 200: sys.exit("timeout waiting for stage %d" % n)
        time.sleep(0.03); continue
    seen = time.time(); act, delay = STAGES[k - 1]
    if act:
        time.sleep(max(0, delay - (time.time() - seen)))
        (key if act == "key" else click)()
    print("stage %d %s at %.2f s after marker" % (k, act, time.time() - seen), flush=True)
    n = k + 1
