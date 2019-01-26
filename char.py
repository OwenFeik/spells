from classes import Klasse
from stats import Stats

class Char():
    def __init__(self,**kwargs):
        
        name=kwargs.get('name')
        self.name=name

        klasse=kwargs.get('class')
        if not klasse:
            raise ValueError
        elif isinstance(klasse,Klasse):
            klasse.owner=self
            self.klasse=klasse
        elif type(klasse)==dict:
            klasse=Klasse.from_json(klasse)
            klasse.owner=self
            self.klasse=klasse
        elif type(klasse)==str:
            klasse=Klasse.from_str(klasse)
            if klasse:
                klasse.owner=self
                self.klasse=klasse
            else:
                raise ValueError

        stats=kwargs.get('stats')
        if type(stats)==Stats:
            self.stats=stats
        elif type(stats)==dict:
            self.stats=Stats.from_json(stats)
    
    def to_json(self):
        data={}
        if hasattr(self,'name'):
            data['name']=self.name
        if hasattr(self,'klasse'):
            data['class']=self.klasse.to_json()
        if hasattr(self,'stats'):
            data['stats']=self.stats.to_json()

        return data
