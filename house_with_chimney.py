import actr
from landmark import Landmark
from puzzle import Puzzle, list_to_imaginal

def generate_house_with_chimney_landmarks():
    chimney = Landmark("SQ-CHIMNEY",'SQUARE','CHIMNEY','STRONG')
    roof_right = Landmark("BT-ROOF",'BIG-T','ROOF-RIGHT','STRONG')
    roof_left = Landmark("PG-ROOF",'PARALL','ROOF-LEFT','STRONG') #triggered by chimney and/or roof_right
    wall_up = Landmark("BIG-T-WALL-UP",'BIG-T','WALL-UP','WEAK')
    wall_down = Landmark('BIG-T-WALL-DOWN','BIG-T','WALL-DOWN','WEAK')

    #options for left point
    mid_t_left_point = Landmark('MID-T-LEFT-POINT', 'MEDIUM-T','LEFT-POINT','STRONG')
    small_t_left_point = Landmark('SMALL-T-LEFT-POINT','SMALL-T','LEFT-POINT','STRONG') #IS IT STRONG?
    small_t_left_comb_up = Landmark('SMALL-T-LEFT-COMB-UP', 'SMALL-T','LEFT-COMB','WEAK')
    small_t_left_comb_down = Landmark('SMALL-T-LEFT-COMB-DOWN','SMALL-T','LEFT-COMB','WEAK')

    # options for right point
    mid_t_right_point = Landmark('MID-T-RIGHT-POINT', 'MEDIUM-T', 'RIGHT-POINT', 'STRONG')
    small_t_right_point = Landmark('SMALL-T-RIGHT-POINT', 'SMALL-T', 'RIGHT-POINT', 'STRONG')  # IS IT STRONG?
    small_t_right_comb_up = Landmark('SMALL-T-RIGHT-COMB-UP', 'SMALL-T', 'RIGHT-COMB', 'WEAK')
    small_t_right_comb_down = Landmark('SMALL-T-RIGHT-COMB-DOWN', 'SMALL-T', 'RIGHT-COMB', 'WEAK')

    #rarer_but_happen
    big_t_low_left_corner = Landmark('BIG-T-LOW-LEFT','BIG-T','LOW-LEFT-CORNER','WEAK') #PROLLY NEED MEDIUM
    big_t_low_right_corner = Landmark('BIG-T-LOW-RIGHT','BIG-T','LOW-RIGHT-CORNER','WEAK')
    big_t_roof_left = Landmark('BIG-T-ROOF-LEFT','BIG-T','ROOF-LEFT', 'WEAK')
    small_t_chimney_high = Landmark('SMALL-T-CHIMNEY-HIGH','SMALL-T','CHIMNEY','WEAK') #PROBABLY WORKS
    small_t_chimney_low = Landmark('SMALL-T-CHIMNEY-LOW','SMALL-T','CHIMNEY','WEAK')

    #####triggers and removes
    chimney.add_removes([small_t_chimney_low,small_t_chimney_high])
    chimney.add_triggers([roof_left])
    roof_right.add_removes([big_t_low_right_corner,big_t_roof_left])
    roof_right.add_triggers([roof_left])
    roof_left.add_removes([big_t_roof_left,big_t_low_left_corner])

    ####
    wall_up.add_removes([wall_down, big_t_low_left_corner,big_t_low_right_corner])
    wall_up.add_triggers([mid_t_right_point,mid_t_left_point,small_t_right_point,small_t_left_point,small_t_right_comb_up,
                          small_t_right_comb_down,small_t_left_comb_down,small_t_left_comb_up])
    mid_t_left_point.add_removes([big_t_low_left_corner,big_t_roof_left,
                                  mid_t_right_point,small_t_left_point,small_t_left_comb_up,small_t_left_comb_down])
    mid_t_right_point.add_removes([big_t_low_right_corner,
                                   mid_t_left_point,small_t_right_point,small_t_right_comb_up,small_t_right_comb_down])
    #small_t_left_point.add_removes([small_t_right_comb_up,small_t_left_comb_down,mid_t_right_point])
    pass


class HouseWithChimney(Puzzle):
    def __init__(self, path= "ACT-R:tangram-solver;simple-model.lisp"):
        super().__init__(path)
        self.active_landmarks, self.unseen_landmarks = generate_house_with_chimney_landmarks()
        list_to_imaginal(self.active_landmarks)
