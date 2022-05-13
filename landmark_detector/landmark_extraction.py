import numpy as np
import cv2 as cv
import pandas as pd
from matplotlib import pyplot as plt
from scipy import ndimage
# import pylab as pl
from matplotlib import collections as mc
import time
import os

# limits of the grid defined by hand
solution_limits = {1: [(-260, 120), (-120, 140)], 2: [(-280, -20), (-80, 200)], 3: [(-320, 60), (-140, 140)],
                   4: [(-280, 0), (-200, 300)]}

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_grid_value(rm, cm, n, tgn):
    '''
    Converts x and y matrix coordinates into grid values for tangram puzzle = tgn

    :param rm: row value in matrix coordinates
    :type rm: int
    :param cm: column value in matrix coordinates
    :type cm: int
    :param n: grid size
    :type n: int
    :return:  grid number 0-15, or -1 if outside the grid
    '''

    y = -rm + 300
    x = cm - 400

    xrange = solution_limits.get(tgn)[0]
    yrange = solution_limits.get(tgn)[1]
    xstep = (xrange[1] - xrange[0]) / n
    ystep = (yrange[1] - yrange[0]) / n
    if (x not in range(xrange[0], xrange[1] + 1) or y not in range(yrange[0], yrange[1] + 1)):
        return -1
    xgrid = (x - xrange[0]) // xstep

    ygrid = (y - yrange[0]) // ystep

    return x, y, ygrid * n + xgrid


def generate_rotation_templates(original, rotations):
    '''generates #rotations rotated and cropped templates from an original tan picture

    :param original: the original uncropped template picture
    :type original: numpy.array
    :param rotations: number of rotations to be produced (varies due to symmetries)
    :type rotations: int

    :return: the list of rotated and cropped templates
    :rtype: list[numpy.array]
    '''
    original = original[3:, 3:]
    nonzero = original.nonzero()
    templates = [original[min(nonzero[0]) - 2:max(nonzero[0]) + 2, min(nonzero[1]) - 2:max(nonzero[1]) + 2]]

    for r in range(-45, -45 * rotations, -45):
        rotated = ndimage.rotate(original, r)
        nonzero = rotated.nonzero()
        rotated = rotated[min(nonzero[0]) - 2:max(nonzero[0]) + 2, min(nonzero[1]) - 2:max(nonzero[1]) + 2]

        templates.append(rotated)

    return templates


def find_placements(piece, state_img, edged_image):
    """
    Applies template matching in order to find a number of possible placements for the given piece

    :param piece: an object of class Template representing the piece
    :type piece: Template
    :param state_img: the binarized image of the puzzle state
    :type state_img: ndarray
    :param edged_image: the image after the application of Canny
    :type edged_image: ndarray

    :return: a list of possible (imprecise) placements for the given piece, in matrix coordinate
    :rtype: list[(int,int)]
    """
    available_placements = []
    for ti in range(len(piece.templates)):
        current = piece.templates[ti]
        edges = cv.Canny(current * 255, 100, 200)
        h, w = current.shape[:2]

        method = cv.TM_SQDIFF

        # res = cv.matchTemplate(edged_image, edges, method, mask=current)
        res = cv.matchTemplate(edged_image, edges, method, mask=current)

        i = 0
        attempt = 0
        while i < 5 and attempt < 7:
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

            # xtop, xbotto, yleft, yright
            xt = min_loc[1] - h // 2 if min_loc[1] > 20 else 0
            xb = min_loc[1] + h // 2 + 1
            yl = min_loc[0] - w // 2 if min_loc[0] > 20 else 0
            yr = min_loc[0] + w // 2 + 1
            # removing the solution
            res[xt:xb, yl:yr] = float('inf')

            # finding the central point
            central_coord = (min_loc[1] + h // 2, min_loc[0] + w // 2)  # center of the bounding box

            # check how much overlapping is present
            part = state_img[min_loc[1]:min_loc[1] + h, min_loc[0]:min_loc[0] + w]
            if np.count_nonzero(np.bitwise_xor(np.bitwise_and(part, current), current)) < 50:

                if '-T' in piece.name:  # coordinates in the app are calculated on the long side
                    if ti == 0:
                        central_coord = (min_loc[1] + h - 2, min_loc[0] + w // 2)
                    elif ti == 2:
                        central_coord = (min_loc[1] + h // 2, min_loc[0] + 2)
                    elif ti == 4:
                        central_coord = (min_loc[1] + 2, min_loc[0] + w // 2)
                    elif ti == 6:
                        central_coord = (min_loc[1] + h // 2, min_loc[0] + w - 2)

                available_placements.append((central_coord, ti * 45))
                i += 1

            attempt += 1

    return available_placements


class Template:
    def __init__(self, name, path, rotations, flipped=False):
        self.name = name
        original_rotation = cv.imread(path, 0)
        t2, original_rotation = cv.threshold(original_rotation, 100, 1, cv.THRESH_BINARY)

        self.templates = generate_rotation_templates(original_rotation, rotations)
        self.flipped = flipped

    def describe(self):
        if not self.flipped:
            return self.name
        else:
            return "PARALL-INV"


class LandmarkExtractor:
    def __init__(self, counts, tgn=4):
        self.pieces_templates = [Template('SMALL-T', f'{ROOT_DIR}/tans/smallt.png', 7),
                                 Template('BIG-T', f'{ROOT_DIR}/tans/bigt.png', 7),
                                 Template('MIDDLE-T', f'{ROOT_DIR}/tans/middlet.png', 7),
                                 Template('SQUARE', f'{ROOT_DIR}/tans/square.png', 2),
                                 Template('PARALL', f'{ROOT_DIR}/tans/parall1.png', 3),
                                 Template('PARALL', f'{ROOT_DIR}/tans/parall2.png', 3, flipped=True)
                                 ]
        self.tgn = tgn

        self.counts = counts

    def extract(self, image_path, pieces_list, step):
        counts = self.counts[step // 4]

        problem = False
        # binary image
        state = cv.imread(image_path, 0)

        state[500:, :] = 0
        state = state[:, :450]
        _, state = cv.threshold(state, 240, 1, cv.THRESH_BINARY)
        cv.imwrite('./utility_pictures/thresholded.png', state * 255)
        # edges
        edged_image = cv.Canny(state * 255, 100, 200)
        cv.imwrite('./utility_pictures/edged.png', edged_image)
        extracted_landmarks = set()
        placeable_pieces = set()
        for piece in [x for x in self.pieces_templates if x.name in pieces_list]:

            piece_counts = counts.loc[counts.item == piece.name]
            piece_landmarks = set()
            available_placements = find_placements(piece, state, edged_image)
            if len(available_placements) == 0:
                print(f'{piece.name}:no placements found')
            else:
                placeable_pieces.add(piece.name if "PARALL" not in piece.name else "PARALL")
            for p in available_placements:
                rot = p[1]
                x, y, grid = get_grid_value(p[0][0], p[0][1], 5, self.tgn)
                if grid != -1:

                    row = piece_counts.loc[(piece_counts['grid_val'] == grid) & \
                                           (piece_counts['rot'] == rot)]
                    if not row.empty:
                        ldm_count = row['strength'].values
                        piece_landmarks.add((piece.describe(), x, y, grid, rot, ldm_count[0]))

            extracted_landmarks.update(piece_landmarks)

        print(placeable_pieces)
        print(set(pieces_list))

        print("#######################")

        if placeable_pieces != set(pieces_list):
            problem = True

        return sorted(list(extracted_landmarks), reverse=True, key=lambda x: x[5]), problem
