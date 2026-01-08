import tkinter as tk
import random
import time
import pandas as pd
import csv
from time import gmtime, strftime
import matplotlib.pyplot as plt



# Colors
background_color = 'white'
background_color_variation = 'gray'
contrast_color = 'black'
square_color = 'blue'

# Helpers

def add_row_to_csv(filename, row):
    """
    Adds a single row to an existing CSV file.

    :param filename: path to the csv file
    :param row: list of values, e.g. ["Alice", 42, "2026-01-08"]
    """
    with open(filename, mode="a", newline="\n", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(row)

class CanvasButton:
    """
    A custom button drawn on a Tkinter Canvas.
    Handles:
    - drawing
    - hover effect
    - click detection
    """

    def __init__(self, canvas, x, y, width, height, text, command,
                 bg=background_color, hover_bg=background_color_variation, fg=contrast_color, font=("Arial", 14)):

        self.canvas = canvas
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg

        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

        # Draw rectangle (button body)
        self.rect = canvas.create_rectangle(
            self.x1, self.y1, self.x2, self.y2,
            fill=self.bg,
            outline=""
        )

        # Draw text (button label)
        self.text = canvas.create_text(
            (self.x1 + self.x2) // 2,
            (self.y1 + self.y2) // 2,
            text=text,
            fill=fg,
            font=font
        )

        # Bind events
        canvas.tag_bind(self.rect, "<Enter>", self.on_enter)
        canvas.tag_bind(self.text, "<Enter>", self.on_enter)

        canvas.tag_bind(self.rect, "<Leave>", self.on_leave)
        canvas.tag_bind(self.text, "<Leave>", self.on_leave)

        canvas.tag_bind(self.rect, "<Button-1>", self.on_click)
        canvas.tag_bind(self.text, "<Button-1>", self.on_click)

    def on_enter(self, event):
        """Mouse enters button area"""
        self.canvas.itemconfig(self.rect, fill=self.hover_bg)

    def on_leave(self, event):
        """Mouse leaves button area"""
        self.canvas.itemconfig(self.rect, fill=self.bg)

    def on_click(self, event):
        """Button clicked"""
        self.command()



class ClickSquareGame:
    """
    Main game class that handles:
    - window setup
    - game state
    - drawing
    - event handling
    - timing
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Anouks Clicking Training")
        self.root.resizable(False, False)

        # === GAME SETTINGS ===
        self.WIDTH = 700
        self.HEIGHT = 700
        self.SQUARE_SIZE = 10
        self.GAME_DURATION = 15.00  # seconds

        # === GAME STATE ===
        self.score = 0
        self.misses = 0
        self.time_left = self.GAME_DURATION
        self.game_running = False
        self.start_time = None
        self.square_id = None

        # === GUI SETUP ===
        self.setup_ui()


    def setup_ui(self):
        """
        Sets up all GUI elements:
        - canvas
        - score label
        - end screen frame
        """

        # Main canvas where the game is drawn
        self.canvas = tk.Canvas(self.root, width=self.WIDTH, height=self.HEIGHT, bg=background_color)
        self.canvas.pack()

        # Score label (top-left corner)
        self.score_label = tk.Label(
            self.root,
            text="Score: 0",
            font=("Arial", 14),
            fg=contrast_color,
            bg=background_color
        )
        self.score_label.place(x=10, y=10)

        # Time label (top-left corner)
        self.time_label = tk.Label(
            self.root,
            text=f"Time: {self.time_left} s",
            font=("Arial", 14),
            fg=contrast_color,
            bg=background_color
        )
        self.time_label.place(x=10, y=30)

        # Bind mouse clicks on canvas
        self.canvas.bind("<Button-1>", self.handle_click)

        # Start the game immediately
        self.start_game()

    def show_countdown(self, count):
        """
        Displays 3-2-1 countdown before the game starts.
        """

        self.canvas.delete("all")

        if count > 0:
            self.canvas.create_text(
                self.WIDTH // 2,
                self.HEIGHT // 2,
                text=str(count),
                fill=contrast_color,
                font=("Arial", 72, "bold")
            )
            self.root.after(1000, lambda: self.show_countdown(count - 1))
        else:
            self.begin_game()


    def start_game(self):
        """
        Resets all game values and starts a new game with a countdown.
        """

        # Reset state
        self.score = 0
        self.time_left = self.GAME_DURATION
        self.game_running = False  # IMPORTANT: not running yet
        self.start_time = None

        # Update UI
        self.score_label.config(text="Score: 0")
        self.time_label.config(text=f"Time: {self.GAME_DURATION} s")
        self.canvas.delete("all")
        self.canvas.config(bg=background_color)

        # Start countdown
        self.show_countdown(5)

    def begin_game(self):
        """
        Starts the actual game after countdown.
        """

        self.canvas.delete("all")
        self.start_time = time.time()
        self.game_running = True

        self.spawn_square()
        self.update_timer()


    def spawn_square(self):
        """
        Creates a square fully inside the visible canvas area.
        """

        if self.square_id:
            self.canvas.delete(self.square_id)

        # Force update to get correct size
        self.canvas.update_idletasks()

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        max_x = canvas_width - self.SQUARE_SIZE
        max_y = canvas_height - self.SQUARE_SIZE

        x = random.randint(0, max_x)
        y = random.randint(0, max_y)

        self.square_id = self.canvas.create_rectangle(
            x,
            y,
            x + self.SQUARE_SIZE,
            y + self.SQUARE_SIZE,
            fill=square_color,
            outline=""
        )

    def handle_click(self, event):
        """
        Handles mouse clicks:
        - If square is hit -> score increases and new square spawns
        - If miss -> screen flashes white
        """

        if not self.game_running:
            return

        clicked_items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)

        if self.square_id in clicked_items:
            # HIT
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.spawn_square()
        else:
            # MISS
            self.misses += 1
            self.flash_screen()

    def flash_screen(self):
        """
        Flashes the screen briefly to indicate a miss.
        """

        self.canvas.config(bg=contrast_color)
        self.root.after(100, lambda: self.canvas.config(bg=background_color))

    def update_timer(self):
        """
        Updates the countdown timer and ends the game when time is up.
        """

        if not self.game_running:
            return

        elapsed = time.time() - self.start_time
        remaining = max(0, self.GAME_DURATION - elapsed)

        # Update label
        self.time_label.config(text=f"Time: {remaining:.2f} s")

        if remaining <= 0:
            self.end_game()
        else:
            self.root.after(100, self.update_timer)


    def save_score(self):
        date = strftime("%d.%m.%Y %H:%M", gmtime())
        score = self.score
        name = ''
        misses = self.misses
        accuracy = float(score) / (misses + score) if (misses + score) > 0 else 0.0

        add_row_to_csv('scores.csv', [date, score, name, misses, accuracy])

    def end_game(self):
        """
        Stops the game and shows the end screen using canvas buttons.
        """

        self.game_running = False
        self.canvas.delete("all")

        self.save_score()

        # Draw final score text
        self.canvas.create_text(
            self.WIDTH // 2,
            120,
            text=f"Time's up!\n\nFinal Score: {self.score}",
            fill=contrast_color,
            font=("Arial", 24),
            justify="center"
        )

        # Create Repeat button
        self.repeat_btn = CanvasButton(
            canvas=self.canvas,
            x=self.WIDTH // 2 - 100,
            y=220,
            width=200,
            height=45,
            text="Repeat",
            command=self.start_game
        )

        # Create Close button
        self.close_btn = CanvasButton(
            canvas=self.canvas,
            x=self.WIDTH // 2 - 100,
            y=280,
            width=200,
            height=45,
            text="Close Game",
            command=self.root.destroy
        )

        # Ranking
        scores_df = pd.read_csv('scores.csv')
        scores_df = scores_df.sort_values(by='score', ascending=False).head(10)

        ranking_text = "Rank  Score  Accuracy   Date\n"
        ranking_text += "-" * 40 + "\n"

        for i, row in enumerate(scores_df.itertuples(), start=1):
            # Medal for top 3
            if i == 1:
                medal = '🥇'
            elif i == 2:
                medal = '🥈'
            elif i == 3:
                medal = '🥉'
            else:
                medal = ' '

            # Format each column with fixed width
            ranking_text += f"{i:<4} {row.score:>6.0f}   {row.accuracy*100:>6.2f}%   {row.date}\n"

        self.canvas.create_text(
            self.WIDTH // 2,
            500,
            text=ranking_text,
            fill=square_color,
            font=("Courier New", 18),  # Use monospace font for perfect alignment
            justify="left"
        )




if __name__ == "__main__":
    root = tk.Tk()
    game = ClickSquareGame(root)
    root.mainloop()
