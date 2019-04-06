import curses
from random import shuffle
from enum import Enum


class FieldCellState(Enum):
    FREE = 0
    MINE = -1


class CoverState(Enum):
    COVERED = 1
    OPENED = 0
    FLAG = 2


KEY_UP = 65
KEY_DOWN = 66
KEY_LEFT = 67
KEY_RIGHT = 68


class Game:

    def __init__(self):
        self.field_height = 0
        self.field_width = 0
        self.field = []
        self.cover = []

    def build(self, height, width, x, y, num_of_mines):
        """Makes game ready to play."""
        self.field_height = height
        self.field_width = width
        self.field = [[0 for j in range(self.field_width)]
                      for i in range(self.field_height)]
        self.cover = [[1 for j in range(self.field_width)]
                      for i in range(self.field_height)]
        self.set_mines(x, y, num_of_mines)
        self.count_mines()
        self.open_square(x, y)

    def clear_field(self):
        """Makes field free from mines"""
        for i in self.field:
            for j in i:
                j = FieldCellState.FREE

    def set_mines(self, x, y, num_of_mines):
        """Sets mines somewhere, except for (x, y)."""
        coord_pairs = list(set([(i, j) for i in range(self.field_height)
                                for j in range(self.field_width)]) - {(x, y)})
        shuffle(coord_pairs)
        to_push = coord_pairs[0:num_of_mines]
        for i in to_push:
            self.field[i[0]][i[1]] = FieldCellState.MINE

    def count_mines(self):
        """For each square counts number of mines next to it."""
        for i in range(0, self.field_height):
            for j in range(0, self.field_width):
                if self.field[i][j] != -1:
                    for delta_i in range(-1, 2):
                        for delta_j in range(-1, 2):
                            if (not (delta_i == 0 and delta_j == 0) and
                                    0 <= i + delta_i < self.field_height and
                                    0 <= j + delta_j < self.field_width and
                                    self.field[i + delta_i][j + delta_j]
                                    == -1):
                                self.field[i][j] = self.field[i][j] + 1

    def open_square(self, x, y):
        """Opens square of the field."""
        if self.cover[x][y] in {0, 2}:
            return False
        if self.cover[x][y] == 1:
            if self.field[x][y] == -1:
                return True
            self.cover[x][y] = 0
            if self.field[x][y] == 0:
                self.recursive_opening_of_zeros(x, y)
            return False

    def set_flag(self, x, y):
        """Sets flag into the square (x, y)."""
        if self.cover[x][y] == CoverState.COVERED:
            self.cover[x][y] = CoverState.FLAG
        elif self.cover[x][y] == CoverState.FLAG:
            self.cover[x][y] = CoverState.COVERED

    def recursive_opening_of_zeros(self, x, y):
        """Opens all zeres near current."""
        if self.field[x][y] != 0:
            return None
        self.cover[x][y] = 0
        for delta_x in range(-1, 2):
            for delta_y in range(-1, 2):
                if not (delta_x == 0 and delta_y == 0):
                    if 0 <= x + delta_x < self.field_width and \
                            0 <= y + delta_y < self.field_height and \
                            not (delta_x == 0 and delta_y == 0):
                        if (self.field[x + delta_x][y + delta_y] == 0 and
                                self.cover[x + delta_x][y + delta_y] == 1):
                            self.recursive_opening_of_zeros(x + delta_x,
                                                            y + delta_y)
                        elif (self.field[x + delta_x][y + delta_y] > 0 and
                              self.cover[x + delta_x][y + delta_y] == 1):
                            self.open_square(x + delta_x, y + delta_y)


