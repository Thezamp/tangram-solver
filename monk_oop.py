import actr
from landmark import Landmark


# path= "ACT-R:tangram-solver;simple-model.lisp"

def generate_monk_ldm():
    hat = Landmark("ST-HAT", "SMALL-T", "HAT", "SIMPLE")
    face = Landmark("SQ-FACE", "SQUARE", "FACE", 'SIMPLE')
    arm = Landmark("PG-ARM", 'PARALL', 'ARM', 'SIMPLE')
    foot = Landmark("ST-FOOT", 'SMALL-T', 'FOOT', 'SIMPLE')
    body = Landmark("BODY", "NONE", "BODY", 'COMPLEX')
    #######
    belly = Landmark('BT-BELLY', 'BIG-T', 'BELLY', 'SIMPLE')
    neck = Landmark('BT-NECK', 'BIG-T', 'NECK', 'SIMPLE')
    knee = Landmark('MT-KNEE', 'MEDIUM-T', 'KNEE', 'SIMPLE')
    upperbody = Landmark('BT-UPPER', 'BIG-T', 'UPPER', 'SIMPLE')
    lowerbody = Landmark('BT-LOWER', 'BIG-T', 'LOWER', 'SIMPLE')
    bottom = Landmark('MT-LOWER', 'MEDIUM-T', 'LOWER', 'SIMPLE')
    leg = Landmark('BT-KNEE', 'BIG-T', 'KNEE', 'SIMPLE')
    error = Landmark('LANDMARK-ERROR', 'ERROR', 'ERROR', 'SIMPLE')

    # simple "deterministic"version
    body.add_triggers([belly, upperbody, lowerbody, knee])
    belly.add_removes([upperbody, lowerbody])
    belly.add_triggers([error])
    upperbody.add_removes([belly])
    lowerbody.add_removes([belly])
    # body.add_triggers([belly, neck, knee, upperbody, lowebody, bottom, leg])
    # belly.add_removes([neck,upperbody,lowerbody,leg,bottom])
    # belly.add_triggers([error])
    # neck.add_removes([belly,upperbody,lowerbody,bottom])
    # neck.add_triggers([error])
    # knee.add_removes([leg,bottom])

    active = [hat, face, arm, foot, body]
    # active = [hat, face, arm, foot]
    # unseen = [belly, neck, knee, upperbody, lowerbody, bottom, leg,error]
    # currently not using unseen
    unseen = [belly, upperbody, lowerbody, knee, error]

    return active, unseen


def list_to_imaginal(ldm_list):
    state_def = ['isa', 'PUZZLE-STATE', 'finished', 'f']
    for ldm in ldm_list:
        state_def.append(ldm.name)
        state_def.append(ldm.name)
    imaginal_chunk = actr.define_chunks(state_def)
    actr.set_buffer_chunk('imaginal', imaginal_chunk)


class Monk():
    def __init__(self, path= "ACT-R:tangram-solver;simple-model.lisp"):

        actr.reset()
        actr.load_act_r_model(path)
        actr.add_command("update", self.update)
        actr.add_command("backtrack", self.backtrack)
        actr.add_dm(['start', 'isa', 'goal', 'state', 'choose-landmark'])
        self.active_landmarks, self.unseen_landmarks = generate_monk_ldm()
        self.active_pieces = ["small-triangle1", "small-triangle2", "square", "medium-triangle",
                              "parallelogram", "big-triangle1", "big-triangle2"]
        self.last_placed = []
        list_to_imaginal(self.active_landmarks)

    def update(self, piece, location):
        # print(piece)
        # print(location)
        used_ldm = [l for l in self.active_landmarks if l.is_involved(piece, location)]
        # print(used_ldm)
        used_ldm = used_ldm[0]
        self.active_landmarks.remove(used_ldm)  # maybe not needed
        self.active_landmarks.extend(used_ldm.get_triggers())
        self.active_landmarks = [ldm for ldm in self.active_landmarks if ldm not in used_ldm.get_removes()]
        # print(self.active_landmarks)
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
        print([l.name for l in last.get_removes()])
        self.active_landmarks = [ldm for ldm in self.active_landmarks if ldm not in last.get_triggers()]
        self.active_landmarks.extend(last.get_removes())
        self.active_landmarks.append(last)

        print(last.get_removes())
        print(self.active_landmarks)
        list_to_imaginal(self.active_landmarks)
        return True

    def run(self, time=10):

        actr.goal_focus('start')
        actr.run(time)
