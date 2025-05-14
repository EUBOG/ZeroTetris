import pygame
import random
import os

# Инициализация Pygame
pygame.init()
pygame.mixer.init()  # Для звука

# Константы
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
ROWS = SCREEN_HEIGHT // BLOCK_SIZE
COLS = SCREEN_WIDTH // BLOCK_SIZE
FPS = 60

# Цвета
BACKGROUND_COLOR = (10, 10, 10)
MALINA_COLOR = (255, 0, 128)  # Малиновый цвет
GRID_COLOR = (50, 50, 50)
NEXT_PIECE_BG = (30, 30, 30)

# Фигуры (тетромино)
SHAPES = [
    [[1, 1, 1, 1]],          # I-образная
    [[1, 1], [1, 1]],        # O-образная
    [[0, 1, 0], [1, 1, 1]],  # T-образная
    [[1, 1, 0], [0, 1, 1]],  # Z-образная
    [[0, 1, 1], [1, 1, 0]],  # S-образная
    [[1, 0, 0], [1, 1, 1]],  # L-образная
    [[0, 0, 1], [1, 1, 1]],  # J-образная
    [[0, 1, 0], [0, 1, 0], [1, 1, 1]],  # Т-большая
    [[1, 0, 1], [1, 1, 1]],             # П-образная
    [[1, 0, 0], [1, 0, 0], [1, 1, 1]]   # Г-образная
]

# Загрузка звуков
try:
    sound_path = os.path.dirname(__file__)
    move_sound = pygame.mixer.Sound(os.path.join(sound_path, "move.wav"))
    clear_sound = pygame.mixer.Sound(os.path.join(sound_path, "line_clear.wav"))
    game_over_sound = pygame.mixer.Sound(os.path.join(sound_path, "game_over.wav"))
    pygame.mixer.music.load(os.path.join(sound_path, "background.mp3"))
    pygame.mixer.music.play(-1)  # Бесконечное воспроизведение фона
except Exception as e:
    print("Не удалось загрузить звуки:", e)


