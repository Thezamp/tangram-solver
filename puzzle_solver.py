import os
import time

import numpy as np
import pandas as pd

import actr
from landmark import Landmark,retrieve_activation
from landmark_detector.landmark_extraction import LandmarkExtractor, get_grid_value, solution_limits
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
    ldm_i = 0
    for i in range(len(ldm_list)):
        l = Landmark(ldm_list[i])

        if len(current_landmarks) < 6 and l.name not in [x.name for x in current_landmarks]:
            current_landmarks.append(l)
            state_def.append(f'LANDMARK-{ldm_i + 1}')

            state_def.append(l.name)
            ldm_i +=1

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

    def __init__(self, tgn, params_dict, path="ACT-R:tangram-solver;models;solver-model.lisp", predictor = False):

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
        self.predictor = predictor
        self.prediction_answer = []

        data = pd.read_csv(f'{ROOT_DIR}/datasets/steps.csv')
        self.players_data = data.loc[data['tangram nr'] == tgn]

        #for phase in [5, 9, 13, 17]:
        for phase in range(4):
            phase_counts = pd.read_csv(f'{ROOT_DIR}/datasets/landmark_str_{phase}.csv')
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
        if self.predictor:
            print(f'Suggest update {piece_type}, {rotation} at {grid} ')
            if piece_type != 'PARALL-INV':
                self.prediction_answer.append(('Place', (piece_type,int(grid),int(rotation))))
            else:
                self.prediction_answer.append(('Place', ('PARALL', int(grid), int(rotation))))
            return True

        if piece_type=='BIG-T' and grid ==17.0:
            print('halt')
        self.status = 'updating'
        try:
            chosen_landmark = [x for x in self.current_landmarks if x.is_involved(piece_type, grid, rotation)][
                0]  # landmark that has been selected
            print('landmark')
        except IndexError:
            return False
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
        try:
            named_piece = [x for x in self.available_pieces if x.type == piece_type][0]
        except IndexError:
            return False
        try:
            self.available_pieces.remove(named_piece)
        except IndexError:
            return False
        try:
            self.pos[named_piece.index] = (x, y, rotation)
        except IndexError:
            return False
        # print(f'pos of {named_piece.index}')
        print(f'action taken: {named_piece.name}-{rotation} at grid pos {grid}')

        self.step_sequence.append((named_piece.name, grid, rotation))
        self.current_placements.append((chosen_landmark, named_piece))

        self.step += 1

        return True

    def piece_backtrack(self):
        if self.predictor:
            print('Suggest backtracking weak piece')
            self.prediction_answer.append(('Backtrack',None))
            return True
        self.btsteps += 1
        self.status = "piece_backtracking"
        # frequencies = [l.get_frequency(self.counts[self.step // 4]) for (l, p) in self.current_placements]
        # the strength must be updated with the new phase
        frequencies = [l.get_frequency(self.counts[self.step // 4]) for (l, p) in self.current_placements]
        idx = frequencies.index(min(frequencies))

        (landmark, named_piece) = self.current_placements.pop(idx)


        #new part

        active_actions = [x for x in self.current_landmarks].sort(key= lambda x: retrieve_activation(x.str))
        ###
        self.pos[named_piece.index] = puzzle_def.get(self.tgn).get('pos')[named_piece.index]
        self.available_pieces.append(named_piece)

        print(f'backtracking weak piece: {named_piece.name}')
        self.step_sequence.append((named_piece.name, -1, landmark.rotation))


        return True

    def region_backtrack(self):
        if self.predictor:
            print('Suggest backtracking problem piece')
            self.prediction_answer.append(('Backtrack', None))
            return  True
        self.status = "region_backtracking"
        self.btsteps += 1
        if len(self.problem_placements) != 0:
            landmark, named_piece = self.problem_placements.pop(0)

            self.pos[named_piece.index] = puzzle_def.get(self.tgn).get('pos')[named_piece.index]
            self.available_pieces.append(named_piece)

            print(f'backtracking piece: {named_piece.name}')

            self.step_sequence.append((named_piece.name, -1, landmark.rotation))
            self.current_placements.remove((landmark, named_piece))
            return True
        else:
            return self.piece_backtrack()

    def flag_completed(self):
        self.status = "completed"

        return True

    def run(self, time=20):

        actr.run(time)

    def save_state(self):
        state= []
        indexes = [[3,4],[2],[0,1],[5],[6]]
        for i in range(len(indexes)):
            piece_state = set()
            for piece_index in indexes[i]:
                p = self.pos[piece_index]
                grid = self.grid_from_turtle(p[0], p[1])
                if grid != -1:
                    piece_state.add((grid,float(p[2])))
            state.append(piece_state)

        return state

    def grid_from_turtle(self,x,y):
        # solution_limits = {1: [(-260, 120), (-120, 140)], 2: [(-280, 0), (-70, 210)], 3: [(-320, 60), (-140, 140)],
        #                    4: [(-280, 0), (-200, 300)]}
        global solution_limits
        xrange = solution_limits.get(self.tgn)[0]
        yrange = solution_limits.get(self.tgn)[1]
        xstep = (xrange[1] - xrange[0]) / 5
        ystep = (yrange[1] - yrange[0]) / 5
        if (x not in range(xrange[0], xrange[1] + 1) or y not in range(yrange[0], yrange[1] + 1)):
            return -1
        xgrid = (x - xrange[0]) // xstep

        ygrid = (y - yrange[0]) // ystep

        return ygrid * 5 + xgrid

def prediction_run(pzn,params_dict,kd=1,kcv=2):
    #steps =  pd.read_csv('./datasets/all_steps_test_paper.csv')
    steps = pd.read_csv('./datasets/all_steps.csv')
    steps = steps.loc[steps['tangram nr'] == pzn]

    acc =[]

    for participant in steps.sid.unique():
        score = 0
        max_score = 0
        p = Puzzle(pzn, params_dict, path="ACT-R:tangram-solver;models;predictor-model.lisp", predictor=True)
        p.path = f'{ROOT_DIR}/puzzle_state.png'
        if pzn == 4:
            p.pos[-1] = -1
        setpos(p.pos, p.sol, True)

        participant_steps = steps.loc[steps.sid == participant]
        pieces = [['BIG-T',True],['BIG-T',True],['MIDDLE-T',True],['SMALL-T',True],['SMALL-T',True],['SQUARE',True],['PARALL',True]]
        p.step = 0
        current_step = 0
        for i_step in range(len(participant_steps)-2):
            p.prediction_answer=[]
            row = participant_steps.iloc[i_step]
            if p.step >16:
                break

            #update state with participant's action
            print(f'participant action: {row["item"]}, {row.rot} at {row.grid_val} ')
            print('###')
            p.pos[row['i_item']] = (row.x,row.y,row.rot)
            setpos(p.pos, p.sol)

            #define currently available pieces
            partial = participant_steps[:i_step + 1]
            for pi in participant_steps.i_item.unique():
                pos = partial.loc[partial.i_item == pi]
                if pos.empty:
                    pieces[pi][1] = True
                elif pos.iloc[-1]['step'] == 100:
                    pieces[pi][1] = True
                else:
                    pieces[pi][1] = False

            available_pieces = [p[0] for p in pieces if p[1]]

            #Agent Part - prediction


            if row['step'] != 100.0:
            # if True:
            #     if row['step'] != 100.0:
            #         current_step =row['step']


                max_score += 1
                p.step = int(row.step)+1
                # p.step = int(current_step) +1
                print(p.step)
                (extract, problem) = p.extractor.extract(p.path, available_pieces, p.step,kd=kd,kcv=kcv)




                for i in range(10):
                    p.current_landmarks = puzzle_state_to_imaginal(extract, problem, len(available_pieces))
                    actr.goal_focus('start')
                    p.run()

                answer = max(set(p.prediction_answer), key=p.prediction_answer.count) if len(p.prediction_answer) else ['Skip',None]
                if answer[0] == 'Place':
                    p_move = answer[1]
                    next_row = participant_steps.iloc[i_step+1]
                    second_next_row = participant_steps.iloc[i_step +2]
                    print(f'next: {(next_row["item"],int(next_row["grid_val"]),int(next_row["rot"]))} ')
                    print(f'second next: {(second_next_row["item"], int(second_next_row["grid_val"]), int(second_next_row["rot"]))}  ')
                    if (p_move == (next_row['item'],int(next_row['grid_val']),int(next_row['rot'])) or
                            p_move == (second_next_row['item'], int(second_next_row['grid_val']), int(second_next_row['rot'])) ):
                        score +=1
                elif answer[0] == 'Backtrack':
                    print(participant_steps.iloc[i_step+1]['step'])
                    print(participant_steps.iloc[i_step+2]['step'])
                    if (participant_steps.iloc[i_step+1]['step'] == 100
                            or participant_steps.iloc[i_step+2]['step'] == 100):
                        score +=1
        acc.append(score/max_score)
    print(acc)
    print(np.mean(acc))
    return acc

def onerun(pzn,params_dict, kd, kcv):
    states=[]
    p = Puzzle(pzn,params_dict, path="ACT-R:tangram-solver;models;cognitive-module.lisp")


    p.path = f'{ROOT_DIR}/puzzle_state.png'
    setpos(p.pos, p.sol, True)

    (extract, problem) = p.extractor.extract(p.path, [x.type for x in p.available_pieces], p.step,kd=kd,kcv=kcv)
    p.current_landmarks = puzzle_state_to_imaginal(
        extract, False, True)
    actr.goal_focus('start')

    #while p.step < 16 and p.step+p.btsteps < 30:
    while p.step < 18 and p.step + p.btsteps < 31:


        if p.status == 'completed':
            print("puzzle completed")
            i =  p.step
            while i<17:
                states.append(p.save_state())
                i+=1

            break

        print(f"STEP: {p.step}")
        time.sleep(0.2)
        p.run(2)
        setpos(p.pos, p.sol)



        (extract, problem) = p.extractor.extract(p.path, [x.type for x in p.available_pieces], p.step, kd=kd, kcv=kcv)

        if p.status == 'region_backtracking':
            actr.goal_focus('is-backtracking')
        else:
            if p.status == 'piece_backtracking':
                actr.goal_focus('retrieve-ignoring-finsts')
            else:
                actr.goal_focus('start')
            if p.status == 'updating':
                states.append(p.save_state())
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


if __name__ == '__notmain__':
    # main()
    for puzzleid in [4]:
        for modeltype in [('balanced',1,3),('vision',0.75,3.25),('freq',1.25,2.75)]:
            # results_df = pd.DataFrame(
            #     columns=['run','step','small triangle', 'middle triangle', 'big triangle', 'square',
            #              'parallelogram'])
            # to_mat= []
            #
            # for r in range(30):
            #     print(f'puzzle {r}')
            #     s,step_sequence = onerun(puzzleid,{':rt': 2.5, ':mas': 10},modeltype[1],modeltype[2])
            #     to_mat.append(seq_to_list(step_sequence))
            #
            #     for i in range(len(s)):
            #         row = {'run' : r, 'step':(i+1),'small triangle':s[i][0],'middle triangle':s[i][1],
            #                        'big triangle':s[i][2],'square':s[i][3],'parallelogram':s[i][4]}
            #         results_df = results_df.append(row,ignore_index=True)
            #
            # results_df.to_csv(f'results/model_states_evolution_{puzzleid}_{modeltype[0]}_cnt.csv')
            # length = max(map(len, to_mat))
            # mat = np.array([xi + [0] * (length - len(xi)) for xi in to_mat])
            # np.savetxt(f"results/heatmap_{puzzleid}_{modeltype[0]}_cnt.csv", mat, delimiter=',')
            prediction_run(2,{':rt': 2.5, ':mas': 10},kd=modeltype[1], kcv=modeltype[2])

if __name__ == '__main__':
    for puzzleid in [4]:
        with open(f'./results/prediction_{puzzleid}.txt', 'w') as out:
            for modeltype in [('balanced',1,3),('vision',0.75,3.25),('freq',1.25,2.75)]:
                res = prediction_run(4, {':rt': 2.5, ':mas': 10}, kd=modeltype[1], kcv=modeltype[2])
                out.write(f'{modeltype}\t{res}\n')
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

# def main():
#     # results_df = pd.DataFrame(columns=['ans','rt','mas','step','small triangle', 'middle triangle','big triangle', 'square', 'parallelogram'])
#     # grid_param = [{':rt':2,':mas':6},{':rt':2.5,':mas':6}, {':rt':2,':mas':7}, {':rt':2.5,':mas':7}]
#     # for params_instance in grid_param:
#     #     steps = onerun(params_instance)
#     #     for i in range(len(steps)):
#     #         row = {'ans':params_instance.get(':ans'), 'rt':params_instance.get(':rt'), 'mas':params_instance.get(':mas'),
#     #                'step':(i+1)*4,'small triangle':[steps[i][3],steps[i][4]],'middle triangle':[steps[i][2]],
#     #                'big triangle':[steps[i][0],steps[i][1]],'square':[steps[i][5]],'parallelogram':[steps[i][6]]}
#     #         results_df = results_df.append(row,ignore_index=True)
#     #
#     # results_df.to_csv('param_search_results.csv')
#     to_mat = []
#     for i in range(31):
#         states, step_sequence = onerun({':rt':2.3,':mas':6})
#         to_mat.append(seq_to_list(step_sequence))
#
#     length = max(map(len, to_mat))
#     mat = np.array([xi + [0] * (length - len(xi)) for xi in to_mat])
#     np.savetxt("datasets/heatmap_4.csv",mat,delimiter=',')
#
# def create_state_evolution_df():
#     for i in range(31):
#         states, step_sequence = onerun({':rt': 2.2, ':mas': 6})
