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
SHAPES_1 = [ # Фигуры начальной сложности
    [[1]],                   # 1 I-образная
    [[1, 1]],                # 2 I-образная
    [[1, 1, 1]],             # 3 I-образная
    [[0, 1, 0], [1, 1, 1]],  # 4 T-маленькая
    [[1, 0, 0], [1, 1, 1]],  # 4 L-образная
    [[0, 0, 1], [1, 1, 1]],  # 4 J-образная
    [[1, 1], [1, 1]],        # 4 O-образная
]
SHAPES_2 = [ # Фигуры 2
    [[1, 1, 0], [0, 1, 1]],  # 4 Z-образная
    [[0, 1, 1], [1, 1, 0]],  # 4 S-образная
]
SHAPES_3 = [ # Фигуры 3
    [[1, 1, 1, 1]],          # 4 I-образная
    [[1, 1, 1, 1, 1]],       # 5 I-образная
]
SHAPES_4 = [ # Фигуры 4
    [[0, 1, 0], [0, 1, 0], [1, 1, 1]],  # 5 Т-большая
]
SHAPES_5 = [ # Фигуры 5
    [[1, 1], [1, 1], [1, 0]],  # 5 6-образная
    [[1, 1], [1, 1], [0, 1]],  # 5 d-образная
]
SHAPES_6 = [ # Фигуры 6
    [[1, 0, 1], [1, 1, 1]],    # 5 П-образная
]
SHAPES_7 = [ # Фигуры 7
    [[1, 0, 0], [1, 0, 0], [1, 1, 1]],   # 5 Г-образная
]
SHAPES_8 = [ # Фигуры 8
    [[1, 1, 0], [0, 1, 0], [0, 1, 1]],   # 5 3-образная
]
SHAPES_9 = [ # Фигуры 9
    [[1, 1, 1, 1], [0, 0, 0, 1]],   # 5 Г-длинная
    [[1, 1, 1, 1], [1, 0, 0, 0]],   # 5 L-длинная
]
SHAPES_10 = [ # Фигуры 10
    [[1, 1, 1, 0], [0, 0, 1, 1]],   # 5 Z-длинная
    [[0, 1, 1, 1], [1, 1, 0, 0]],   # 5 S-длинная
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
        # Инициализация игрового окна и начальных параметров
        self.screen = pygame.display.set_mode((SCREEN_WIDTH + 400, SCREEN_HEIGHT))
        pygame.display.set_caption("Малиновый Тетрис")
        self.clock = pygame.time.Clock()

        self.music_volume = 0.5 # Громкость музыки
        self.move_volume = 0.5 # Громкость кнопок управления блоками
        self.clear_volume = 0.8  # Громкость исчезающих строк
        self.over_volume = 0.5   # Громкость конца игры
        pygame.mixer.music.set_volume(self.music_volume)
        move_sound.set_volume(self.move_volume)
        clear_sound.set_volume(self.clear_volume)
        game_over_sound.set_volume(self.over_volume)

        # Создаём пустую сетку (игровое поле)
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

        # Создаем рекорды
        self.record = 0
        self.records = []
        self.load_record()  # ← Здесь загружаем рекорд
        self.best_score = self.get_best_record() # получаем лучший рекорд

        self.level_tresh = {
            1: SHAPES_1,
            2: SHAPES_1 + SHAPES_2,
            3: SHAPES_1 + SHAPES_2 + SHAPES_3,
            4: SHAPES_1 + SHAPES_2 + SHAPES_3 + SHAPES_4,
            5: SHAPES_1 + SHAPES_2 + SHAPES_3 + SHAPES_4 + SHAPES_5,
            6: SHAPES_1 + SHAPES_2 + SHAPES_3 + SHAPES_4 + SHAPES_5 + SHAPES_6,
            7: SHAPES_1 + SHAPES_2 + SHAPES_3 + SHAPES_4 + SHAPES_5 + SHAPES_6 + SHAPES_7,
            8: SHAPES_1 + SHAPES_2 + SHAPES_3 + SHAPES_4 + SHAPES_5 + SHAPES_6 + SHAPES_7 + SHAPES_8,
            9: SHAPES_1 + SHAPES_2 + SHAPES_3 + SHAPES_4 + SHAPES_5 + SHAPES_6 + SHAPES_7 + SHAPES_8 + SHAPES_9,
            10: SHAPES_1 + SHAPES_2 + SHAPES_3 + SHAPES_4 + SHAPES_5 + SHAPES_6 + SHAPES_7 + SHAPES_8 + SHAPES_9 + SHAPES_10
        }

        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 1000
        self.fall_time = 0

        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.x = COLS // 2 - len(self.current_piece[0]) // 2
        self.y = 0
        self.game_over = False



    def load_record(self): # Загружаем рекорды из файла
        self.records = []
        if os.path.exists("records.txt"):
            with open("records.txt", "r") as f:
                lines = f.readlines()
                for line in lines:
                    if ": " in line:
                        name, score = line.strip().split(": ")
                        try:
                            self.records.append((name, int(score)))
                        except ValueError:
                            continue
            self.records.sort(key=lambda x: x[1], reverse=True)

    def get_best_record(self): # Лучший рекорд
        if self.records:
            return self.records[0][1]
        else:
            return 0

    def load_record(self): # Загружаем рекорды из файла
        self.records = []
        if os.path.exists("records.txt"):
            with open("records.txt", "r") as f:
                lines = f.readlines()
                for line in lines:
                    if ": " in line:
                        name, score_str = line.strip().split(": ")
                        try:
                            score = int(score_str)
                            self.records.append((name, score))
                        except ValueError:
                            continue
        self.records.sort(key=lambda x: x[1], reverse=True)

    def save_record(self, name="Player", top_n = 10): # Добавление нового рекорда в топ 10
        self.load_record()  # ← Загружаем старые рекорseды перед добавлением
        self.records.append((name, self.score))
        self.records.sort(key=lambda x: x[1], reverse=True)
        with open("records.txt", "w") as f:
            for name, score in self.records[:10]:  # Сохраняем топ-10
                f.write(f"{name}: {score}\n")

    def input_name_screen(self):
        font = pygame.font.SysFont("Arial", 24)
        input_text = ""
        typing = True
        while typing:
            self.screen.fill(BACKGROUND_COLOR)
            prompt = font.render("Введите имя:", True, MALINA_COLOR)
            text = font.render(input_text + "_", True, (255, 255, 255))
            self.screen.blit(prompt, (50, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(text, (50, SCREEN_HEIGHT // 2))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and input_text:
                        typing = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif len(input_text) < 10 and event.unicode.isalnum():
                        input_text += event.unicode

        self.save_record(input_text or "Anon")

    def new_piece(self): # Создатm случайную фигуру в зависимости от текущего уровня
        if self.level >= 10:
            available_shapes = SHAPES_1 + SHAPES_2 + SHAPES_3 + SHAPES_4 + SHAPES_5 + SHAPES_6 + SHAPES_7 + SHAPES_8 + SHAPES_9 + SHAPES_10
        elif self.level >= 9:
            available_shapes = SHAPES_1 + SHAPES_2 + SHAPES_3 + SHAPES_4 + SHAPES_5 + SHAPES_6 + SHAPES_7 + SHAPES_8 + SHAPES_9
        elif self.level >= 8:
            available_shapes = SHAPES_1 + SHAPES_2 + SHAPES_3 + SHAPES_4 + SHAPES_5 + SHAPES_6 + SHAPES_7 + SHAPES_8
        elif self.level >= 7:
            available_shapes = SHAPES_1 + SHAPES_2 + SHAPES_3 + SHAPES_4 + SHAPES_5 + SHAPES_6 + SHAPES_7
        elif self.level >= 6:
            available_shapes = SHAPES_1 + SHAPES_2 + SHAPES_3 + SHAPES_4 + SHAPES_5 + SHAPES_6
        elif self.level >= 5:
            available_shapes = SHAPES_1 + SHAPES_2 + SHAPES_3 + SHAPES_4 + SHAPES_5
        elif self.level >= 4:
            available_shapes = SHAPES_1 + SHAPES_2 + SHAPES_3 + SHAPES_4
        elif self.level >= 3:
            available_shapes = SHAPES_1 + SHAPES_2 + SHAPES_3
        elif self.level >= 2:
            available_shapes = SHAPES_1 + SHAPES_2
        else:
            available_shapes = SHAPES_1

        return [[1 if cell else 0 for cell in row] for row in random.choice(available_shapes)]

    def draw_grid(self):
        """Рисует текущее состояние игрового поля (сетку с заполненными блоками)."""
        for row in range(len(self.grid)):
            for col in range(COLS):
                color = MALINA_COLOR if self.grid[row][col] else BACKGROUND_COLOR
                pygame.draw.rect(self.screen, color,
                                 (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(self.screen, GRID_COLOR,
                                 (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_grid_with_flash(self, lines, flash_color):
        """Рисует сетку с подсветкой указанных строк."""
        for row in range(len(self.grid)):
            for col in range(COLS):
                if row in lines:
                    pygame.draw.rect(self.screen, flash_color,
                                     (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                else:
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
        Проверяем столкновение фигуры с границами или другими блоками.
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

    def lock_piece(self): # Фиксим фигуру на поле и создаем новую
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

    def animate_lines_cleared(self, lines):
        """Анимация вспышки перед удалением строк."""
        print(f"Анимация строк: {lines}")
        # Цвета для анимации
        flash_colors = [MALINA_COLOR, (255, 100, 180), (255, 200, 230)]

        for _ in range(3):  # Три вспышки
            for color in flash_colors:
                self.screen.fill(BACKGROUND_COLOR)
                self.draw_grid_with_flash(lines, color)
                self.draw_next_piece()
                self.draw_score()
                pygame.display.flip()
                pygame.time.delay(60)  # Время между кадрами анимации

        # Удаление строк после анимации
        for row in sorted(lines, reverse=False):
            del self.grid[row]
            self.grid.insert(0, [0 for _ in range(COLS)])

        try:
            clear_sound.play()
        except:
            pass

    def clear_lines(self):
        """Проверяет, очищает и возвращает количество линий."""
        lines_to_clear = [row for row in range(len(self.grid)) if all(self.grid[row])]
        if lines_to_clear:
            self.animate_lines_cleared(lines_to_clear)
        return len(lines_to_clear)

    def rotate_piece(self): # Поворот фигуры, если нет коллизии
        rotated = list(zip(*self.current_piece[::-1]))  # Поворот матрицы
        if not self.check_collision(piece=rotated):
            self.current_piece = rotated
            try:
                move_sound.play()
            except:
                pass

    def hard_drop(self): # Сразу вниз
        while not self.check_collision(dy=1):
            self.y += 1
        try:
            move_sound.play()
        except:
            pass

    def draw_next_piece(self): # показываем следующую фигуру справа
        x_offset = COLS * BLOCK_SIZE + 10
        y_offset = 10
        pygame.draw.rect(self.screen, NEXT_PIECE_BG, (x_offset, y_offset, 150, 150))
        for row in range(len(self.next_piece)):
            for col in range(len(self.next_piece[0])):
                if self.next_piece[row][col]:
                    pygame.draw.rect(self.screen, MALINA_COLOR,
                                     (x_offset + col * BLOCK_SIZE,
                                      y_offset + row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(self.screen, GRID_COLOR,
                                     (x_offset + col * BLOCK_SIZE,
                                      y_offset + row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_score(self):
        """Отображает текущие очки, уровень и количество удалённых линий."""
        font = pygame.font.SysFont("Arial", 18)
        score_text = font.render(f"Очки: {self.score}", True, (255, 255, 255))
        level_text = font.render(f"Уровень: {self.level}", True, (255, 255, 255))
        lines_text = font.render(f"Линии: {self.lines_cleared}", True, (255, 255, 255))
        music_volume_text = font.render(f"Громкость музыки: {int(self.music_volume * 100)}%", True, (255, 255, 255))
        m_v_text = font.render(f"повысить: + понизить: -",True, (255, 255, 255))
        move_volume_text = font.render(f"Громкость кнопок: {int(self.move_volume * 100)}%", True, (255, 255, 255))
        move_v_text = font.render(f"повысить: e понизить: w", True,(255, 255, 255))
        clear_volume_text = font.render(f"Громкость стирания линий: {int(self.clear_volume * 100)}%", True, (255, 255, 255))
        c_v_text = font.render(f"повысить: f понизить: d", True, (255, 255, 255))
        over_volume_text = font.render(f"Громкость завершения: {int(self.over_volume * 100)}%", True, (255, 255, 255))
        o_v_text = font.render(f"повысить: v понизить: c", True, (255, 255, 255))
        record_text = font.render(f"Рекорд: {self.best_score}", True, MALINA_COLOR)
        pause_text = font.render(f"Пауза - P", True, (255, 255, 255))
        self.screen.blit(record_text, (COLS * BLOCK_SIZE + 10, 170))
        self.screen.blit(score_text, (COLS * BLOCK_SIZE + 10, 200))
        self.screen.blit(level_text, (COLS * BLOCK_SIZE + 10, 230))
        self.screen.blit(lines_text, (COLS * BLOCK_SIZE + 10, 260))
        self.screen.blit(music_volume_text, (COLS * BLOCK_SIZE + 10, 290))
        self.screen.blit(m_v_text, (COLS * BLOCK_SIZE + 10, 305))
        self.screen.blit(move_volume_text, (COLS * BLOCK_SIZE + 10, 320))
        self.screen.blit(move_v_text, (COLS * BLOCK_SIZE + 10, 335))
        self.screen.blit(clear_volume_text, (COLS * BLOCK_SIZE + 10, 350))
        self.screen.blit(c_v_text, (COLS * BLOCK_SIZE + 10, 365))
        self.screen.blit(over_volume_text, (COLS * BLOCK_SIZE + 10, 380))
        self.screen.blit(o_v_text, (COLS * BLOCK_SIZE + 10, 395))
        self.screen.blit(pause_text, (COLS * BLOCK_SIZE + 10, 420))


    def pause_menu(self):
        paused = True
        font = pygame.font.SysFont("Arial", 24)
        options = ["Продолжить (P)", "Перезапустить (R)", "Выход (Q)"]
        selected = 0

        while paused:
            self.screen.fill(BACKGROUND_COLOR)
            y = SCREEN_HEIGHT // 2 - 60
            for i, opt in enumerate(options):
                color = MALINA_COLOR if i == selected else (255, 255, 255)
                text = font.render(opt, True, color)
                self.screen.blit(text, (50, y))
                y += 40

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_p:
                        paused = False
                    elif event.key == pygame.K_r:
                        self.__init__()  # Пересоздаём игру
                        paused = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        exit()

    def change_music_volume(self, delta): # Изменение громкости фоновой музыки
        self.music_volume = max(0.0, min(1.0, self.music_volume + delta))
        pygame.mixer.music.set_volume(self.music_volume)
        print(f"Громкость музыки: {self.music_volume:.2f}")

    def change_move_volume(self, delta): # Изменение громкости нажатия кнопок
        self.move_volume = max(0.0, min(1.0, self.move_volume + delta))
        move_sound.set_volume(self.move_volume)

    def change_clear_volume(self, delta):  # Изменение громкости исчезающих линий
        self.clear_volume = max(0.0, min(1.0, self.clear_volume + delta))
        clear_sound.set_volume(self.clear_volume)

    def change_over_volume(self, delta):  # Изменение громкости исчезающих линий
        self.over_volume = max(0.0, min(1.0, self.over_volume + delta))
        game_over_sound.set_volume(self.over_volume)

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
                    if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.change_music_volume(0.1)   # + — повысить громкость музыки
                    elif event.key == pygame.K_MINUS:
                        self.change_music_volume(-0.1)  # - — понизить громкость музыки
                    if event.key == pygame.K_e:
                        self.change_move_volume(0.1)   # e — повысить громкость кнопок
                    elif event.key == pygame.K_w:
                        self.change_move_volume(-0.1)  # w — понизить громкость кнопок
                    elif event.key == pygame.K_f:
                        self.change_clear_volume(0.1)  # f — повысить громкость исчезания строк
                    elif event.key == pygame.K_d:
                        self.change_clear_volume(-0.1) # d — понизить громкость исчезания строк
                    elif event.key == pygame.K_v:
                        self.change_clear_volume(0.1)  # v — повысить громкость конца
                    elif event.key == pygame.K_c:
                        self.change_clear_volume(-0.1) # c — понизить громкость конца
                    if event.key == pygame.K_p:
                        self.pause_menu()
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
                    # pygame.time.delay(100)  # Добавляем паузу для обновления экрана
                self.fall_time = 0

            self.draw_grid()
            self.draw_piece()
            self.draw_next_piece()
            self.draw_score()
            # self.draw_volume()
            pygame.display.flip()
        pygame.mixer.music.stop()  # Стоп музыка
        pygame.time.delay(500)  # Пауза между музыкой и звуком окончания
        try:
            game_over_sound.play()
            pygame.time.delay(300)  # Ждём окончания звука
        except:
            pass
        self.input_name_screen()  # Запрашиваем имя при завершении
        pygame.quit()


# Запуск игры
if __name__ == "__main__":
    game = TetrisGame()
    game.run()