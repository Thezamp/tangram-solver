import os
import time

import numpy as np
import pandas as pd

import actr
from landmark import Landmark
from landmark_detector.landmark_extraction import LandmarkExtractor
from application.create_state import setpos

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

#big t, big t, middle t, small t, small t, square, parall
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


def puzzle_state_to_imaginal(ldm_list, problem, available):
    """sets the actr imaginal buffer

    :param ldm_list: list of landmarks definitions
    :type ldm_list: List
    :param problem: whether to add the UNF-REG landmark
    :type problem: Bool
    :param available: whether there are still pieces available
    :type available: Bool
    :return current_landmarks: list of Landmarks defining the current imaginal buffer, for representation


    The first 6 strongest landmarks are loaded into the ACT-R imaginal buffer. The rest are anyway added to the declarative
    memory

    The imaginal buffer is so defined:
    (chunk-type PUZZLE-STATE
        PIECES-AVAILABLE
        LANDMARK-1
        LANDMARK-2
        LANDMARK-3
        LANDMARK-4
        LANDMARK-5
        LANDMARK-6
        SPECIAL-LANDMARK
    )

    """

    if available:
        state_def = ['isa', 'PUZZLE-STATE', 'PIECES-AVAILABLE', 'T']
    else:
        state_def = ['isa', 'PUZZLE-STATE', 'PIECES-AVAILABLE', 'nil']
        imaginal_chunk = actr.define_chunks(state_def)
        actr.set_buffer_chunk('imaginal', imaginal_chunk)
        return []

    current_landmarks = []

    for i in range(len(ldm_list)):
        l = Landmark(ldm_list[i])
        current_landmarks.append(l)
        if i < 6:
            state_def.append(f'LANDMARK-{i + 1}')

            state_def.append(l.name)

    if problem:
        state_def.append('SPECIAL-LANDMARK')
        state_def.append('UNF-REG')

    imaginal_chunk = actr.define_chunks(state_def)
    actr.overwrite_buffer_chunk('imaginal', imaginal_chunk)
    return current_landmarks


class Piece():
    def __init__(self, name, type, index):
        self.name = name
        self.type = type
        self.used = False
        self.grid = -1
        self.rotation = 0
        self.index = index

    def place(self, grid, rotation):
        self.grid = grid
        self.rotation = rotation
        self.used = True

    def remove(self):
        self.grid = -1
        self.used = False


