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

def get_grid_value(rm, cm, tgn):
    '''
    Converts x and y matrix coordinates into grid values for tangram puzzle = tgn

    outputs the grid number 0-15, or -1 in case the placement is generically outside the grid
    '''

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
    '''generates #rotations rotated and cropped templates from an original tan picture

    :param nparray original: the original uncropped template picture
    :param int rotations: number of rotations to be produced (varies due to symmetries)

    :return list: the list of rotated and cropped templates
    '''
    original = original[3:,3:]
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

    :param Template piece: an object of class Template representing the piece
    :param ndarray state_img: the binarized image of the puzzle state
    :param ndarray edged_image: the image after the application of Canny

    :returns List(Tuples): a list of possible (imprecise) placements for the given piece
    """
    available_placements = []
    for ti in range(len(piece.templates)):
        current = piece.templates[ti]
        edges = cv.Canny(current * 255, 100, 200)
        h, w = current.shape[:2]
        method = cv.TM_SQDIFF

        #res = cv.matchTemplate(edged_image, edges, method, mask=current)
        res = cv.matchTemplate(edged_image, edges, method)


        i = 0
        attempt = 0
        while i < 5 and attempt < 7:
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

            xt = min_loc[1] - h // 2 if min_loc[1] > 20 else 0
            xb = min_loc[1] + h // 2 + 1
            yl = min_loc[0] - w // 2 if min_loc[0] > 20 else 0
            yr = min_loc[0] + w // 2 + 1

            res[xt:xb, yl:yr] = float('inf')
            central_coord = (min_loc[1] + h // 2, min_loc[0] + w // 2)  # center of the bounding box
            # if (state_img[central_coord] == 1):
            part = state_img[min_loc[1]:min_loc[1]+h,min_loc[0]:min_loc[0]+w]
            if np.count_nonzero(np.bitwise_xor(np.bitwise_and(part,current),current)) <50 :
                # print((min_loc[1]+h//2,min_loc[0]+w//2))
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
    def __init__(self, name, path, rotations, flipped= False):
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
        # this can be a list
        # self.pieces = {'small_t': Template('SMALL-T', './tans/smallt.png', 7),
        #                'big_t': Template('BIG-T', './tans/bigt.png', 7),
        #                'middle_t': Template('MIDDLE-T', './tans/middlet.png', 7),
        #                'square': Template('SQUARE', './tans/square.png', 2),
        #                'parallelogram': Template('PARALL', './tans/parall1.png', 3),
        #                'parallelogram_m': Template('PARALL', './tans/parall2.png', 7)
        #                }
        self.pieces_templates = [Template('SMALL-T', f'{ROOT_DIR}/tans/smallt.png', 7),
                       Template('BIG-T',  f'{ROOT_DIR}/tans/bigt.png', 7),
                       Template('MIDDLE-T',  f'{ROOT_DIR}/tans/middlet.png', 7),
                       Template('SQUARE',  f'{ROOT_DIR}/tans/square.png', 2),
                       Template('PARALL',  f'{ROOT_DIR}/tans/parall1.png', 3),
                       Template('PARALL',  f'{ROOT_DIR}/tans/parall2.png', 3, flipped=True)
                       ]
        self.tgn = tgn
        # self.counts = []
        # for phase in [4, 8, 12, 16]:
        #     counts = pd.read_csv( f'{ROOT_DIR}/../datasets/landmark_counts_{phase}.csv')
        #     self.counts.append(counts.loc[counts['tangram nr'] == tgn])
        self.counts = counts

    def extract(self, image_path, pieces_list, step):
        counts = self.counts[step // 4]
        #counts = self.counts[3]
        problem = False
        # binary image
        state = cv.imread(image_path, 0)
        #state = state[31:-1, 1:-1]
        state[500:, :] = 0
        state= state[:,:450]
        _, state = cv.threshold(state, 240, 1, cv.THRESH_BINARY)
        cv.imwrite('thresholded.png',state*255)
        # edges
        edged_image = cv.Canny(state * 255, 100, 200)
        cv.imwrite('edged.png',edged_image)
        extracted_landmarks = set()
        for piece in [x for x in self.pieces_templates if x.name in pieces_list]:

            piece_counts = counts.loc[counts.item == piece.name]
            piece_landmarks = set()
            available_placements = find_placements(piece, state, edged_image)
            # list of ((x,y),rot)
            for p in available_placements:
                rot = p[1]
                grid = get_grid_value(p[0][0], p[0][1], self.tgn)
                if grid != -1:


                    row = piece_counts.loc[(piece_counts['grid_val'] == grid) & \
                                     (piece_counts['rot'] == rot)]
                    if not row.empty:
                        ldm_count = row['counts'].values
                        #extracted_landmarks.add((piece.name, grid, rot, ldm_count[0]))
                        piece_landmarks.add((piece.describe(), grid, rot, ldm_count[0]))
            # if len(piece_landmarks) == 0 and not piece_counts.empty and piece.name != 'PARALL':
            # if len(available_placements) == 0  and piece.name != 'PARALL':
            #     problem = True

            extracted_landmarks.update(piece_landmarks)

        if set([x[0] if "PARALL" not in x[0] else "PARALL" for x in extracted_landmarks]) != set(pieces_list) and set(pieces_list).issubset(set(counts['item'].tolist())):
            problem = True
        return sorted(list(extracted_landmarks), reverse=True, key=lambda x: x[3]), problem


# def main():
#     l = LandmarkExtractor(4)
#     start = time.time()
#     pieces_list = ['SMALL-T', 'BIG-T', 'MIDDLE-T', 'SQUARE', 'PARALL']
#     imaginal, problem = l.extract(f'{ROOT_DIR}/puzzle_state.png', pieces_list, 0)
#     print(time.time() - start)
#     print(imaginal)
#     print(problem)
#     print(len(imaginal))
#
#     # time.sleep(10)
#     return 0
#
#
# if __name__ == '__main__':
#     main()
