from classes import Klasse
from stats import Stats

class Char():
    def __init__(self,**kwargs):
        
        name=kwargs.get('name')
        if name:
            self.name=name
        else:
            self.name='unnamed'

        klasses=kwargs.get('classes')
        self.klasses=[]
        for klasse in klasses:
            if isinstance(klasse,Klasse):
                klasse.owner=self
                self.klasses.append(klasse)
            elif type(klasse)==dict:
                klasse=Klasse.from_json(klasse)
                klasse.owner=self
                self.klasses.append(klasse)
            elif type(klasse)==str:
                klasse=Klasse.from_str(klasse)
                if klasse:
                    klasse.owner=self
                    self.klasses.append(klasse)
                else:
                    raise ValueError

        stats=kwargs.get('stats')
        if type(stats)==Stats:
            self.stats=stats
        elif type(stats)==dict:
            self.stats=Stats.from_json(stats)
        else:
            self.stats=Stats(10,10,10,10,10,10)
    
    def to_json(self):
        data={}
        if hasattr(self,'name'):
            data['name']=self.name
        if hasattr(self,'klasse'):
            data['class']=[klasse.to_json() for klasse in self.klasses]
        if hasattr(self,'stats'):
            data['stats']=self.stats.to_json()

        return data