class Puzzle():

    def __init__(self, tgn, params_dict, path="ACT-R:tangram-solver;models;solver-model.lisp"):

        #self.completed = False
        self.status = None
        self.actr_setup(path, params_dict)
        self.tgn = tgn

        self.pos = puzzle_def.get(tgn).get('pos').copy()
        self.sol = puzzle_def.get(tgn).get('sol').copy()
        self.available_pieces = [Piece("SMALL-T-1", 'SMALL-T', 3), Piece("SMALL-T-2", 'SMALL-T', 4),
                                 Piece("MIDDLE-T", 'MIDDLE-T', 2),
                                 Piece("BIG-T-1", 'BIG-T', 0), Piece("BIG-T-2", 'BIG-T', 1),
                                 Piece("SQUARE", 'SQUARE', 5), Piece("PARALL", 'PARALL', 6)]
        self.path = ''
        self.current_placements = []  # what landmarks are actually used
        self.step_sequence = []  # sequence of all the steps
        self.problem_placements = []  # the landmarks that generated or are placed while there is an unfeasible region
        self.current_landmarks = []  # python equivalent of the imaginal buffer
        self.counts = []
        self.step = 0
        self.btsteps = 0

        data = pd.read_csv(f'{ROOT_DIR}/datasets/steps.csv')
        self.players_data = data.loc[data['tangram nr'] == tgn]

        for phase in [4, 8, 12, 16]:
            phase_counts = pd.read_csv(f'{ROOT_DIR}/datasets/landmark_str_{phase + 1}.csv')
            self.counts.append(phase_counts.loc[phase_counts['tangram nr'] == tgn])

        self.extractor = LandmarkExtractor(self.counts, tgn)

    def actr_setup(self, path,params_dict):
        actr.clear_all()
        actr.reset()

        actr.load_act_r_model(path)
        for param_name in params_dict.keys():
            actr.set_parameter_value(param_name, params_dict.get(param_name))


        actr.add_command("update", self.update)
        actr.add_command("piece-backtrack", self.piece_backtrack)
        actr.add_command("region-backtrack", self.region_backtrack)
        actr.add_command("flag-completed", self.flag_completed)
        actr.add_dm(['start', 'isa', 'goal', 'state', 'choose-landmark'])

    def update(self, piece_type, grid, rotation):
        """Updates the state given an ACT-R chunk definition

        :param piece_type: piece in the landmark
        :type piece_type: String
        :param grid: grid position of the landmark
        :type grid: int
        :param rotation: rotation value of the landmark
        :type rotation: int
        :return: True

        Once the landmark is extractedfrom the current imaginal, the state is updated.

        Specifically, the first available piece of the given type is chosen and removed from the available ones.
        The tuple (Piece, Landmark) is added to the step sequence and to the current placements. The position in the
        experiment window is taken from the human data
        """
        self.status = 'updating'
        try:
            chosen_landmark = [x for x in self.current_landmarks if x.is_involved(piece_type, grid, rotation)][
                0]  # landmark that has been selected
            print('landmark')
        except IndexError:
            print('here')
        if piece_type == 'PARALL':
            self.pos[7] = 1
        if piece_type == 'PARALL-INV':
            self.pos[7] = -1
            piece_type = 'PARALL'

        # generate the new picture

        # x, y = pixel_rows[['x', 'y']].iloc[0]
        pixel_rows = pd.DataFrame({'counts': self.players_data.loc[(self.players_data.item == piece_type) & \
                                                                   (self.players_data['grid_val'] == grid) & \
                                                                   (self.players_data.rot == rotation)].groupby(
            ['x', 'y']).size()}).reset_index()
        x, y = pixel_rows.sort_values(by='counts', ascending=False)[['x', 'y']].iloc[0]

        # named_piece = next(x for x in self.available_pieces if x.type == piece_type)
        named_piece = [x for x in self.available_pieces if x.type == piece_type][0]
        print('piece')
        self.available_pieces.remove(named_piece)
        print('removed')
        self.pos[named_piece.index] = (x, y, rotation)
        print(f'pos of {named_piece.index}')
        print(f'action taken: {named_piece.name}-{rotation} at grid pos {grid}')

        self.step_sequence.append((named_piece.name, grid, rotation))
        self.current_placements.append((chosen_landmark, named_piece))

        self.step += 1

        return True

    def piece_backtrack(self):
        self.status = "piece_backtracking"
        # frequencies = [l.get_frequency(self.counts[self.step // 4]) for (l, p) in self.current_placements]
        # the strength must be updated with the new phase
        frequencies = [l.get_frequency(self.counts[self.step // 4]) for (l, p) in self.current_placements]
        idx = frequencies.index(min(frequencies))

        (landmark, named_piece) = self.current_placements.pop(idx)

        self.pos[named_piece.index] = puzzle_def.get(self.tgn).get('pos')[named_piece.index]
        self.available_pieces.append(named_piece)

        print(f'backtracking weak piece: {named_piece.name}')
        self.step_sequence.append((named_piece.name, -1, landmark.rotation))
        self.btsteps += 1

        return True

    def region_backtrack(self):
        self.status = "region_backtracking"
        landmark, named_piece = self.problem_placements.pop(0)

        self.pos[named_piece.index] = puzzle_def.get(self.tgn).get('pos')[named_piece.index]
        self.available_pieces.append(named_piece)

        print(f'backtracking piece: {named_piece.name}')

        self.step_sequence.append((named_piece.name, -1, landmark.rotation))
        self.current_placements.remove((landmark, named_piece))
        self.btsteps += 1

        return True

    def flag_completed(self):
        self.status = "completed"

        return True

    def run(self, time=20):

        actr.run(time)


def onerun(params_dict):
    states=[]
    p = Puzzle(4,params_dict, path="ACT-R:tangram-solver;models;backtracking-xy-model.lisp")


    p.path = f'{ROOT_DIR}/puzzle_state.png'
    setpos(p.pos, p.sol, True)

    (extract, problem) = p.extractor.extract(p.path, [x.type for x in p.available_pieces], p.step)
    p.current_landmarks = puzzle_state_to_imaginal(
        extract, False, True)
    actr.goal_focus('start')

    while p.step < 16 and p.step+p.btsteps < 30:


        if p.status == 'completed':
            print("puzzle completed")
            i =  p.step //4
            while i<4:
                states.append(p.pos)
                i+=1

            break

        print(f"STEP: {p.step}")
        time.sleep(0.2)
        p.run(2)
        setpos(p.pos, p.sol)



        (extract, problem) = p.extractor.extract(p.path, [x.type for x in p.available_pieces], p.step)

        if p.status == 'region_backtracking':
            actr.goal_focus('is-backtracking')
        else:
            if p.status == 'piece_backtracking':
                actr.goal_focus('retrieve-ignoring-finsts')
            else:
                actr.goal_focus('start')
            if p.status == 'updating' and p.step % 4==0:
                states.append(p.pos)
            if problem:
                p.problem_placements.append(p.current_placements[-1])

        if (not problem) and len(p.problem_placements) != 0:
            p.problem_placements = []

        p.current_landmarks = puzzle_state_to_imaginal(extract, problem, len(p.available_pieces))

    return states, p.step_sequence

def seq_to_list(step_sequence):
    conversion= {'SMALL-T-1':1, 'SMALL-T-2':1, "SQUARE":2, "PARALL":3,"MIDDLE-T": 4,
                "BIG-T-1":5, "BIG-T-2":5 }
    converted_steps= []
    for step in step_sequence:
        converted_steps.append(conversion.get(step[0]))
    return converted_steps

def main():
    # results_df = pd.DataFrame(columns=['ans','rt','mas','step','small triangle', 'middle triangle','big triangle', 'square', 'parallelogram'])
    # grid_param = [{':rt':2,':mas':6},{':rt':2.5,':mas':6}, {':rt':2,':mas':7}, {':rt':2.5,':mas':7}]
    # for params_instance in grid_param:
    #     steps = onerun(params_instance)
    #     for i in range(len(steps)):
    #         row = {'ans':params_instance.get(':ans'), 'rt':params_instance.get(':rt'), 'mas':params_instance.get(':mas'),
    #                'step':(i+1)*4,'small triangle':[steps[i][3],steps[i][4]],'middle triangle':[steps[i][2]],
    #                'big triangle':[steps[i][0],steps[i][1]],'square':[steps[i][5]],'parallelogram':[steps[i][6]]}
    #         results_df = results_df.append(row,ignore_index=True)
    #
    # results_df.to_csv('param_search_results.csv')
    to_mat = []
    for i in range(31):
        states, step_sequence = onerun({':rt':2.2,':mas':6})
        to_mat.append(seq_to_list(step_sequence))

    length = max(map(len, to_mat))
    mat = np.array([xi + [0] * (length - len(xi)) for xi in to_mat])
    np.savetxt("datasets/heatmap_4.csv",mat,delimiter=',')


if __name__ == '__main__':
    main()


'''
### parameters that can be changed:
rt, mas, ans
bla based on strength
strength distribution?
finsts

### possible tweaks:
decreasing activation when backtracking

### further steps:
parameter tuning 
results comparison function

'''