from random import shuffle 

coord_pairs = [(i, j) for i in range(8) for j in range(8)]
to_erase = coord_pairs
shuffle(to_erase)
print(to_erase[0:10])
  
class game:
  def __init__(self):
    self.field_height = 0
    self.field_width = 0
    self.field = []
    self.cover = []
    
  def build(self, height, width, x, y):
    game.field_height = height
    game.field_width = width
    game.field = [[0 for j in range(game.field_width)]
                  for i in range(self.field_height)]
    game.cover = [[1 for j in range(game.field_width)]
                  for i in range(self.field_height)]
    self.set_field_to_zeros()
    self.set_mines(x, y)
    self.count_mines(x, y)
  
  def set_field_to_zeros(self):
    """Makes field free from mines"""
    for i in self.field:
      for j in i:
        j = 0;
        
  def set_mines(self, x, y):
    """Sets mines somewhere, except for (x, y)."""
    coord_pairs = list(set([(i, j) for i in range(8) for j in range(8)]) - {(x, y)})
    shuffle(coord_pairs)
    to_push = coord_pairs[0:10]
    for i in to_push:
      field[to_push[0]][to_push[1]] = -1;
      
  def count_mines(self):
    """For each square counts number of mines next to it."""
    for i in range(1, field_height - 1):
      for j in range(1, field_width - 1):
        if field[i][j] == -1:
          for delta_i in [-1, 1]:
            for delta_j in [-1, 1]:
              if (field[i + delta_i][j + delta_j] != -1):
                field[i + delta_i][j + delta_j] = field[i + delta_i][j + delta_j] + 1
  
  def open_square(x, y):
    if cover[x][y] in {0, 2}: 
      return False
    else:
      if cover[x][y] == 1:
        if field[x][y] == -1:
          return True
        else:
          return False

test_game = game()
test_game.build(8, 8, 1, 1)
