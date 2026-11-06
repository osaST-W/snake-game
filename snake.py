"""
Классическая игра "Змейка" на Python с использованием стандартной библиотеки tkinter.
Управление: Стрелки или W, A, S, D
Пауза: Пробел
Перезапуск: R или кнопка на экране
"""

import tkinter as tk
import random

# Константы игры
WIDTH = 400
HEIGHT = 400
GRID_SIZE = 20
INITIAL_SPEED = 120  # миллисекунды на шаг
SPEED_DECREMENT = 2  # ускорение при поедании яблока
MIN_SPEED = 50

COLOR_BG = "#1e1e2e"
COLOR_GRID = "#2a2b3d"
COLOR_SNAKE_HEAD = "#a6e3a1"
COLOR_SNAKE_BODY = "#94e2d5"
COLOR_FOOD = "#f38ba8"
COLOR_TEXT = "#cdd6f4"
COLOR_OVERLAY = "#11111b"


class SnakeGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Змейка на Python (Tkinter)")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_BG)

        # Переменные состояния игры
        self.score = 0
        self.high_score = 0
        self.speed = INITIAL_SPEED
        self.game_running = False
        self.is_paused = False
        self.loop_id = None

        # Верхняя панель (счёт)
        self.top_frame = tk.Frame(root, bg=COLOR_BG)
        self.top_frame.pack(fill="x", padx=15, pady=(10, 5))

        self.score_label = tk.Label(
            self.top_frame,
            text="Счёт: 0",
            font=("Segoe UI", 12, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG,
        )
        self.score_label.pack(side="left")

        self.high_score_label = tk.Label(
            self.top_frame,
            text="Рекорд: 0",
            font=("Segoe UI", 12, "bold"),
            fg="#f9e2af",
            bg=COLOR_BG,
        )
        self.high_score_label.pack(side="right")

        # Игровой холст
        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg=COLOR_BG,
            highlightthickness=1,
            highlightbackground="#45475a",
        )
        self.canvas.pack(padx=15, pady=5)

        # Подсказка по управлению
        self.help_label = tk.Label(
            root,
            text="Стрелки / WASD — движение | Пробел — пауза | R — перезапуск",
            font=("Segoe UI", 9),
            fg="#a6adc8",
            bg=COLOR_BG,
        )
        self.help_label.pack(pady=(0, 10))

        # Привязка клавиш управления
        self.root.bind("<Up>", lambda e: self.change_direction("Up"))
        self.root.bind("<Down>", lambda e: self.change_direction("Down"))
        self.root.bind("<Left>", lambda e: self.change_direction("Left"))
        self.root.bind("<Right>", lambda e: self.change_direction("Right"))
        self.root.bind("<w>", lambda e: self.change_direction("Up"))
        self.root.bind("<s>", lambda e: self.change_direction("Down"))
        self.root.bind("<a>", lambda e: self.change_direction("Left"))
        self.root.bind("<d>", lambda e: self.change_direction("Right"))
        self.root.bind("<W>", lambda e: self.change_direction("Up"))
        self.root.bind("<S>", lambda e: self.change_direction("Down"))
        self.root.bind("<A>", lambda e: self.change_direction("Left"))
        self.root.bind("<D>", lambda e: self.change_direction("Right"))
        self.root.bind("<space>", lambda e: self.toggle_pause())
        self.root.bind("<r>", lambda e: self.reset_game())
        self.root.bind("<R>", lambda e: self.reset_game())

        self.reset_game()

    def reset_game(self):
        if self.loop_id:
            self.root.after_cancel(self.loop_id)
            self.loop_id = None

        self.score = 0
        self.speed = INITIAL_SPEED
        self.score_label.config(text=f"Счёт: {self.score}")
        self.direction = "Right"
        self.next_direction = "Right"
        self.is_paused = False
        self.game_running = True

        # Начальные координаты змейки (центр поля)
        start_x = (WIDTH // GRID_SIZE // 2) * GRID_SIZE
        start_y = (HEIGHT // GRID_SIZE // 2) * GRID_SIZE
        self.snake = [
            (start_x, start_y),
            (start_x - GRID_SIZE, start_y),
            (start_x - 2 * GRID_SIZE, start_y),
        ]

        self.food = self.spawn_food()
        self.draw()
        self.game_loop()

    def spawn_food(self):
        while True:
            fx = random.randint(0, (WIDTH - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
            fy = random.randint(0, (HEIGHT - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
            if (fx, fy) not in self.snake:
                return (fx, fy)

    def change_direction(self, new_dir):
        opposites = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if self.game_running and not self.is_paused:
            if new_dir != opposites.get(self.direction):
                self.next_direction = new_dir

    def toggle_pause(self):
        if not self.game_running:
            return
        self.is_paused = not self.is_paused
        if not self.is_paused:
            self.game_loop()
        else:
            self.draw_overlay("ПАУЗА", "Нажмите ПРОБЕЛ для продолжения")

    def game_loop(self):
        if not self.game_running or self.is_paused:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]

        if self.direction == "Up":
            new_head = (head_x, head_y - GRID_SIZE)
        elif self.direction == "Down":
            new_head = (head_x, head_y + GRID_SIZE)
        elif self.direction == "Left":
            new_head = (head_x - GRID_SIZE, head_y)
        elif self.direction == "Right":
            new_head = (head_x + GRID_SIZE, head_y)

        # Проверка столкновения со стенами
        nx, ny = new_head
        if nx < 0 or nx >= WIDTH or ny < 0 or ny >= HEIGHT:
            self.game_over()
            return

        # Проверка самопересечения
        if new_head in self.snake:
            self.game_over()
            return

        self.snake.insert(0, new_head)

        # Поедание яблока
        if new_head == self.food:
            self.score += 10
            if self.score > self.high_score:
                self.high_score = self.score
                self.high_score_label.config(text=f"Рекорд: {self.high_score}")
            self.score_label.config(text=f"Счёт: {self.score}")
            self.speed = max(MIN_SPEED, self.speed - SPEED_DECREMENT)
            self.food = self.spawn_food()
        else:
            self.snake.pop()

        self.draw()
        self.loop_id = self.root.after(self.speed, self.game_loop)

    def draw(self):
        self.canvas.delete("all")

        # Сетка фона
        for x in range(0, WIDTH, GRID_SIZE):
            self.canvas.create_line(x, 0, x, HEIGHT, fill=COLOR_GRID, width=1)
        for y in range(0, HEIGHT, GRID_SIZE):
            self.canvas.create_line(0, y, WIDTH, y, fill=COLOR_GRID, width=1)

        # Еда
        fx, fy = self.food
        self.canvas.create_oval(
            fx + 2, fy + 2, fx + GRID_SIZE - 2, fy + GRID_SIZE - 2,
            fill=COLOR_FOOD, outline="#e06c75"
        )

        # Змейка
        for idx, (sx, sy) in enumerate(self.snake):
            color = COLOR_SNAKE_HEAD if idx == 0 else COLOR_SNAKE_BODY
            self.canvas.create_rectangle(
                sx + 1, sy + 1, sx + GRID_SIZE - 1, sy + GRID_SIZE - 1,
                fill=color, outline=""
            )
            # Глаза для головы
            if idx == 0:
                self.draw_eyes(sx, sy)

    def draw_eyes(self, hx, hy):
        eye_color = "#11111b"
        if self.direction == "Right":
            e1 = (hx + 14, hy + 5, hx + 17, hy + 8)
            e2 = (hx + 14, hy + 12, hx + 17, hy + 15)
        elif self.direction == "Left":
            e1 = (hx + 3, hy + 5, hx + 6, hy + 8)
            e2 = (hx + 3, hy + 12, hx + 6, hy + 15)
        elif self.direction == "Up":
            e1 = (hx + 5, hy + 3, hx + 8, hy + 6)
            e2 = (hx + 12, hy + 3, hx + 15, hy + 6)
        else:  # Down
            e1 = (hx + 5, hy + 14, hx + 8, hy + 17)
            e2 = (hx + 12, hy + 14, hx + 15, hy + 17)

        self.canvas.create_oval(*e1, fill=eye_color, outline="")
        self.canvas.create_oval(*e2, fill=eye_color, outline="")

    def draw_overlay(self, title, subtitle):
        self.canvas.create_rectangle(
            20, HEIGHT // 2 - 50, WIDTH - 20, HEIGHT // 2 + 50,
            fill=COLOR_OVERLAY, outline="#45475a", width=2
        )
        self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2 - 18,
            text=title, font=("Segoe UI", 18, "bold"), fill="#f38ba8"
        )
        self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2 + 18,
            text=subtitle, font=("Segoe UI", 10), fill=COLOR_TEXT
        )

    def game_over(self):
        self.game_running = False
        self.draw_overlay("ИГРА ОКОНЧЕНА!", "Нажмите 'R' для перезапуска")


if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
