import actr
from landmark import Landmark


def list_to_imaginal(ldm_list):
    state_def = ['isa', 'PUZZLE-STATE', 'finished', 'f']
    for ldm in ldm_list:
        state_def.append(ldm.name)
        state_def.append(ldm.name)
    imaginal_chunk = actr.define_chunks(state_def)
    actr.set_buffer_chunk('imaginal', imaginal_chunk)


class Puzzle():

    def __init__(self, path= "ACT-R:tangram-solver;models;simple-model.lisp"):

        actr.reset()
        actr.load_act_r_model(path)

        actr.add_command("update", self.update)
        actr.add_command("backtrack", self.backtrack)
        actr.add_dm(['start', 'isa', 'goal', 'state', 'choose-landmark'])
        self.active_landmarks = []
        self.unseen_landmarks = []
        self.active_pieces = ["small-triangle1", "small-triangle2", "square", "medium-triangle",
                              "parallelogram", "big-triangle1", "big-triangle2"]
        self.last_placed = []


    def update(self, piece, location):

        print(f'action taken: {piece} at {location}')

        used_ldm = [l for l in self.active_landmarks if l.is_involved(piece, location)]

        used_ldm = used_ldm[0]
        self.active_landmarks.remove(used_ldm)  # maybe not needed
        self.active_landmarks.extend(used_ldm.get_triggers())
        self.active_landmarks = [ldm for ldm in self.active_landmarks if ldm not in used_ldm.get_removes()]

        if len(self.active_landmarks) == 0:
            print("stop")
            imaginal_chunk = actr.define_chunks(['isa', 'puzzle-state', 'finished', 't'])
            actr.set_buffer_chunk('imaginal', imaginal_chunk)
        else:
            list_to_imaginal(self.active_landmarks)

        self.last_placed.append(used_ldm)
        return True

    def backtrack(self, useless_param):


        last = self.last_placed.pop(-1)
        print(f'backtracking: {last.name}')
        #print([l.name for l in last.get_removes()])
        self.active_landmarks = [ldm for ldm in self.active_landmarks if ldm not in last.get_triggers()]
        self.active_landmarks.extend(last.get_removes())
        self.active_landmarks.append(last)

        #print(last.get_removes())
        #print(self.active_landmarks)
        list_to_imaginal(self.active_landmarks)
        return True

    def run(self, time=10):

        actr.goal_focus('start')
        actr.run(time)