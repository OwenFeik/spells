from classes import Klasse
from stats import Stats
from utilities import clean_string

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
                if kwargs.get('sb'):
                    klasse=Klasse.from_json(klasse,kwargs.get('sb'))
                else:
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
    
        max_hp=kwargs.get('max_hp')
        if max_hp:
            if type(max_hp)==int:
                self.max_hp=max_hp
            else:
                raise ValueError
    
        current_hp=kwargs.get('current_hp')
        if current_hp:
            if type(current_hp)==int:
                self.current_hp=current_hp
            else:
                raise ValueError

    def has_class(self,klasse):
        klasse=klasse.lower()
        for kls in self.klasses:
            if kls.klasse==klasse:
                return kls
        return False
    
    def long_rest(self):
        for klasse in self.klasses:
            klasse.long_rest()
        if hasattr(self,'current_hp') and hasattr(self,'max_hp'):
            self.current_hp=self.max_hp

    def prepare_spell(self,spell,klasse=None):
        if not self.klasses:
            print(f'The character {self.name} can\'t prepare spells because it doesn\'t have a class!')
        elif klasse:
            for kls in self.klasses:
                if kls.klasse==klasse.lower():
                    kls.prepare_spell(spell)
                    break
        else:
            if len(self.klasses)==1 and hasattr(self.klasses[0],'prepare_spell'):
                self.klasses[0].prepare_spell(spell)
            elif len(self.klasses)==1:
                print(f'The class {self.klasses[0].klasse} can\'t cast spells')
            else:
                klasses=[kls.klasse for kls in self.klasses if hasattr(kls,'prepare_spell')]
                out=f'\nChoose a class to prepare {spell.name} with.\n'
                for i,kls in enumerate(klasses):
                    out+=f'\n[{i+1}] {kls}'
                print(out+'\n')

                return ('class',klasses,'prep',spell.name)
            
    def cast_spell(self,spell,klasse=None):
        if not self.klasses:
            print(f'The character {self.name} can\'t cast spells because it doesn\'t have a class!')
        elif klasse:
            for kls in self.klasses:
                if kls.klasse==klasse.lower():
                    kls.cast_spell(spell)
        else:
            if len(self.klasses)==1 and hasattr(self.klasses[0],'cast_spell'): 
                self.klasses[0].cast_spell(spell)
            elif len(self.klasses)==1:
                print(f'The class {self.klasses[0].klasse} can\'t cast spells')
            else:
                klasses=[kls.klasse.capitalize() for kls in self.klasses if hasattr(kls,'cast_spell')]
                out=f'Choose a class to cast {spell.name} with.\n'
                for i,kls in enumerate(klasses):
                    out+=f'\n[{i+1}] {kls}'
                print(out+'\n')

                return ('class',klasses,'cast',spell.name)
                    
    def to_json(self):
        data={}
        if hasattr(self,'name'):
            data['name']=self.name
        if hasattr(self,'klasses'):
            data['classes']=[klasse.to_json() for klasse in self.klasses]
        if hasattr(self,'stats'):
            data['stats']=self.stats.to_json()
        if hasattr(self,'max_hp'):
            data['max_hp']=self.max_hp
        if hasattr(self,'current_hp'):
            data['current_hp']=self.current_hp

        return data
    
    @staticmethod
    def from_json(data):
        return Char(**data)

    @staticmethod
    def from_wizard():
        prompt='What is you characters name? '
        current='name'
        data={}
        while True:
            # try:
            inpt=[clean_string(string) for string in input(f'{prompt}> ').split(' ') if string != '']
            
            if current=='name':
                data['name']=inpt[0]
                prompt='Enter your characters classes and levels: <class> <level> <class> <level> '
                current='class'
            elif current=='class':
                data['classes']=[]
                if len(inpt)%2==0 and not len(inpt)==0:
                    for i in range(0,int(len(inpt)/2)):
                        if inpt[2*i].lower() in Klasse.klasse_list():
                            if inpt[(2*i)+1].isnumeric():
                                data['classes'].append(Klasse.from_json({'class':inpt[2*i].lower(),'level':int(inpt[(2*i)+1])}))
                            else:
                                prompt='Enter the characters classes and levels: e.g. Cleric 1 wizard 2 '
                        else:
                            print(f'Class {inpt[2*i]} not available.')
                    break
                else:
                    prompt='Enter the characters classes and levels: e.g. Cleric 1 wizard 2'

        # except:
            # print('Inadmissable input.')

        return Char.from_json(data)
