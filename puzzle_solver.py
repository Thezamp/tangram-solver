import os
import random

import pandas as pd

import actr
from landmark import Landmark
from landmark_detector.landmark_extraction import LandmarkExtractor
from application.application_screen import ApplicationScreen
from application.create_state import setpos

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

puzzle_def = {1: {'pos': [(250, 99, 180), (349, 0, 270), (200, -49, 225), (151, 49, 90), (250, -49, 0), (200, 0, 45),
                          (274, -74, 90), 1],
                  'sol': [(-100, 40, 0), (-100, -34, 135), (-172, -34, 180), (-65, 3, -45), (7, -69, -45), (-137, 3, 0),
                          (44, -69, 45), 1], },
              2: {'pos': [(250, 99, 180), (349, 0, 270), (200, -49, 225), (151, 49, 90), (250, -49, 0), (200, 0, 45),
                          (274, -74, 90), 1],
                  'sol': [(-101, 40, 0), (-137, 38, -180), (-188, -11, 225), (-88, -61, 0), (-38, -11, 270),
                          (-166, 147, 0), (-202, 75, 45), 1]},
              3: {'pos': [(250, 99, 180), (349, 0, 270), (200, -49, 225), (151, 49, 90), (250, -49, 0), (200, 0, 45),
                          (274, -74, 90), 1],
                  'sol': [(-161, 40, 90), (-61, -60, 0), (-122, -65, 180), (-200, 45, -225), (-270, -25, -225),
                          (-200, -25, 0),
                          (-194, -100, 135), -1]},
              4: {'pos': [(250, 99, 180), (349, 0, 270), (200, -49, 225), (151, 49, 90), (250, -49, 0), (200, 0, 45),
                          (274, -74, 90), 1],
                  'sol': [(-131, -43, 45), (-131, 99, 135), (-112, -63, 225), (-140, -152, 135), (-65, 244, 0),
                          (-65, 207, 0),
                          (-192, 90, 90), -1]}
              }


def puzzle_state_to_imaginal(extracted,available):
    """
    sets the actr imaginal buffer

    the imaginal buffer is so defined:
    (chunk-type PUZZLE-STATE
        PIECES-AVAILABLE
        LANDMARK-1
        LANDMARK-2
        LANDMARK-3
        LANDMARK-4
        LANDMARK-5yu
        LANDMARK-6
        SPECIAL-LANDMARK
    )

    """


    ldm_list = extracted[0]
    problem = extracted[1]
    if available:
        state_def = ['isa', 'PUZZLE-STATE', 'PIECES-AVAILABLE', 'T']
    else:
        state_def = ['isa', 'PUZZLE-STATE', 'PIECES-AVAILABLE', 'nil']
        imaginal_chunk= actr.define_chunks(state_def)
        actr.set_buffer_chunk('imaginal', imaginal_chunk)
        return []

    current_imaginal = []
    flip = 1
    #for i in range(len(ldm_list[0:6])):
    for i in range(len(ldm_list)):
        l = Landmark(ldm_list[i])
        if i <6:
            state_def.append(f'LANDMARK-{i + 1}')

            state_def.append(l.name)
            current_imaginal.append(l)
    if problem:
        state_def.append('SPECIAL-LANDMARK')
        state_def.append('UNF-REG')

    imaginal_chunk = actr.define_chunks(state_def)
    actr.set_buffer_chunk('imaginal', imaginal_chunk)
    return current_imaginal


class Piece():
    def __init__(self, name, type, index):
        self.name = name
        self.type = type
        self.used = False
        self.grid = -1
        self.orientation = 0
        self.index = index

    def place(self, grid, orientation):
        self.grid = grid
        self.orientation = orientation
        self.used = True

    def remove(self):
        self.grid = -1
        self.used = False


