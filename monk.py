import actr
import random

actr.load_act_r_model("ACT-R:tangram-solver;simple-model.lisp")


def create_landmark_entry(piece, location, type):
    ldm = {"piece": str.capitalize(piece), "location": str.capitalize(location), "type": str.capitalize(type)}
    return ldm


def dict_to_chunk_landmark(name, dict):
    chunk = [name, "isa", "landmark"]
    for k in dict.keys():
        chunk.append(k)
        chunk.append(dict.get(k))
    return chunk


def monk_puzzle():
    def update_state(list):
        for lkey in state_dict.keys():
            ldm = state_dict.get(lkey)
            if ldm.get("piece") == list[0] and ldm.get("location") == list[1]:
                print("FOUND")
                break
        del state_dict[lkey]

        state_def = ['isa', 'puzzle-state']
        for landmark in state_dict.keys():
            state_def.append(landmark)
            state_def.append(landmark)
        print(state_def)
        imaginal_update = actr.define_chunks(state_def)
        actr.set_buffer_chunk('imaginal', imaginal_start)
        #actr.set_buffer_chunk('imaginal',actr.define_chunks(state_def))
        #return actr.define_chunks(state_def)
        return True

    actr.reset()
    actr.add_command("update-state",update_state)
    # this will be the python representation
    state_dict = {"landmark1": create_landmark_entry("small-triangle", "head", "simple"),
                  "landmark2": create_landmark_entry("square", "head", "simple"),
                  "landmark3": create_landmark_entry("parallelogram", "arm", "simple"),
                  "landmark4": create_landmark_entry("small-triangle", "foot", "simple"),
                  "landmark5": create_landmark_entry("nil", "body", "complex")}

    state_def = ['isa', 'puzzle-state']
    for landmark in state_dict.keys():
        # ldm_chunk = actr.define_chunks(dict_to_chunk_landmark(landmark,state_dict.get(landmark)))
        actr.add_dm(dict_to_chunk_landmark(landmark, state_dict.get(landmark)))

        state_def.append(landmark)
        state_def.append(landmark)
    #    print()

    imaginal_start = actr.define_chunks(state_def)
    actr.set_buffer_chunk('imaginal', imaginal_start)
    actr.add_dm(['start', 'isa', 'goal', 'state', 'choose-landmark'])
    actr.goal_focus('start')
    # actr.run(10)
    return


if __name__ == "__main__":
    monk_puzzle()
