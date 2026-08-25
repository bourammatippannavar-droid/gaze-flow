import math
import time
import pygame
from .particle_visualizer import PALETTE, BG, HandState, _dist, _palm_center, _count_fingers, _fibonacci_sphere, _lerp

STEPS = [("open_palm", "SHOW AN OPEN PALM", "hold it steady"), ("fist", "MAKE A FIST", "curl all four fingers in"), ("pinch", "PINCH & HOLD", "touch thumb tip to index tip"), ("two_hand_spread", "SPREAD BOTH HANDS", "show two hands, pull them apart")]
HOLD_REQUIRED = 0.5

def _detect_step(key, hands):
    if key == "two_hand_spread":
        if len(hands) < 2: return False
        a, b = _palm_center(hands[0]), _palm_center(hands[1])
        return math.hypot((a[0] - b[0]) * 1000, (a[1] - b[1]) * 1000) > 260
    if not hands: return False
    hand = [(1 - point[0], point[1], point[2]) for point in hands[0]]
    if key == "open_palm": return _count_fingers(hand) >= 4
    if key == "fist": return _count_fingers(hand) == 0
    return _dist((hand[4][0] * 1000, hand[4][1] * 1000), (hand[8][0] * 1000, hand[8][1] * 1000)) < 55

class GestureTrainer:
    def __init__(self, hand_state: HandState, width=900, height=700, on_complete=None):
        self.hand_state, self.width, self.height, self.on_complete = hand_state, width, height, on_complete

    def run(self):
        pygame.init(); screen = pygame.display.set_mode((self.width, self.height)); pygame.display.set_caption("GazeFlow - Gesture Trainer"); clock = pygame.time.Clock()
        title_font = pygame.font.SysFont("consolas", 30, bold=True); font = pygame.font.SysFont("consolas", 16); small = pygame.font.SysFont("consolas", 13)
        home = _fibonacci_sphere(700); cx, cy = self.width / 2, self.height / 2 - 40; radius = min(self.width, self.height) * .22
        index = 0; hold_started = None; step_started = time.monotonic(); results = []; finished = False; rotation = 0; color = list(PALETTE[0]); running = True
        while running:
            dt = clock.tick(60) / 1000; now = time.monotonic()
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r: index, hold_started, results, finished, step_started = 0, None, [], False, now
            hands = self.hand_state.get_hands(); screen.fill(BG); rotation += .01
            if not finished:
                key, label, hint = STEPS[index]; matched = _detect_step(key, hands); progress = 0
                if matched:
                    hold_started = now if hold_started is None else hold_started; progress = min(1, (now - hold_started) / HOLD_REQUIRED); color = [_lerp(color[i], PALETTE[5][i], .15) for i in range(3)]
                    if progress >= 1:
                        results.append({"gesture": key, "seconds": round(now - step_started, 2)}); index += 1; hold_started = None; step_started = now
                        if index >= len(STEPS):
                            finished = True
                            if self.on_complete: self.on_complete({"steps": results, "total_seconds": round(sum(item["seconds"] for item in results), 2)})
                else:
                    hold_started = None; color = [_lerp(color[i], PALETTE[0][i], .1) for i in range(3)]
                for x, y, z in home:
                    x1, z1 = x * math.cos(rotation) - z * math.sin(rotation), x * math.sin(rotation) + z * math.cos(rotation); depth = 4 + z1
                    if depth > .1:
                        projection = 4 / depth; point = (int(cx + x1 * radius * projection), int(cy + y * radius * projection)); shade = max(.35, min(1, projection)); pygame.draw.circle(screen, tuple(int(c * shade) for c in color), point, 2)
                pygame.draw.circle(screen, (60, 60, 66), (int(cx), int(cy)), 66, 2)
                if matched: pygame.draw.arc(screen, tuple(map(int, color)), (int(cx) - 66, int(cy) - 66, 132, 132), -math.pi / 2, -math.pi / 2 + progress * math.tau, 4)
                for text, y, typeface in ((label, self.height - 150, title_font), (hint, self.height - 112, font), (f"step {index + 1} / {len(STEPS)}", self.height - 84, small)):
                    rendered = typeface.render(text, True, (236, 232, 223) if typeface != small else (110, 112, 120)); screen.blit(rendered, (cx - rendered.get_width() / 2, y))
            else:
                done = title_font.render("PRACTICE COMPLETE", True, (245, 241, 232)); screen.blit(done, (cx - done.get_width() / 2, 120)); y = 180
                for item in results:
                    screen.blit(font.render(f"{item['gesture']:<16} {item['seconds']}s", True, (200, 200, 205)), (cx - 120, y)); y += 28
                screen.blit(font.render(f"total: {sum(item['seconds'] for item in results):.2f}s", True, (236, 232, 223)), (cx - 120, y + 14)); screen.blit(small.render("press R to restart - ESC to close", True, (110, 112, 120)), (cx - 125, y + 54))
            pygame.display.flip()
        pygame.quit()
