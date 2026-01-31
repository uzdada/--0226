import pygame
import math
import time

pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dual Tire Drift Track 🏎️")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

# 색상
BG = (30, 30, 30)
ROAD = (70, 70, 70)
WALL = (20, 20, 20)
LINE = (220, 220, 220)
CAR_COLOR = (220, 60, 60)

# =========================
# 원형 서킷
# =========================
class Track:
    def __init__(self):
        self.center = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        self.outer_r = 450
        self.inner_r = 250
        self.wall_thickness = 20

    def draw(self, screen):
        screen.fill(BG)
        pygame.draw.circle(screen, WALL, self.center, self.outer_r + self.wall_thickness)
        pygame.draw.circle(screen, ROAD, self.center, self.outer_r)
        pygame.draw.circle(screen, WALL, self.center, self.inner_r)
        pygame.draw.circle(screen, ROAD, self.center, self.inner_r - self.wall_thickness)
        pygame.draw.circle(screen, LINE, self.center, (self.outer_r + self.inner_r) // 2, 3)

    def collision(self, pos):
        d = pos.distance_to(self.center)
        return d > self.outer_r + self.wall_thickness or d < self.inner_r

# =========================
# 자동차 및 타이어 마킹
# =========================
class TireMark:
    def __init__(self, pos, angle):
        self.pos = pos
        self.angle = angle
        self.life = 200  # 흔적 남는 시간

class Car:
    def __init__(self):
        self.reset()
        self.last_drift_time = 0
        self.tire_marks = []

    def reset(self):
        self.pos = pygame.Vector2(WIDTH // 2 + 400, HEIGHT // 2)
        self.vel = pygame.Vector2(0, 0)
        self.angle = -90
        self.engine = 0.35
        self.max_speed = 12
        self.turn_rate = 3.2
        self.friction = 0.965
        self.size = (36, 18)
        self.tire_marks = []

    def update(self, keys, track):
        speed = self.vel.length()

        # 가속/감속
        if keys[pygame.K_w]:
            forward = pygame.Vector2(math.cos(math.radians(self.angle)),
                                     math.sin(math.radians(self.angle)))
            self.vel += forward * self.engine
        if keys[pygame.K_s]:
            self.vel *= 0.92

        # 조향
        if speed > 0.4:
            steer = self.turn_rate * (speed / self.max_speed)
            if keys[pygame.K_a]:
                self.angle -= steer
            if keys[pygame.K_d]:
                self.angle += steer

        # 속도 제한
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)

        # 마찰 적용
        self.vel *= self.friction
        self.pos += self.vel

        # 벽 충돌
        if track.collision(self.pos):
            self.vel *= -0.5
            self.pos += self.vel

        # 드리프트 감지
        drift_points = 0
        if speed > 3:
            vel_dir = math.degrees(math.atan2(self.vel.y, self.vel.x))
            diff_angle = abs((vel_dir - self.angle + 180) % 360 - 180)
            if diff_angle > 25:
                # 좌우 타이어 마킹
                w, h = self.size
                left_offset = pygame.Vector2(-w/2, h/4).rotate(self.angle)
                right_offset = pygame.Vector2(-w/2, -h/4).rotate(self.angle)
                self.tire_marks.append(TireMark(self.pos + left_offset, self.angle))
                self.tire_marks.append(TireMark(self.pos + right_offset, self.angle))

                current_time = time.time()
                if current_time - self.last_drift_time >= 1:
                    self.last_drift_time = current_time
                    drift_points = 10

        # 흔적 수명 감소
        for mark in self.tire_marks:
            mark.life -= 1
        self.tire_marks = [m for m in self.tire_marks if m.life > 0]

        return drift_points

    def draw(self, screen):
        # 타이어 흔적 그리기 (좌·우, 길쭉 직사각형, 투명도)
        for mark in self.tire_marks:
            surf = pygame.Surface((12, 4), pygame.SRCALPHA)
            alpha = int(255 * (mark.life / 200))
            surf.fill((10, 10, 10, alpha))
            rotated = pygame.transform.rotate(surf, -mark.angle)
            rect = rotated.get_rect(center=(mark.pos.x, mark.pos.y))
            screen.blit(rotated, rect)

        # 자동차 그리기
        w, h = self.size
        shape = [
            pygame.Vector2(w/2, 0),
            pygame.Vector2(w/4, h/2),
            pygame.Vector2(-w/2, h/2),
            pygame.Vector2(-w/2, -h/2),
            pygame.Vector2(w/4, -h/2),
        ]
        rotated = [p.rotate(self.angle) + self.pos for p in shape]
        pygame.draw.polygon(screen, CAR_COLOR, rotated)

# =========================
# 메인
# =========================
def main():
    track = Track()
    car = Car()
    running = True
    score = 0

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            car.reset()
            score = 0

        drift_points = car.update(keys, track)
        score += drift_points

        track.draw(screen)
        car.draw(screen)

        ui = font.render(f"WASD Drive | R Reset | Drift Score: {score}", True, (230, 230, 230))
        screen.blit(ui, (20, 20))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