class Drower:
    current_game = Game()

    def __init__(self):
        self.k = None

    def open_first_sqr(self, height, width):
        game_screen = curses.initscr()
        game_screen.clear()
        cursor_x = 0
        cursor_y = 0
        game_screen.refresh()
        while self.k != ord('q'):
            game_screen.refresh()
            self.k = game_screen.getch()
            if self.k == KEY_UP:
                cursor_y = cursor_y - 1
            elif self.k ==KEY_DOWN:
                cursor_y = cursor_y + 1
            elif self.k == KEY_LEFT:
                cursor_x = cursor_x + 1
            elif self.k == 68:
                cursor_x = cursor_x - 1
            elif self.k == ord(' '):
                self.current_game.build(height, width, cursor_x, cursor_y, 7)
                return self.play_game(self.current_game, cursor_x, cursor_y)
            cursor_x = max(0, cursor_x)
            cursor_x = min(width - 1, cursor_x)
            cursor_y = max(0, cursor_y)
            cursor_y = min(height - 1, cursor_y)
            game_screen.clear()
            game_screen.refresh()
            game_screen.move(cursor_y, cursor_x * 2)

    def play_game(self, curr_game, curr_x, curr_y):
        game_screen = curses.initscr()
        k = None
        cursor_x = curr_x
        cursor_y = curr_y
        game_screen.clear()
        game_screen.move(cursor_y, cursor_x * 2)
        game_screen.refresh()
        while self.k != ord('q'):
            self.k = game_screen.getch()
            game_screen.clear()
            for i in range(curr_game.field_height):
                for j in range(curr_game.field_width):
                    if curr_game.cover[i][j] == 1:
                        game_screen.addstr(j, i * 2, ' ')
                    elif curr_game.cover[i][j] == 2:
                        game_screen.addstr(j, i * 2, 'F')
                    elif curr_game.cover[i][j] == 0:
                        game_screen.addstr(j, i * 2,
                                           str(self.current_game.field[i][j]))
            game_screen.refresh()
            game_screen.move(cursor_y, cursor_x * 2)
            if self.k == 66:  # key down
                cursor_y = cursor_y + 1
            elif self.k == 65:  # key up
                cursor_y = cursor_y - 1
            elif self.k == 67:
                cursor_x = cursor_x + 1
            elif self.k == 68:
                cursor_x = cursor_x - 1
            elif self.k == ord(' '):
                if self.current_game.open_square(cursor_x, cursor_y):
                    return self.game_over(game_screen)
            elif self.k == ord('f'):
                self.current_game.set_flag(cursor_x, cursor_y)
            cursor_x = max(0, cursor_x)
            cursor_x = min(self.current_game.field_width - 1, cursor_x)
            cursor_y = max(0, cursor_y)
            cursor_y = min(self.current_game.field_height - 1, cursor_y)
            game_screen.move(cursor_y, cursor_x * 2)
            game_screen.refresh()

    def game_menu(self):
        game_screen = curses.initscr()
        game_screen.clear()
        game_screen.addstr(1, 1, "Press s to start a game")
        game_screen.addstr(3, 1, "Press q to finish")
        game_screen.refresh()
        while self.k != ord('q'):
            if self.k == ord('s'):
                return self.open_first_sqr(8, 8)
            game_screen.refresh()
            self.k = game_screen.getch()

    def game_over(self, game_screen):
        game_screen.clear()
        game_screen.addstr(1, 1, "You failed!")
        game_screen.addstr(3, 1, "Press m to get into game menu")
        game_screen.addstr(5, 1, "Press q to get into game menu")
        game_screen.refresh()
        while self.k != ord('q'):
            if self.k == ord('m'):
                return self.game_menu()
            game_screen.refresh()
            self.k = game_screen.getch()

    def you_win(self, game_screen):
        game_screen.clear()
        game_screen.addstr(1, 1, "You won!")
        game_screen.addstr(3, 1, "Press m to get into game menu")
        game_screen.addstr(5, 1, "Press q to get into game menu")
        game_screen.refresh()
        while self.k != ord('q'):
            if self.k == ord('m'):
                return self.game_menu()
            game_screen.refresh()
            self.k = game_screen.getch()


if __name__ == "__main__":
    drower1 = Drower()
    drower1.game_menu()
