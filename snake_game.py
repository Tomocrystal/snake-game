import pygame
import random
import sys

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 20
CELL_NUMBER_X = WINDOW_WIDTH // CELL_SIZE
CELL_NUMBER_Y = WINDOW_HEIGHT // CELL_SIZE

BACKGROUND_COLOR = (30, 30, 30)
GRID_COLOR = (45, 45, 45)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
SCREEN_UPDATE_EVENT = pygame.USEREVENT


def draw_grid(screen: pygame.Surface) -> None:
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))


class Snake:
    def __init__(self):
        self.reset()

    @property
    def head(self) -> pygame.Vector2:
        return self.body[0]

    def reset(self) -> None:
        self.body = [
            pygame.Vector2(5, 10),
            pygame.Vector2(4, 10),
            pygame.Vector2(3, 10),
        ]
        self.direction = pygame.Vector2(1, 0)
        self.new_block = False

    def draw_snake(self, screen: pygame.Surface) -> None:
        for block in self.body:
            x = int(block.x * CELL_SIZE)
            y = int(block.y * CELL_SIZE)
            block_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GREEN, block_rect)

    def move_snake(self) -> None:
        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]

    def add_block(self) -> None:
        self.new_block = True

    def set_direction(self, new_direction: pygame.Vector2) -> None:
        if self.direction + new_direction != pygame.Vector2(0, 0):
            self.direction = new_direction

    def check_collision(self) -> bool:
        if not 0 <= self.head.x < CELL_NUMBER_X or not 0 <= self.head.y < CELL_NUMBER_Y:
            return True

        for block in self.body[1:]:
            if block == self.head:
                return True

        return False


class Food:
    def __init__(self, occupied=None):
        self.randomize(occupied)

    def draw_food(self, screen: pygame.Surface) -> None:
        food_rect = pygame.Rect(int(self.pos.x * CELL_SIZE), int(self.pos.y * CELL_SIZE), CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, RED, food_rect)

    def randomize(self, occupied=None) -> None:
        occupied = occupied or []
        while True:
            self.x = random.randint(0, CELL_NUMBER_X - 1)
            self.y = random.randint(0, CELL_NUMBER_Y - 1)
            self.pos = pygame.Vector2(self.x, self.y)
            if self.pos not in occupied:
                break


class Game:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 64)
        self.speed_ms = 150
        self.reset()

    def reset(self) -> None:
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.score = 0
        self.game_over = False
        self.speed_ms = 150
        pygame.time.set_timer(SCREEN_UPDATE_EVENT, self.speed_ms)

    def update(self) -> None:
        if self.game_over:
            return

        self.snake.move_snake()
        self.check_food_collision()
        self.check_fail()

    def draw_elements(self, screen: pygame.Surface) -> None:
        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen)
        self.food.draw_food(screen)
        self.snake.draw_snake(screen)

        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            self.draw_game_over(screen)

    def draw_game_over(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        game_over_text = self.large_font.render("游戏结束", True, WHITE)
        restart_text = self.font.render("按 R 键重新开始", True, WHITE)

        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))

        screen.blit(game_over_text, game_over_rect)
        screen.blit(restart_text, restart_rect)

    def check_food_collision(self) -> None:
        if self.food.pos == self.snake.head:
            self.food.randomize(self.snake.body)
            self.snake.add_block()
            self.score += 1
            self.update_speed()

    def update_speed(self) -> None:
        new_speed = max(60, 150 - self.score * 5)
        if new_speed != self.speed_ms:
            self.speed_ms = new_speed
            pygame.time.set_timer(SCREEN_UPDATE_EVENT, self.speed_ms)

    def check_fail(self) -> None:
        if self.snake.check_collision():
            self.game_over = True

    def handle_key(self, key: int) -> None:
        if key == pygame.K_r and self.game_over:
            self.reset()
            return

        if self.game_over:
            return

        if key == pygame.K_UP:
            self.snake.set_direction(pygame.Vector2(0, -1))
        elif key == pygame.K_DOWN:
            self.snake.set_direction(pygame.Vector2(0, 1))
        elif key == pygame.K_RIGHT:
            self.snake.set_direction(pygame.Vector2(1, 0))
        elif key == pygame.K_LEFT:
            self.snake.set_direction(pygame.Vector2(-1, 0))

    def quit(self) -> None:
        pygame.quit()
        sys.exit()


def main() -> None:
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("贪吃蛇游戏")
    clock = pygame.time.Clock()

    game = Game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == SCREEN_UPDATE_EVENT:
                game.update()
            elif event.type == pygame.KEYDOWN:
                if event.key in {pygame.K_ESCAPE, pygame.K_q}:
                    running = False
                else:
                    game.handle_key(event.key)

        game.draw_elements(screen)
        pygame.display.flip()
        clock.tick(60)

    game.quit()


if __name__ == "__main__":
    main()