class TetrisGame:
    def __init__(self):
        """Инициализация игрового окна и начальных параметров."""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH + 100, SCREEN_HEIGHT))
        pygame.display.set_caption("Малиновый Тетрис")
        self.clock = pygame.time.Clock()

        # Создаём пустую сетку (игровое поле)
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.x = COLS // 2 - len(self.current_piece[0]) // 2
        self.y = 0
        self.game_over = False

        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 1000
        self.fall_time = 0

    def new_piece(self):
        """Создает новую случайную фигуру из списка SHAPES."""
        return [[1 if cell else 0 for cell in row] for row in random.choice(SHAPES)]

    def draw_grid(self):
        """Рисует текущее состояние игрового поля (сетку с заполненными блоками)."""
        for row in range(ROWS):  # ← Теперь используем ROWS, а не len(self.grid)
            for col in range(COLS):
                color = MALINA_COLOR if self.grid[row][col] else BACKGROUND_COLOR
                pygame.draw.rect(self.screen, color,
                                 (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(self.screen, GRID_COLOR,
                                 (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_piece(self, piece=None, offset_x=0, offset_y=0):
        """Рисует указанную фигуру по заданным координатам."""
        piece = piece or self.current_piece
        for row in range(len(piece)):
            for col in range(len(piece[0])):
                if piece[row][col]:
                    pygame.draw.rect(self.screen, MALINA_COLOR,
                                     ((self.x + col + offset_x) * BLOCK_SIZE,
                                      (self.y + row + offset_y) * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(self.screen, GRID_COLOR,
                                     ((self.x + col + offset_x) * BLOCK_SIZE,
                                      (self.y + row + offset_y) * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE), 1)

    def check_collision(self, dx=0, dy=0, piece=None):
        """
        Проверяет столкновение фигуры с границами или другими блоками.
        :param dx: смещение по X
        :param dy: смещение по Y
        :param piece: текущая фигура (можно передать другую)
        :return: True, если есть коллизия
        """
        piece = piece or self.current_piece
        for row in range(len(piece)):
            for col in range(len(piece[0])):
                if piece[row][col]:
                    new_x = self.x + col + dx
                    new_y = self.y + row + dy
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS or self.grid[new_y][new_x]:
                        return True
        return False

    def lock_piece(self):
        """Фиксирует фигуру на игровом поле и создаёт новую."""
        for row in range(len(self.current_piece)):
            for col in range(len(self.current_piece[0])):
                if self.current_piece[row][col]:
                    self.grid[self.y + row][self.x + col] = 1

        lines = self.clear_lines()
        print(f"Очищено линий: {lines}")
        self.score += lines * 100
        self.lines_cleared += lines
        self.level = self.lines_cleared // 10 + 1
        self.fall_speed = max(200, 1000 - self.level * 70)

        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        self.x = COLS // 2 - len(self.current_piece[0]) // 2
        self.y = 0

        if self.check_collision():
            self.game_over = True
            try:
                print("Игра окончена, проигрываем звук...")
                game_over_sound.play()
                pygame.time.delay(1500)
            except Exception as e:
                print("Ошибка воспроизведения game_over_sound:", e)

    def clear_lines(self):
        """Очищает полностью заполненные линии, сохраняя фиксированное количество строк."""
        lines_to_clear = [row for row in range(ROWS) if all(self.grid[row])]  # ← теперь ROWS
        print(f"Очищаем строки: {lines_to_clear}")

        cleared = 0
        for row in reversed(lines_to_clear):
            del self.grid[row]
            self.grid.insert(0, [0 for _ in range(COLS)])
            cleared += 1

        try:
            if lines_to_clear:
                clear_sound.play()
        except:
            pass

        return cleared

    def rotate_piece(self):
        """Поворачивает текущую фигуру на 90 градусов, если нет коллизии."""
        rotated = list(zip(*self.current_piece[::-1]))  # Поворот матрицы
        if not self.check_collision(piece=rotated):
            self.current_piece = rotated
            try:
                move_sound.play()
            except:
                pass

    def hard_drop(self):
        """Мгновенно опускает фигуру в самый низ."""
        while not self.check_collision(dy=1):
            self.y += 1
        try:
            move_sound.play()
        except:
            pass

    def draw_next_piece(self):
        """Отображает следующую фигуру справа от основного поля."""
        x_offset = COLS * BLOCK_SIZE + 10
        y_offset = 50
        pygame.draw.rect(self.screen, NEXT_PIECE_BG, (x_offset, y_offset, 90, 90))
        for row in range(len(self.next_piece)):
            for col in range(len(self.next_piece[0])):
                if self.next_piece[row][col]:
                    pygame.draw.rect(self.screen, MALINA_COLOR,
                                     (x_offset + col * BLOCK_SIZE // 2,
                                      y_offset + row * BLOCK_SIZE // 2,
                                      BLOCK_SIZE // 2, BLOCK_SIZE // 2))

    def draw_score(self):
        """Отображает текущие очки, уровень и количество удалённых линий."""
        font = pygame.font.SysFont("Arial", 18)
        score_text = font.render(f"Очки: {self.score}", True, (255, 255, 255))
        level_text = font.render(f"Уровень: {self.level}", True, (255, 255, 255))
        lines_text = font.render(f"Линии: {self.lines_cleared}", True, (255, 255, 255))
        self.screen.blit(score_text, (COLS * BLOCK_SIZE + 10, 200))
        self.screen.blit(level_text, (COLS * BLOCK_SIZE + 10, 230))
        self.screen.blit(lines_text, (COLS * BLOCK_SIZE + 10, 260))

    def run(self):
        """Основной игровой цикл."""
        while not self.game_over:
            self.screen.fill(BACKGROUND_COLOR)
            self.fall_time += self.clock.get_rawtime()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and not self.check_collision(dx=-1):
                        self.x -= 1
                        try:
                            move_sound.play()
                        except:
                            pass
                    if event.key == pygame.K_RIGHT and not self.check_collision(dx=1):
                        self.x += 1
                        try:
                            move_sound.play()
                        except:
                            pass
                    if event.key == pygame.K_DOWN and not self.check_collision(dy=1):
                        self.y += 1
                    if event.key == pygame.K_UP:
                        self.rotate_piece()
                    if event.key == pygame.K_SPACE:
                        self.hard_drop()

            if self.fall_time > self.fall_speed:
                if not self.check_collision(dy=1):
                    self.y += 1
                else:
                    self.lock_piece()
                    pygame.time.delay(100)  # Добавляем паузу для обновления экрана
                self.fall_time = 0

            self.draw_grid()
            self.draw_piece()
            self.draw_next_piece()
            self.draw_score()
            pygame.display.flip()

        try:
            game_over_sound.play()
        except:
            pass
        pygame.quit()


# Запуск игры
if __name__ == "__main__":
    game = TetrisGame()
    game.run()