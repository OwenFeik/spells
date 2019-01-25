from classes import Klasse

class Char():
    def __init__(self,klasse,name='temp'):
        if isinstance(klasse,Klasse):
            self.klasse=klasse
        elif type(klasse)==str:
            klasse=Klasse.from_str(klasse)
            if klasse:
                self.klasse=klasse
            else:
                raise ValueError
        self.name=name

    
    def to_json(self):
        return {
            'name': self.name,
            'class': self.klasse.to_json()
        }

    @staticmethod
    def from_json(data):
        name=data.get('name')
        klasse=Klasse.from_json(data.get('class'))

        return Char(klasse,name)
