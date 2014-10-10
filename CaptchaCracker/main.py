# Enter your code here. Read input from STDIN. Print output to STDOUT

def createBnbModel():
    def loadTrainingTuples():
        tuples = []
        if not tuples:
            with open("fingerprint_tuples.txt","r") as f:
              import json
              content = f.read().replace("\n","")[:-2]+"]"
              tuples = json.loads(content)
        return tuples
    def loadBoolString(string):
        return map(int, list(string))
    from sklearn.naive_bayes import BernoulliNB

    bnb = BernoulliNB()
    tuples = loadTrainingTuples()
    X = [loadBoolString(string) for char, string in tuples]
    y = [char for char, string in tuples]
    bnb.fit(X, y)

    return bnb


def readRgbGrid(filename=None):
    if filename:
      with open(filename, "r") as f:
        content = f.readlines()
    else:
      import sys
      content = sys.stdin.readlines()

    raw_grid = [line.split(" ") for line in content[1:]]
    grid = [[map(float, point.split(",")) for point in row] for row in raw_grid]
    return grid


def makePointGrid(rgbGrid):
    def isDarkEnough(rgb):
        return (rgb[0]+rgb[1]+rgb[2]) < 100
    return [[isDarkEnough(point) for point in row] for row in rgbGrid]


def splitByEmptyCols(grid):
    def colEmpty(grid, col):
        import operator
        return all(map(operator.not_, [row[col] for row in grid]))
    def gridSection(grid, start, end):
        return [row[start:end] for row in grid]
    def purgeEmptyRows(grid):
        return [row for row in grid if any(row)]
    def removeEmptySides(grid):
        while colEmpty(grid, 0):
            grid = [row[1:] for row in grid]
        while colEmpty(grid, len(grid[0])-1):
            grid = [row[:-1] for row in grid]
        return grid

    grid = removeEmptySides(grid)

    partitions = []
    last_end = 0
    for i in xrange(len(grid[0])):
        if colEmpty(grid, i):
            if last_end!=i:
              sub_grid = gridSection(grid, last_end, i)
              if sub_grid:
                partitions.append( purgeEmptyRows(sub_grid) )
            last_end = i + 1

    if last_end!=len(grid[0]):
      sub_grid = gridSection(grid, last_end, len(grid[0]))
      if sub_grid:
        partitions.append( purgeEmptyRows(sub_grid) )

    return partitions


def flatten(grid):
    if len(grid)==0:
        return []
    if type(grid[0])==list:
        return grid[0] + flatten(grid[1:])
    else:
        return [grid[0]] + (flatten(grid[1:]))


def getBoolStrings(grid):
    flattened = flatten(grid)
    return "".join(["1" if entry else "0" for entry in flattened])


def predict_string(tests, model):
    return "".join([model.predict(map(int, test))[0] for test in tests])


def alignOutput(tests, filename):
  with open(filename,"r") as f:
    string = f.read().replace("\n","")
    return zip(string, tests)


def writeDictAsTuples(char_dict, filename):
  with open(filename, "w") as f:
    f.write("[\n")
    for char, string in char_dict.items():
      f.write("[\"{}\", \"{}\"],\n".format(char, string))
    f.write("]")

def normalizeGrids(grids):
  size = max([max([len(row) for row in grid]) for grid in grids])
  return [[[False]*(size-len(row))+row for row in grid] for grid in grids]


def main():
  mode="test"

  if mode=="write":
    char_dict = {}
    for i in xrange(0,25):
      zero = "0" if i<10 else ""
      rgb_grid = readRgbGrid("input/input{}{}.txt".format(zero, i))
      point_grid = makePointGrid(rgb_grid)
      letter_grids = splitByEmptyCols(point_grid)
      normalized_grids = normalizeGrids(letter_grids)
      test_strings = [getBoolStrings(grid) for grid in normalized_grids]
      id_tuple = alignOutput(test_strings,"output/output{}{}.txt".format(zero, i))
      for (char, string) in id_tuple:
        if char in char_dict and char_dict[char]!=string:
          print "RUH ROH -- MISMATCH"
          print char
          print char_dict[char]
          print string
          print "".join(["^" if c1!=c2 else " " for c1, c2 in zip(char_dict[char], string)])
        else:
          char_dict[char] = string

      writeDictAsTuples(char_dict, "fingerprint_tuples.txt")
      print "Write complete!"
  else:
    rgb_grid = readRgbGrid()
    point_grid = makePointGrid(rgb_grid)
    letter_grids = splitByEmptyCols(point_grid)
    normalized_grids = normalizeGrids(letter_grids)
    test_lists = [flatten(grid) for grid in normalized_grids]
    model = createBnbModel()
    string = predict_string(test_lists, model)
    print string

main()

