import actr

saliency_dict = {'STRONG':3,'WEAK':1,'COMPOUND':2,'DERIVED':2}

class Landmark:
    """ Represent a perceived landmark, defined as an
    "interesting"placement of a tan

    Attributes:
        name: name of the landmark (and the chunk in actr)
        piece: the tan involved
        location: where the tan would be placed
        type: distinction simple/complex, will be used later to
            better define strategies
        triggers: other landmarks that will appear once this is chosen
        removes: other landmarks that are incompatible
        chunk_def: the string-list used to define the act-r chunk

    Methods:
        is_involved: returns true if the suggested placement corresponds
            to the landmark

    """
    def __init__(self, name, piece_type, location, type, add_to_dm = True):
        self.name = name
        self.piece_type = piece_type
        self.location = location
        self.type = type
        self.triggers = []
        self.removes = [self]
        self.chunk_def = [name, "isa", "landmark", "piece-type", self.piece_type, "location", self.location, "type", self.type]
        if add_to_dm:
            actr.add_dm(self.chunk_def)
        actr.set_base_levels([name, saliency_dict.get(self.type)])

    def add_triggers(self, tlist):
        self.triggers = tlist

    def add_removes(self, rlist):
        self.removes = rlist

    def get_triggers(self):
        return self.triggers

    def get_removes(self):
        return self.removes

    def is_involved(self, piece, location):

        if self.piece_type == piece and self.location==location:

            return True

        return False

    def get_saliency(self):

        return saliency_dict.get(self.type)
