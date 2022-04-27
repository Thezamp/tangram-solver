import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from scipy import ndimage
# import pylab as pl
from matplotlib import collections as mc
import time


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


def load_logs():
    return 0


class Template:
    def __init__(self, name, path, rotations):
        self.name = name
        original_rotation = cv.imread(path, 0)
        t2, original_rotation = cv.threshold(original_rotation, 100, 1, cv.THRESH_BINARY)

        self.templates = generate_rotation_templates(original_rotation, rotations)


class Landmark_extractor:
    def __init__(self):
        self.pieces = {'small_t': Template('small_t', '', 7),
                       'big_t': Template('big_t', '', 7),
                       'middle_t': Template('middle_t', '', 7),
                       'square': Template('square', '', 2),
                       'parallelogram': Template('parall', '', 3),
                       'parallelogram_m': Template('parall', '', 7)
                       }
        self.logs = load_logs()

    def extract(self, image_path):
        state = cv.imread(image_path, 0)
        state = state[31:-1, 1:-1]
        state[500:, :] = 0
        _, state = cv.threshold(state, 240, 1, cv.THRESH_BINARY)

        edged_image = cv.Canny(state * 255, 100, 200)

        for piece in self.pieces.values():
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
                    if (state[central_coord] == 1):
                        # print((min_loc[1]+h//2,min_loc[0]+w//2))

                        available_placements.append((central_coord, ti * 45))
                        i += 1

                    attempt += 1
