import curses
from random import shuffle
from enum import Enum


# class FieldCellState(Enum):
#     MINE = -1
# Видимо не буду делать Enum для Field, тк оно можем содерхать и цифры


class CoverState(Enum):
    COVERED = 1
    OPENED = 0
    FLAG = 2


KEY_UP = 65
KEY_DOWN = 66
KEY_LEFT = 67
KEY_RIGHT = 68


FIELD_MINE = -1


class Game:

    def __init__(self):
        self.field_height = 0
        self.field_width = 0
        self.num_of_marked = 0
        self.num_of_mines = 0
        self.field = []
        self.cover = []
        self.num_of_flags = 0
        self.cursor_y = 0
        self.cursor_x = 0

    def build(self, height, width, x, y, num_of_mines):
        """Makes game ready to play."""
        self.clear_field()
        self.field_height = height
        self.field_width = width
        self.field = [[0 for j in range(self.field_width)]
                      for i in range(self.field_height)]
        self.cover = [[CoverState.COVERED for j in range(self.field_width)]
                      for i in range(self.field_height)]
        self.set_mines(x, y, num_of_mines)
        self.count_mines()
        self.num_of_marked = 0
        self.num_of_mines = num_of_mines
        self.num_of_flags = 0
        self.open_square(x, y)

    def clear_field(self):
        """Makes field free from mines"""
        for i in self.field:
            for j in i:
                j = 0

    def set_mines(self, x, y, num_of_mines):
        """Sets mines somewhere, except for (x, y)."""
        coord_pairs = list(set([(i, j) for i in range(self.field_height)
                                for j in range(self.field_width)]) - {(x, y)})
        shuffle(coord_pairs)
        to_push = coord_pairs[0:num_of_mines]
        for i in to_push:
            self.field[i[0]][i[1]] = FIELD_MINE

    def count_mines(self):
        """For each square counts number of mines next to it."""
        for i in range(0, self.field_height):
            for j in range(0, self.field_width):
                if self.field[i][j] != FIELD_MINE:
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
        if self.cover[x][y] in {CoverState.OPENED, CoverState.FLAG}:
            return False
        if self.cover[x][y] == CoverState.COVERED:
            if self.field[x][y] == -1:
                return True
            self.num_of_marked += 1
            if self.field[x][y] == 0:
                self.recursive_opening_of_zeros(x, y)
            else:
                self.cover[x][y] = CoverState.OPENED
            return False

    def set_flag(self, x, y):
        """Sets flag into the square (x, y)."""
        if self.cover[x][y] == CoverState.COVERED:
            self.cover[x][y] = CoverState.FLAG
            self.num_of_flags += 1
            self.num_of_marked += 1
        elif self.cover[x][y] == CoverState.FLAG:
            self.cover[x][y] = CoverState.COVERED
            self.num_of_flags -= 1
            self.num_of_marked -= 1

    def recursive_opening_of_zeros(self, x, y):
        """Opens all zeros near current."""
        if self.field[x][y] != 0:
            return None
        self.cover[x][y] = CoverState.OPENED
        for delta_x in range(-1, 2):
            for delta_y in range(-1, 2):
                if not (delta_x == 0 and delta_y == 0):
                    if 0 <= x + delta_x < self.field_width and \
                            0 <= y + delta_y < self.field_height and \
                            not (delta_x == 0 and delta_y == 0):
                        if (self.field[x + delta_x][y + delta_y] == 0 and
                                self.cover[x + delta_x][y + delta_y]
                                == CoverState.COVERED):
                            self.num_of_marked += 1
                            self.recursive_opening_of_zeros(x + delta_x,
                                                            y + delta_y)
                        elif (self.field[x + delta_x][y + delta_y] > 0 and
                                self.cover[x + delta_x][y + delta_y]
                                == CoverState.COVERED):
                            self.open_square(x + delta_x, y + delta_y)

    def check(self):
        if self.num_of_marked < self.field_height * self.field_width or \
                self.num_of_mines != self.num_of_flags:
            return 0
        return 1


