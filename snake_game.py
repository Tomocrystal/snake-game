import pygame
import random
import sys

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 20
CELL_NUMBER_X = WINDOW_WIDTH // CELL_SIZE
CELL_NUMBER_Y = WINDOW_HEIGHT // CELL_SIZE

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

class Snake:
    def __init__(self):
        self.body = [pygame.Vector2(5, 10), pygame.Vector2(4, 10), pygame.Vector2(3, 10)]
        self.direction = pygame.Vector2(1, 0)
        self.new_block = False

    def draw_snake(self, screen):
        for block in self.body:
            x = int(block.x * CELL_SIZE)
            y = int(block.y * CELL_SIZE)
            block_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GREEN, block_rect)

    def move_snake(self):
        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]

    def add_block(self):
        self.new_block = True

    def check_collision(self):
        if not 0 <= self.body[0].x < CELL_NUMBER_X or not 0 <= self.body[0].y < CELL_NUMBER_Y:
            return True
        
        for block in self.body[1:]:
            if block == self.body[0]:
                return True
        
        return False

class Food:
    def __init__(self):
        self.randomize()

    def draw_food(self, screen):
        food_rect = pygame.Rect(int(self.pos.x * CELL_SIZE), int(self.pos.y * CELL_SIZE), CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, RED, food_rect)

    def randomize(self):
        self.x = random.randint(0, CELL_NUMBER_X - 1)
        self.y = random.randint(0, CELL_NUMBER_Y - 1)
        self.pos = pygame.Vector2(self.x, self.y)

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.running = True
        self.paused = False
        self.key_map = {
            pygame.K_UP: pygame.Vector2(0, -1),
            pygame.K_DOWN: pygame.Vector2(0, 1),
            pygame.K_LEFT: pygame.Vector2(-1, 0),
            pygame.K_RIGHT: pygame.Vector2(1, 0),
        }

    def update(self):
        if not self.paused:
            self.snake.move_snake()
            self.check_collision()
            self.check_fail()

    def draw_elements(self, screen):
        screen.fill(BLACK)
        self.food.draw_food(screen)
        self.snake.draw_snake(screen)
        
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.paused:
            pause_font = pygame.font.Font(None, 72)
            pause_surface = pause_font.render("已暂停", True, WHITE)
            pause_rect = pause_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(pause_surface, pause_rect)

    def check_collision(self):
        if self.food.pos == self.snake.body[0]:
            self.food.randomize()
            self.snake.add_block()
            self.score += 1
            
            for block in self.snake.body[1:]:
                if block == self.food.pos:
                    self.food.randomize()

    def check_fail(self):
        if self.snake.check_collision():
            self.game_over()

    def game_over(self):
        self.running = False

    def toggle_pause(self):
        self.paused = not self.paused

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.toggle_pause()
            elif not self.running and event.key == pygame.K_r:
                self.__init__()
            elif self.running and not self.paused and event.key in self.key_map:
                new_direction = self.key_map[event.key]
                if new_direction != -self.snake.direction:
                    self.snake.direction = new_direction

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('贪吃蛇游戏')
    clock = pygame.time.Clock()
    
    game = Game()
    
    SCREEN_UPDATE = pygame.USEREVENT
    pygame.time.set_timer(SCREEN_UPDATE, 150)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_input(event)

        if game.running:
            if event.type == SCREEN_UPDATE:
                game.update()
            game.draw_elements(screen)
        else:
            screen.fill(BLACK)
            title_font = pygame.font.Font(None, 72)
            score_font = pygame.font.Font(None, 48)
            prompt_font = pygame.font.Font(None, 36)
            
            title_surface = title_font.render("游戏结束", True, RED)
            score_surface = score_font.render(f"最终得分: {game.score}", True, WHITE)
            prompt_surface = prompt_font.render("按 R 键重新开始", True, WHITE)
            
            title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
            score_rect = score_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            prompt_rect = prompt_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
            
            screen.blit(title_surface, title_rect)
            screen.blit(score_surface, score_rect)
            screen.blit(prompt_surface, prompt_rect)

        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()