
class Char():
    def __init__(self,name='temp',prepared=[]):
        self.name=name
        self.prepared=prepared

    def prepare_spell(self,spell):
        if spell.name in self.prepared:
            self.prepared.remove(spell.name)
        else:
            self.prepared.append(spell.name)

    def to_json(self):
        return {
            'name': self.name,
            'prepared': self.prepared
        }

    @staticmethod
    def from_json(data):
        name=data.get('name')
        prepared=data.get('prepared')

        return Char(name,prepared)
