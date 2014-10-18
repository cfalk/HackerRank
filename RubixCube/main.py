
def getImageGrid(filename):
  from PIL import Image
  image = Image.open(filename)
  pixels = image.load()
  width, height = image.size
  rgb_grid = [[pixels[i, j] for i in xrange(width)] for j in xrange(height)]
  return rgb_grid

def avgPixel(pixels):
  r = 0
  g = 0
  b = 0
  num_pixels = float(len(pixels))
  for pix in pixels:
    r += pix[0]
    g += pix[1]
    b += pix[2]
  return (r/num_pixels, g/num_pixels, b/num_pixels)


def removeBackground(grid):
  def findBackground(grid):
    width = len(grid[0])
    height = len(grid)
    threshold = 0.25
    opp_thresh = 1-threshold
    backgrounds = []
    for row in grid[:int(height*threshold)]+grid[int(height*opp_thresh):]:
      background = avgPixel(row[:int(width*threshold)]+row[int(width*opp_thresh):])
      backgrounds.append(background)

    return avgPixel(backgrounds)

  def preparePix(pix, background):
    if colorDifference(pix, background)<150:
      return (0,0,0)
    else:
      return pix

  background = findBackground(grid)
  return [[preparePix(pix, background) for pix in row] for row in grid]


def colorDifference(pix1, pix2):
  total = 0
  for i in xrange(3):
    total += (pix1[i]-pix2[i])**2
  return (total**0.5)


def makeUniformColors(grid):
  def closestCol(pix, available_pix):
    threshold = 40
    shortest = float("inf")
    color = pix # If no "close" color, make this a new color.
    for other_pix in available_pix:
      col_dist = colorDifference(pix, other_pix)
      if col_dist < shortest and col_dist < threshold:
        shortest = col_dist
        color = other_pix
    return color

  col_set = set()
  uniform_grid = []
  for row in grid:
    uniform_grid.append([])
    for pix in row:
      representative = closestCol(pix, col_set)
      col_set.add(representative)
      uniform_grid[-1].append( representative )

  return uniform_grid, col_set


def makeColorGraph(grid, colors):
  def getColorCounts(grid, colors):
    num_cols = len(grid[0])
    counts = []
    for i in xrange(num_cols):
      counts.append({color:0 for color in colors})
      for row in grid:
        color = row[i]
        counts[-1][color] += 1
    return counts[::-1]

  def getColorArrays(col_dicts):
    arrays = []
    colors = col_dicts[0].keys()
    return [[col_dict[color] for col_dict in col_dicts] for color in colors]


    return arrays

  def normalize(colors):
    max = 256.0
    return [(p[0]/max, p[1]/max, p[2]/max) for p in colors]

  import pylab
  pylab.figure()
  col_counts = getColorCounts(grid, colors)

  colors = col_counts[0].keys()
  label_cols = normalize(colors)
  labels = map(str,colors)
  col_arrays = getColorArrays(col_counts)

  background = colors.index((0,0,0))
  col_arrays.pop(background)
  colors.pop(background)

  for i, array in enumerate(col_arrays):
    pylab.bar(range(len(array)),array, width=1, color=label_cols[i], label=labels[i])

  pylab.show()


def writeImage(rgb_grid):
  def getColorBand(i):
    from numpy import uint8
    band = [[(elem[i]) for elem in row] for row in rgb_grid]
    return uint8(band)

  from PIL import Image
  from numpy import array
  r = Image.fromarray(getColorBand(0), "L")
  g = Image.fromarray(getColorBand(1), "L")
  b = Image.fromarray(getColorBand(2), "L")
  image = Image.merge("RGB", (r,g,b))
  image.save("newImage.jpg")


def getPixelRange(i, j, grid, radius, noBlack=True):
  def L2(p1,p2):
    return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**0.5

  if noBlack and isBlack(grid[j][i]): yield (i,j)

  startI = i-radius if (i-radius)>0 else 0
  endI = i+radius if (i+radius)<len(grid[0]) else len(grid[0])
  startJ = j-radius if (j-radius)>0 else 0
  endJ = j+radius if (j+radius)<len(grid) else len(grid)

  for y in xrange(startJ, endJ):
    for x in xrange(startI, endI):
      if not isBlack(grid[y][x]) and L2((x,y),(i,j))<radius:
        yield (x,y)

  #yield (i, j)


def blurColors(grid, iterations=1):
  width = len(grid[0])
  height = len(grid)
  radius = 5
  for i in xrange(iterations):
    new_grid = []
    for j in xrange(height):
      new_grid.append([])
      for i in xrange(width):
        pix = avgPixel([grid[y][x] for x,y in getPixelRange(i,j,grid, radius)])
        new_grid[-1].append(pix)
    grid = new_grid

  return grid


def isBlack(pix):
  black = (30,30,30)
  threshold = 100
  return colorDifference(pix, black)<threshold


def amplifyBlack(grid):
  height = len(grid)
  width = len(grid[0])
  black = (0,0,0)
  radius = 4
  new_grid = [[None for j in xrange(width)] for i in xrange(height)]

  for i in xrange(height):
    for j in xrange(width):
      pix = grid[i][j]
      if new_grid[i][j]==None:
        if isBlack(pix):
          new_grid[i][j] = black
          for (x,y) in getPixelRange(j, i, grid, radius, noBlack=False):
            new_grid[y][x] = black
        else:
          new_grid[i][j] = pix

  return new_grid



def main():
  rgb_grid = getImageGrid("cube4solved.jpg")

  rgb_grid = removeBackground(rgb_grid)
  rgb_grid = amplifyBlack(rgb_grid)

  rgb_grid = blurColors(rgb_grid)
  rgb_grid, colors = makeUniformColors(rgb_grid)

  makeColorGraph(rgb_grid, colors)

  writeImage(rgb_grid)


if __name__=="__main__":
  main()

