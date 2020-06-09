import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        #raise NotImplementedError
        l1 = []
        for var,words in self.domains.items():
            for w in words.copy():
                if var.length != len(w):
                    self.domains[var].remove(w)
                

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        #raise NotImplementedError
        revise = False
        if self.crossword.overlaps[x,y] is not None:
            i,j = self.crossword.overlaps[x,y]
            for ele1 in self.domains[x].copy():
                state = False
                for ele2 in self.domains[y]:
                    if ele1[i] == ele2[j]:
                        state = True
                        break
                if not state:
                    self.domains[x].remove(ele1)
                    revise = True
        return revise

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        #raise NotImplementedError
        l =  []
        if arcs is not None:
            l = arcs
        else:
            for x,y in self.crossword.overlaps:
                if self.crossword.overlaps[x,y] is not None:
                    l.append((x,y))

        while len(l) != 0:
            x,y = l[0]
            l = l[1:]
            if self.revise(x,y):
                if len(self.domains[x]) == 0:
                    return False
                for v2 in self.crossword.neighbors(x):
                    if v2 != x:
                        l.append((v2,x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        #raise NotImplementedError
        for var in self.domains:
            if var in assignment:
                continue
            return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        #raise NotImplementedError
        for v1 in assignment:
            if v1.length != len(assignment[v1]):
                return False
            for v2 in self.crossword.neighbors(v1):
                if (v2 != v1) & (v2 in assignment):
                    i,j = self.crossword.overlaps[v1,v2]
                    if assignment[v1][i] != assignment[v2][j]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        #raise NotImplementedError
        #return self.domains[var]
        neigh = self.crossword.neighbors(var)
        for v in neigh.copy():
            if v in assignment:
                neigh.remove(v)
        l = []
        for word in self.domains[var]:
            cnt = 0
            for v in neigh:
                i,j = self.crossword.overlaps[var,v]
                for word2 in self.domains[v]:
                    if word[i] != word2[j]:
                        cnt += 1
            l.append((cnt,word))
        l.sort()
        l1 = [x[1] for x in l]
        return l1

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        #raise NotImplementedError
        l = []
        l2 = []
        for v1 in self.domains:
            if v1 not in assignment:
                l.append((len(self.domains[v1]),v1))
                l2.append(v1)
        #return l2[0]

        l1 = []
        l.sort(key = lambda x:x[0])
        if len(l) == 0:
            return None
        val = l[0][0]
        for i in l:
            if i[0] == val:
                n = self.crossword.neighbors(i[1])
                l1.append((n,i[1]))
        l1.sort(reverse=True)
        return l1[0][1]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        #raise NotImplementedError
        if self.consistent(assignment) & self.assignment_complete(assignment):
            return assignment
        if not(self.consistent(assignment)):
            return None
        var = self.select_unassigned_variable(assignment)
        for word in self.order_domain_values(var,assignment):
            assignment[var]=word
            result = self.backtrack(assignment)
            if result != None:
                return result
            assignment.pop(var)
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()