import math
import random
import threading
import time

import pygame

WRIST = 0
THUMB_TIP, THUMB_IP = 4, 3
INDEX_TIP, INDEX_PIP, INDEX_MCP = 8, 6, 5
MIDDLE_TIP, MIDDLE_PIP = 12, 10
RING_TIP, RING_PIP = 16, 14
PINKY_TIP, PINKY_PIP, PINKY_MCP = 20, 18, 17
PALETTE = [(88, 101, 242), (55, 182, 255), (47, 217, 196), (242, 193, 78), (255, 111, 89), (245, 241, 232)]
FLASH = (255, 255, 255)
BG = (6, 6, 10)

class HandState:
    def __init__(self):
        self._lock = threading.Lock()
        self._hands = []
    def set_hands(self, hands):
        with self._lock: self._hands = [list(hand) for hand in hands]
    def get_hands(self):
        with self._lock: return [list(hand) for hand in self._hands]

def _dist(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])
def _palm_center(lm):
    points = [lm[i] for i in (0, 5, 9, 13, 17)]
    return sum(p[0] for p in points) / 5, sum(p[1] for p in points) / 5
def _count_fingers(lm):
    return sum(lm[tip][1] < lm[pip][1] for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18))) + int(_dist(lm[4], lm[17]) > _dist(lm[3], lm[17]))
def _fibonacci_sphere(count):
    points = []
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(count):
        y = 1 - (i / max(count - 1, 1)) * 2
        radius = math.sqrt(max(0, 1 - y * y))
        angle = golden * i
        points.append((math.cos(angle) * radius, y, math.sin(angle) * radius))
    return points
def _lerp(a, b, t): return a + (b - a) * t
def _color(c1, c2, t): return tuple(int(_lerp(c1[i], c2[i], t)) for i in range(3))

class ParticleVisualizer:
    def __init__(self, hand_state, count=1400, width=900, height=700):
        self.hand_state = hand_state
        self.count, self.width, self.height = count, width, height
        self._stop = threading.Event()
        self._thread = None
    def start(self):
        if self._thread and self._thread.is_alive(): return
        self._stop.clear(); self._thread = threading.Thread(target=self._run, daemon=True); self._thread.start()
    def stop(self): self._stop.set()
    def _run(self):
        pygame.init(); screen = pygame.display.set_mode((self.width, self.height)); pygame.display.set_caption("GazeFlow - Particle Sphere")
        clock = pygame.time.Clock(); home = _fibonacci_sphere(self.count); positions = [list(p) for p in home]; velocity = [[0, 0, 0] for _ in home]
        reform = [[0, 0, 0] for _ in home]; state = "idle"; charge_start = explode_start = reform_start = 0; charge = 0
        rot_x = rot_y = spin = 0; last_palm = None; offset = [0, 0]; target_offset = [0, 0]; scale = target_scale = 1
        current_color = target_color = PALETTE[5]; base_radius = min(self.width, self.height) * .28; cx, cy = self.width / 2, self.height / 2; font = pygame.font.SysFont("consolas", 14)
        while not self._stop.is_set():
            dt = clock.tick(60) / 1000; now = time.monotonic()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self._stop.set()
            hands = self.hand_state.get_hands(); ring = None
            if len(hands) == 1:
                lm = [(1 - p[0], p[1], p[2]) for p in hands[0]]; palm = _palm_center(lm); target_offset = [(palm[0] - .5) * 3.4, -(palm[1] - .5) * 2.4]
                if last_palm is not None: spin += (palm[0] - last_palm) * 2.6
                last_palm = palm[0]; target_color = PALETTE[min(5, _count_fingers(lm))]
                a, b = lm[4], lm[8]; pinch = _dist((a[0] * self.width, a[1] * self.height), (b[0] * self.width, b[1] * self.height)) < 46
                if pinch and state in ("idle", "charging"):
                    if state == "idle": state, charge_start = "charging", now
                    charge = min(1, (now - charge_start) / .95); ring = ((a[0] + b[0]) * self.width / 2, (a[1] + b[1]) * self.height / 2, charge)
                elif not pinch and state == "charging":
                    state, explode_start = "exploding", now; charge = max(charge, .2)
                    for i, (x, y, z) in enumerate(home):
                        j = [x + random.uniform(-.3, .3), y + random.uniform(-.3, .3), z + random.uniform(-.3, .3)]; length = math.sqrt(sum(v * v for v in j)) or 1; speed = (1.6 + random.random() * 2.2) * (.4 + charge); velocity[i] = [v / length * speed for v in j]
                    charge = 0
            else:
                last_palm = None
                if state == "charging": state, charge = "idle", 0
                if len(hands) >= 2:
                    a, b = _palm_center(hands[0]), _palm_center(hands[1]); spread = math.hypot((a[0] - b[0]) * self.width, (a[1] - b[1]) * self.height); target_scale = max(.55, min(2.1, .9 + (spread - 120) / 520 * 1.3))
            if state == "exploding":
                for i in range(self.count):
                    for axis in range(3): positions[i][axis] += velocity[i][axis] * dt; velocity[i][axis] *= .985
                if now - explode_start >= .85: state, reform_start = "reforming", now; reform = [p[:] for p in positions]
            elif state == "reforming":
                t = min(1, (now - reform_start) / 1.4); ease = t * t * (3 - 2 * t)
                for i in range(self.count): positions[i] = [reform[i][a] + (home[i][a] - reform[i][a]) * ease for a in range(3)]
                if t >= 1: state, positions = "idle", [list(p) for p in home]
            spin *= .9; rot_y += .012 + spin; rot_x += .003; offset = [offset[i] + (target_offset[i] - offset[i]) * min(1, dt * 5) for i in range(2)]; scale += (target_scale - scale) * min(1, dt * 4); current_color = _color(current_color, FLASH if state == "charging" else target_color, .06 if state == "charging" else min(1, dt * 3))
            screen.fill(BG); cos_y, sin_y, cos_x, sin_x = math.cos(rot_y), math.sin(rot_y), math.cos(rot_x), math.sin(rot_x); radius = base_radius * scale
            for x, y, z in positions:
                x1, z1 = x * cos_y - z * sin_y, x * sin_y + z * cos_y; y1, z2 = y * cos_x - z1 * sin_x, y * sin_x + z1 * cos_x; depth = 4.2 + z2
                if depth <= .1: continue
                projection = 4.2 / depth; point = (int(cx + offset[0] * base_radius + x1 * radius * projection), int(cy + offset[1] * base_radius + y1 * radius * projection)); color = tuple(int(c * max(.35, min(1, projection))) for c in current_color); pygame.draw.circle(screen, color, point, max(1, int(2.2 * projection)))
            if ring:
                x, y, fraction = ring; pygame.draw.circle(screen, (60, 60, 66), (int(x), int(y)), 30, 2); pygame.draw.arc(screen, current_color, (int(x) - 30, int(y) - 30, 60, 60), -math.pi / 2, -math.pi / 2 + fraction * math.tau, 3)
            screen.blit(font.render(f"hands: {len(hands)}   state: {state}", True, (110, 112, 120)), (16, self.height - 26)); pygame.display.flip()
        pygame.quit()
