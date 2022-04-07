import actr


class Landmark:
    def __init__(self, name, piece, location, type):
        self.name = name
        self.piece = piece
        self.location = location
        self.type = type
        self.triggers = []
        self.removes = [self]
        self.chunk_def = [name, "isa", "landmark", "piece", self.piece, "location", self.location, "type", self.type]
        actr.add_dm(self.chunk_def)

    def add_triggers(self, tlist):
        self.triggers = tlist

    def add_removes(self, rlist):
        self.removes = rlist

    def get_triggers(self):
        return self.triggers

    def get_removes(self):
        return self.removes

    def is_involved(self, piece, location):
        if self.piece == piece and self.location==location:
            return True
        return False