class Drawer:

    def __init__(self):
        self.game_screen = curses.initscr()
        self.current_game = Game()
        self.k = None
        self.cursor_x = 0
        self.cursor_y = 0

    def open_first_sqr(self, height, width):
        self.set_to_default()
        self.current_game.field_width = width
        self.current_game.field_height = height
        while self.k != ord('q'):
            self.k = self.game_screen.getch()
            self.change_cursor_position()
            if self.k == ord(' '):
                self.current_game.build(height, width, self.cursor_x,\
                                        self.cursor_y, 7)
                return self.play_game()
            self.game_screen.clear()
            self.game_screen.move(self.cursor_y, self.cursor_x * 2)
            self.game_screen.refresh()

    def play_game(self):
        self.k = None
        self.game_screen.clear()
        self.game_screen.move(self.cursor_y, self.cursor_x * 2)
        self.game_screen.refresh()
        while self.k != ord('q'):
            self.k = self.game_screen.getch()
            self.game_screen.clear()
            for i in range(self.current_game.field_height):
                for j in range(self.current_game.field_width):
                    if self.current_game.cover[i][j] == CoverState.COVERED:
                        self.game_screen.addstr(j, i * 2, ' ')
                    elif self.current_game.cover[i][j] == CoverState.FLAG:
                        self.game_screen.addstr(j, i * 2, 'F')
                    elif self.current_game.cover[i][j] == CoverState.OPENED:
                        self.game_screen.addstr(j, i * 2,
                                           str(self.current_game.field[i][j]))
            self.game_screen.refresh()
            self.game_screen.move(self.cursor_y, self.cursor_x * 2)
            self.change_cursor_position()
            if self.k == ord(' '):
                if self.current_game.open_square(self.cursor_x, self.cursor_y):
                    return self.game_over()
            elif self.k == ord('f'):
                self.current_game.set_flag(self.cursor_x, self.cursor_y)
            # debug
            # self.game_screen.addstr(2, 18, str(self.current_game.num_of_marked))
            # self.game_screen.addstr(3, 18, str(self.current_game.num_of_flags))
            # self.game_screen.addstr(4, 18, str(self.current_game.num_of_mines))
            # end of debugging output
            self.game_screen.move(self.cursor_y, self.cursor_x * 2)
            self.game_screen.refresh()
            if self.current_game.check():
                return self.you_win()

    def game_menu(self):
        self.game_screen.clear()
        self.game_screen.addstr(1, 1, "Press s to start a game")
        self.game_screen.addstr(3, 1, "Press q to finish")
        self.game_screen.refresh()
        while self.k != ord('q'):
            if self.k == ord('s'):
                return self.open_first_sqr(8, 8)
            self.game_screen.refresh()
            self.k = self.game_screen.getch()

    def game_over(self):
        self.game_screen.clear()
        self.game_screen.addstr(1, 1, "You failed!")
        self.game_screen.addstr(3, 1, "Press m to get into game menu")
        self.game_screen.addstr(5, 1, "Press q to get into game menu")
        self.game_screen.refresh()
        while self.k != ord('q'):
            if self.k == ord('m'):
                return self.game_menu()
            self.game_screen.refresh()
            self.k = self.game_screen.getch()

    def you_win(self):
        self.game_screen.clear()
        self.game_screen.addstr(1, 1, "You won!")
        self.game_screen.addstr(3, 1, "Press m to get into game menu")
        self.game_screen.addstr(5, 1, "Press q to get into game menu")
        self. game_screen.refresh()
        while self.k != ord('q'):
            if self.k == ord('m'):
                return self.game_menu()
            self.game_screen.refresh()
            self.k = self.game_screen.getch()

    def check_cursor_position(self):
        self.cursor_x = max(0, self.cursor_x)
        self.cursor_x = min(self.current_game.field_width - 1, self.cursor_x)
        self.cursor_y = max(0, self.cursor_y)
        self.cursor_y = min(self.current_game.field_height - 1, self.cursor_y)

    def change_cursor_position(self):
        if self.k == KEY_UP:
            self.cursor_y = self.cursor_y - 1
        elif self.k == KEY_DOWN:
            self.cursor_y = self.cursor_y + 1
        elif self.k == KEY_RIGHT:
            self.cursor_x = self.cursor_x - 1
        elif self.k == KEY_LEFT:
            self.cursor_x = self.cursor_x + 1
        self.check_cursor_position()

    def set_to_default(self):
        self.game_screen.clear()
        self.k = None
        self.cursor_x = 0
        self.cursor_y = 0
        self.game_screen.refresh()


if __name__ == "__main__":
    drawer1 = Drawer()
    drawer1.game_menu()
