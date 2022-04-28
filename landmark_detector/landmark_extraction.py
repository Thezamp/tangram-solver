import numpy as np
import cv2 as cv
import pandas as pd
from matplotlib import pyplot as plt
from scipy import ndimage
# import pylab as pl
from matplotlib import collections as mc
import time

# limits of the grid defined by hand
solution_limits = {1: [(-260, 120), (-120, 140)], 2: [(-280, -20), (-80, 200)], 3: [(-320, 60), (-140, 140)],
                   4: [(-280, 0), (-200, 300)]}


def get_grid_value(rm, cm, tgn):
    '''
    Converts x and y matrix coordinates into grid values for tangram puzzle = tgn

    outputs the grid number 0-15, or -1 in case the placement is generically outside the grid
    '''
    # attention: coordinates for triangles are currently from the middle point of the bbox
    y = -rm + 300
    x = cm - 400

    xrange = solution_limits.get(tgn)[0]
    yrange = solution_limits.get(tgn)[1]
    xstep = (xrange[1] - xrange[0]) / 4
    ystep = (yrange[1] - yrange[0]) / 4
    if (x not in range(xrange[0], xrange[1] + 1) or y not in range(yrange[0], yrange[1] + 1)):
        return -1
    xgrid = (x - xrange[0]) // xstep

    ygrid = (y - yrange[0]) // ystep

    return ygrid * 4 + xgrid


def generate_rotation_templates(original, rotations):
    '''generates rotation +1 orientations'''
    nonzero = original.nonzero()
    templates = [original[min(nonzero[0]) - 2:max(nonzero[0]) + 2, min(nonzero[1]) - 2:max(nonzero[1]) + 2]]
    for r in range(-45, -45 * rotations, -45):
        rotated = ndimage.rotate(original, r)
        nonzero = rotated.nonzero()
        rotated = rotated[min(nonzero[0]) - 2:max(nonzero[0]) + 2, min(nonzero[1]) - 2:max(nonzero[1]) + 2]
        templates.append(rotated)

    return templates


def find_placements(piece, state_img, edged_image):
    available_placements = []
    for ti in range(len(piece.templates)):
        current = piece.templates[ti]
        edges = cv.Canny(current * 255, 100, 200)
        h, w = current.shape[:2]
        method = cv.TM_SQDIFF

        res = cv.matchTemplate(edged_image, edges, method, mask=current)

        i = 0
        attempt = 0
        while i < 4 and attempt < 5:
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

            xt = min_loc[1] - h // 2 if min_loc[1] > 20 else 0
            xb = min_loc[1] + h // 2 + 1
            yl = min_loc[0] - w // 2 if min_loc[0] > 20 else 0
            yr = min_loc[0] + w // 2 + 1

            res[xt:xb, yl:yr] = float('inf')
            central_coord = (min_loc[1] + h // 2, min_loc[0] + w // 2)
            if (state_img[central_coord] == 1):
                # print((min_loc[1]+h//2,min_loc[0]+w//2))

                available_placements.append((central_coord, ti * 45))
                i += 1

            attempt += 1

    return available_placements


class Template:
    def __init__(self, name, path, rotations):
        self.name = name
        original_rotation = cv.imread(path, 0)
        t2, original_rotation = cv.threshold(original_rotation, 100, 1, cv.THRESH_BINARY)

        self.templates = generate_rotation_templates(original_rotation, rotations)


class LandmarkExtractor:
    def __init__(self, tgn=4):
        self.pieces = {'small_t': Template('small triangle', './tans/smallt.png', 7),
                       'big_t': Template('big triangle', './tans/bigt.png', 7),
                       'middle_t': Template('middle triangle', './tans/middlet.png', 7),
                       'square': Template('square', './tans/square.png', 2),
                       'parallelogram': Template('parall', './tans/parall1.png', 3),
                       'parallelogram_m': Template('parall', './tans/parall2.png', 7)
                       }
        self.tgn = tgn
        counts = pd.read_csv('./../datasets/landmark_counts.csv')
        self.counts = counts.loc[counts['tangram nr'] == tgn]
        steps = pd.read_csv('./../datasets/steps.csv')
        self.steps = steps.loc[steps['tangram nr'] == tgn]

    def extract(self, image_path):
        # binary image
        state = cv.imread(image_path, 0)
        state = state[31:-1, 1:-1]
        state[500:, :] = 0
        _, state = cv.threshold(state, 240, 1, cv.THRESH_BINARY)

        # edges
        edged_image = cv.Canny(state * 255, 100, 200)

        extracted_landmarks = []
        for piece in self.pieces.values():
            available_placements = find_placements(piece, state, edged_image)
            # list of ((x,y),rot)
            for p in available_placements:
                rot = p[1]
                grid = get_grid_value(p[0][0], p[0][1], self.tgn)
                if grid != -1:
                    row = self.counts.loc[(self.counts['grid_val'] == grid) & \
                                          (self.counts['rot'] == rot) & \
                                          (self.counts.item == piece.name)]
                    if not row.empty:
                        ldm_count = row['counts'].values
                        extracted_landmarks.append((piece.name, grid, rot, ldm_count[0]))
        return extracted_landmarks


def main():
    l = LandmarkExtractor(4)
    start = time.time()
    l.extract('./example_pictures/1.png')
    print(time.time() - start)

    # time.sleep(10)
    return 0


if __name__ == '__main__':
    main()
