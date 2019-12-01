import time
import argparse
from copy import deepcopy

all_dir         = {0, 1, 2, 3, 4, 5, 6}
left_dir        = {2, 3, 5}
right_dir       = {1, 4, 5}
up_dir          = {3, 4, 6}
down_dir        = {1, 2, 6}
straight_dir    = {5, 6}
bend_dir        = {1, 2, 3, 4}
horizontal_dir  = {5}
vertical_dir    = {6}

parser = argparse.ArgumentParser()
parser.add_argument("--image", "-i", help="set image path, can be in txt (0 for black, 1 for white, - for empty) or jpg/jpeg/png")
args = parser.parse_args()


class Board:
    def __init__(self, filename=""):
        self.grid = []
        if filename:
            # input from file
            with open(filename, "r") as f:
                for line in f:
                    self.grid.append(line.strip())
        else:
            # input from stdin
            tmp = input()
            while tmp != '$':
                self.grid.append(tmp)
                tmp = input()
        self.r = len(self.grid)
        self.c = len(self.grid[0])
        self.init_pearl()
        self.init_solution()

    def init_pearl(self):
        # pearl = (bool {0-black, 1-white}, r, c)
        self.pearl = set()
        for r in range(self.r):
            for c in range(self.c):
                if self.grid[r][c] in ['0', '1']:
                    self.pearl.add((int(self.grid[r][c]), r, c))

    def init_solution(self):
        """
        solution = list of possible line shape on that cell:
        0 : empty
        1 : up-right
        2 : right-down
        3 : down-left
        4 : left-up
        5 : horizontal
        6 : vertical
        """
        self.solution = [[all_dir.copy() for x in range(self.c)] for y in range(self.r)]
        # remove invalid edge shape
        for c in range(self.c):
            self.solution[0][c]  -= up_dir     # top row
            self.solution[-1][c] -= down_dir   # down row

        for r in range(self.r):
            self.solution[r][0]  -= left_dir   # leftmost col
            self.solution[r][-1] -= right_dir  # rightmost col

        print("Board init complete!")
        self.print_solution()

        for pearl in self.pearl:
            # remove straight line from black
            if pearl[0] == 0:
                # pearl location: (pearl[1], pearl[2])
                self.solution[pearl[1]][pearl[2]] &= bend_dir
                # remove black near edge
                if pearl[1] + 2 > self.r - 1:
                    self.solution[pearl[1]][pearl[2]] &= up_dir
                if pearl[1] - 2 < 0:
                    self.solution[pearl[1]][pearl[2]] &= down_dir
                if pearl[2] + 2 > self.c - 1:
                    self.solution[pearl[1]][pearl[2]] &= left_dir
                if pearl[2] - 2 < 0:
                    self.solution[pearl[1]][pearl[2]] &= right_dir

            # remove bend line from white
            elif pearl[0] == 1:
                # pearl location: (pearl[1], pearl[2])
                self.solution[pearl[1]][pearl[2]] &= straight_dir

        print("Pearl loaded!")
        self.print_solution()

        tmp = []
        while tmp != self.solution:
            tmp = deepcopy(self.solution)
            for pearl in self.pearl:
                if pearl[0] == 0:
                    self.apply_black_rule(pearl[1], pearl[2])
                elif pearl[0] == 1:
                    self.apply_white_rule(pearl[1], pearl[2])

            for r in range(self.r):
                for c in range(self.c):
                    if len(self.solution[r][c]) == 1:
                        self.filter_adj(r, c)
        print("Line extended!")
        self.print_solution()

    def apply_black_rule(self, r, c):
        # remove invalid black reach (within 2 block)
        if len(self.solution[r][c]) > 1:
            # up, right, down, left
            if r != 0:
                if (not vertical_dir & self.solution[r - 1][c]):
                    self.solution[r][c] -= up_dir
                elif r != 1:
                    if (not down_dir & self.solution[r - 2][c]):
                        self.solution[r][c] -= up_dir

            if r != self.r - 1:
                if (not vertical_dir & self.solution[r + 1][c]):
                    self.solution[r][c] -= down_dir
                elif r != self.r - 2:
                    if (not up_dir & self.solution[r + 2][c]):
                        self.solution[r][c] -= down_dir

            if c != 0:
                if (not horizontal_dir & self.solution[r][c - 1]):
                    self.solution[r][c] -= left_dir
                elif c != 1:
                    if (not right_dir & self.solution[r][c - 2]):
                        self.solution[r][c] -= left_dir

            if c != self.c - 1:
                if (not horizontal_dir & self.solution[r][c + 1]):
                    self.solution[r][c] -= right_dir
                elif c != self.c - 2:
                    if (not left_dir & self.solution[r][c + 2]):
                        self.solution[r][c] -= right_dir

        # must go down
        if self.solution[r][c].issubset(down_dir):
            self.solution[r + 1][c] &= vertical_dir
            self.solution[r + 2][c] &= up_dir
            if r != 0:
                self.solution[r - 1][c] -= down_dir
            # |--
            # |.  (.) cant go left
            if {1}.issubset(self.solution[r][c]):
                self.solution[r + 1][c + 1] -= left_dir
            # --|
            #  .| (.) cant go right
            if {2}.issubset(self.solution[r][c]):
                self.solution[r + 1][c - 1] -= right_dir

        # must go left
        if self.solution[r][c].issubset(left_dir):
            self.solution[r][c - 1] &= horizontal_dir
            self.solution[r][c - 2] &= right_dir
            if c != self.c - 1:
                self.solution[r][c + 1] -= left_dir
            # --|
            #  .| (.) cant go up
            if {2}.issubset(self.solution[r][c]):
                self.solution[r + 1][c - 1] -= up_dir
            #  .|
            # --| (.) cant go down
            if {3}.issubset(self.solution[r][c]):
                self.solution[r - 1][c - 1] -= down_dir

        # must go up
        if self.solution[r][c].issubset(up_dir):
            self.solution[r - 1][c] &= vertical_dir
            self.solution[r - 2][c] &= down_dir
            if r != self.r - 1:
                self.solution[r + 1][c] -= up_dir
            #  .|
            # --| (.) cant go right
            if {3}.issubset(self.solution[r][c]):
                self.solution[r - 1][c - 1] -= right_dir
            # |.
            # |-- (.) cant go left
            if {4}.issubset(self.solution[r][c]):
                self.solution[r - 1][c + 1] -= left_dir

        # must go right
        if self.solution[r][c].issubset(right_dir):
            self.solution[r][c + 1] &= horizontal_dir
            self.solution[r][c + 2] &= left_dir
            if r != 0:
                self.solution[r][c - 1] -= right_dir
            # |--
            # |.  (.) cant go up
            if {1}.issubset(self.solution[r][c]):
                self.solution[r + 1][c + 1] -= up_dir
            # |.
            # |-- (.) cant go down
            if {1}.issubset(self.solution[r][c]):
                self.solution[r - 1][c + 1] -= down_dir

    def apply_white_rule(self, r, c):
        # no bend on adj vertical, must be horizontal
        if len(self.solution[r][c]) > 1:
            adj_verts = set()
            if r != 0:
                adj_verts |= self.solution[r - 1][c]
            if r != self.r - 1:
                adj_verts |= self.solution[r + 1][c]

            if not adj_verts & bend_dir:
                self.solution[r][c] = horizontal_dir

            # no bend on adj horizontal, must be vertical
            adj_hors = set()
            if c != 0:
                adj_hors |= self.solution[r][c - 1]
            if c != self.c - 1:
                adj_hors |= self.solution[r][c + 1]

            if not adj_hors & bend_dir:
                self.solution[r][c] = vertical_dir

        # horizontal
        if self.solution[r][c] == horizontal_dir:
            self.solution[r][c - 1] &= right_dir
            self.solution[r][c + 1] &= left_dir
            if r != 0:
                self.solution[r - 1][c] -= down_dir
            if r != self.r - 1:
                self.solution[r + 1][c] -= up_dir

            # no bend on left, right must bend
            if not self.solution[r][c - 1] & bend_dir:
                self.solution[r][c + 1] &= bend_dir
            # no bend on right, left must bend
            if not self.solution[r][c + 1] & bend_dir:
                self.solution[r][c - 1] &= bend_dir

        # vertical
        if self.solution[r][c] == vertical_dir:
            self.solution[r - 1][c] &= down_dir
            self.solution[r + 1][c] &= up_dir
            if c != 0:
                self.solution[r][c - 1] -= right_dir
            if c != self.c - 1:
                self.solution[r][c + 1] -= left_dir

            # no bend on down, up must bend
            if not self.solution[r - 1][c] & bend_dir:
                self.solution[r + 1][c] &= bend_dir
            # no bend on up, down must bend
            if not self.solution[r + 1][c] & bend_dir:
                self.solution[r - 1][c] &= bend_dir

    def filter_adj(self, r, c):
        # if current cell is empty
        if self.solution[r][c] == {0}:
            # no adj cell go to current cell
            if r != 0:
                self.solution[r - 1][c] -= down_dir
            if c != 0:
                self.solution[r][c - 1] -= right_dir
            if r != self.r - 1:
                self.solution[r + 1][c] -= up_dir
            if c != self.c - 1:
                self.solution[r][c + 1] -= left_dir

        # if current cell is shape 1
        elif self.solution[r][c] == {1}:
            # restrict left and up
            if r != 0:
                self.solution[r - 1][c] -= down_dir
            if c != 0:
                self.solution[r][c - 1] -= right_dir

            # must go down and right
            self.solution[r + 1][c] &= up_dir
            self.solution[r][c + 1] &= left_dir

        # if current cell is shape 2
        elif self.solution[r][c] == {2}:
            # restrict right and up
            if r != 0:
                self.solution[r - 1][c] -= down_dir
            if c != self.c - 1:
                self.solution[r][c + 1] -= left_dir

            # must go down and left
            self.solution[r + 1][c] &= up_dir
            self.solution[r][c - 1] &= right_dir

        # if current cell is shape 3
        elif self.solution[r][c] == {3}:
            # restrict down and right
            if r != self.r - 1:
                self.solution[r + 1][c] -= up_dir
            if c != self.c - 1:
                self.solution[r][c + 1] -= left_dir

            # must go up and left
            self.solution[r - 1][c] &= down_dir
            self.solution[r][c - 1] &= right_dir

        # if current cell is shape 4
        elif self.solution[r][c] == {4}:
            # restrict left and down
            if r != self.r - 1:
                self.solution[r + 1][c] -= up_dir
            if c != 0:
                self.solution[r][c - 1] -= right_dir

            # must go up and right
            self.solution[r - 1][c] &= down_dir
            self.solution[r][c + 1] &= left_dir

        # if current cell is shape 5
        elif self.solution[r][c] == {5}:
            # restrict up and down
            if r != 0:
                self.solution[r - 1][c] -= down_dir
            if r != self.r - 1:
                self.solution[r + 1][c] -= up_dir

            # must go left and right
            self.solution[r][c - 1] &= right_dir
            self.solution[r][c + 1] &= left_dir

        # if current cell is shape 6
        elif self.solution[r][c] == {6}:
            # restrict left and right
            if c != 0:
                self.solution[r][c - 1] -= right_dir
            if c != self.c - 1:
                self.solution[r][c + 1] -= left_dir

            # must go up and down
            self.solution[r - 1][c] &= down_dir
            self.solution[r + 1][c] &= up_dir

    def solve(self):
        pass

    def solvable(self):
        for r in range(self.r):
            for c in range(self.c):
                if not self.solution[r][c]:
                    return False
        return True

    def is_solved(self):
        for r in range(self.r):
            for c in range(self.c):
                if len(self.solution[r][c]) != 1:
                    return False
        return True

    def print_solution(self):
        for r in range(self.r):
            for c in range(self.c):
                print("".join(map(str, self.solution[r][c])), end=" " * (7 - len(self.solution[r][c])))
                print("|", end="")
            print()
        print()

    def print_board(self):
        for line in self.grid:
            print(line)


if __name__ == "__main__":
    if args.image:
        filename = args.image
    else:
        filename = input("Type input file name: ")
    t0 = time.time()
    B = Board(filename)
    if B.solvable():
        B.solve()
        if B.is_solved():
            print("Here is the solution:")
            B.print_board()
            B.print_solution()
        else:
            print("Sorry currently I can't solve this board :(")
    else:
        print("Puzzle is unsolvable!")

    t1 = time.time()
    print("Finished! Time taken:", t1 - t0, "seconds")