class Puzzle():
    ###NEED TO FIX PIECES AND LANDMARKS
    def __init__(self, tgn, path="ACT-R:tangram-solver;models;solver-model.lisp"):


        self.completed = False #needed because of act-r setup
        self.actr_setup(path)

        self.pos = puzzle_def.get(tgn).get('pos')
        self.sol = puzzle_def.get(tgn).get('sol')
        self.available_pieces = [Piece("SMALL-T-1", 'SMALL-T', 3), Piece("SMALL-T-2", 'SMALL-T', 4),
                                 Piece("MIDDLE-T", 'MIDDLE-T', 2),
                                 Piece("BIG-T-1", 'BIG-T', 0), Piece("BIG-T-2", 'BIG-T', 1),
                                 Piece("SQUARE", 'SQUARE', 5), Piece("PARALL", 'PARALL', 6)]
        self.path = ''
        self.current_placements = []  # what landmarks are actually used
        self.step_sequence = []  # sequence of all the steps
        self.problem_placements = []  # the landmarks that generated or are placed while there is an unfeasible region
        self.current_imaginal = []  # python equivalent of the imaginal buffer
        self.counts = []
        self.step = 0

        data = pd.read_csv(f'{ROOT_DIR}/datasets/steps.csv')
        self.players_data = data.loc[data['tangram nr'] == tgn]

        for phase in [4, 8, 12, 16]:
            phase_counts = pd.read_csv(f'{ROOT_DIR}/datasets/landmark_counts_{phase}.csv')
            self.counts.append(phase_counts.loc[phase_counts['tangram nr'] == tgn])

        self.extractor = LandmarkExtractor(self.counts, tgn)

    def actr_setup(self, path):
        actr.reset()
        actr.load_act_r_model(path)

        actr.add_command("update", self.update)
        actr.add_command("piece-backtrack", self.piece_backtrack)
        actr.add_command("region-backtrack", self.region_backtrack)
        actr.add_command("flag-completed", self.flag_completed)
        actr.add_dm(['start', 'isa', 'goal', 'state', 'choose-landmark'])

    def update(self, piece_type, grid, orientation):

        # update the state
        chosen_landmark = [x for x in self.current_imaginal if x.is_involved(piece_type, grid, orientation)][
            0]  # landmark that has been selected

        if piece_type == 'PARALL':
            self.pos[7] = 1
        if piece_type == 'PARALL-INV':
            self.pos[7] = -1
            piece_type = 'PARALL'
        # generate the new picture
        pixel_rows = self.players_data.loc[(self.players_data.item == piece_type) & \
                                           (self.players_data['grid_val'] == grid) & \
                                           (self.players_data.rot == orientation)][['x', 'y']]
        x, y = pixel_rows.iloc[random.randint(0, len(pixel_rows) - 1)]
        named_piece = next(x for x in self.available_pieces if x.type == piece_type)
        self.available_pieces.remove(named_piece)

        self.pos[named_piece.index] = (x, y, orientation)

        print(f'action taken: {named_piece.name}-{orientation} at grid pos {grid}')

        self.step_sequence.append((named_piece.name, grid, orientation))
        self.current_placements.append((chosen_landmark, named_piece))

        self.step += 1

        # generate the new imaginal
        # extracted= self.extractor.extract(self.path, [x.type for x in self.available_pieces], self.step)
        #
        # if extracted[1]:
        #     #the piece created an unfeasible region
        #     self.problem_placements.append((chosen_landmark,named_piece))

        # self.current_imaginal = puzzle_state_to_imaginal(extracted)

        return True

    def piece_backtrack(self):
        #print('to be implemented')

        frequencies = [l.get_frequency(self.counts[self.step // 4]) for (l, p) in self.current_placements]
        idx = frequencies.index(min(frequencies))

        (landmark, named_piece) = self.current_placements.pop(idx)

        x, y = self.players_data.loc[(self.players_data.item == named_piece.type) & \
                                     (self.players_data['grid_val'] == -1)][['x', 'y']].iloc[0]

        self.pos[named_piece.index] = (x, y, landmark.orientation)
        self.available_pieces.append(named_piece)

        print(f'backtracking weak piece: {named_piece.name}')
        self.step_sequence.append((named_piece.name, -1, landmark.orientation))
        self.step += 1
        return True

    def region_backtrack(self):
        landmark, named_piece = self.problem_placements.pop(0)
        x, y = self.players_data.loc[(self.players_data.item == named_piece.type) & \
                                     (self.players_data['grid_val'] == -1)][['x', 'y']].iloc[0]
        self.pos[named_piece.index] = (x, y, landmark.orientation)
        self.available_pieces.append(named_piece)
        print(f'backtracking piece: {named_piece.name}')
        self.step_sequence.append((named_piece.name, -1, landmark.orientation))
        self.current_placements.remove((landmark, named_piece))
        self.step += 1

        # extracted = self.extractor.extract(self.path, [x.type for x in self.available_pieces], self.step)

        # self.current_imaginal = puzzle_state_to_imaginal(extracted)
        return True

    def flag_completed(self):
        self.completed = True

        return True

    def run(self, time=20):

        actr.goal_focus('start')
        actr.run(time)


def main():
    p = Puzzle(4, path="ACT-R:tangram-solver;models;backtracking-solver-model.lisp")
    p.path = f'{ROOT_DIR}/puzzle_state.png'
    setpos(p.pos, p.sol, True)

    p.current_imaginal = puzzle_state_to_imaginal(
        p.extractor.extract(p.path, [x.type for x in p.available_pieces], p.step), True)

    for i in range(15):
        if p.completed:
            print("puzzle completed")
            break

        print(f"STEP: {p.step}")
        p.run(2)
        setpos(p.pos, p.sol)

        extract = p.extractor.extract(p.path, [x.type for x in p.available_pieces], p.step)
        if extract[1]:
            p.problem_placements.append(p.current_placements[-1])
        if not extract[1] and len(p.problem_placements) != 0:
            p.problem_placements = []
        p.current_imaginal = puzzle_state_to_imaginal(extract,len(p.available_pieces))


if __name__ == '__main__':
    main()
