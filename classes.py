from dataloaders import get_spellslots

class Klasse():
    def __init__(self,level=1):
        self.level=level
        self.owner=None

    def prepare_spell(self,spell): # Overridden by classes that prepare spells
        print('This class can\'t prepare spells!')

    def cast_spell(self,spell): # Overridden by spellcasting classes
        print('This class can\'t cast spells!')

    @staticmethod
    def from_json(data):
        klasse=data.pop('class')
        if klasse=='Cleric' or klasse=='cleric':
            return Cleric.from_json(data)
    
    @staticmethod
    def from_str(klasse):
        if klasse=='Cleric' or klasse=='cleric':
            return Cleric()
        else:
            return None

class Cleric(Klasse):
    def __init__(self,level=1,prepared=None,cantrips=None,slots_used=[0]*9):
        Klasse.__init__(self,level)
        self.klasse='cleric'
        self.prepared=[] if prepared is None else prepared
        self.cantrips=[] if cantrips is None else cantrips

        self.slots=get_spellslots('cleric',self.level)
        self.slots_used=slots_used

    def prepare_spell(self,spell):
        if spell.level==0:
            if spell.name in self.cantrips:
                self.cantrips.remove(spell.name)
            else:
                self.cantrips.append(spell.name)
        elif spell.name in self.prepared:
            self.prepared.remove(spell.name)
        else:
            self.prepared.append(spell.name)

    def cast_spell(self,spell):
        if spell.name in self.prepared:
            if self.slots_used[spell.level]<self.slots[spell.level]:
                self.slots_used[spell.level]+=1
                print(f'You cast {spell.name}.')
            else:
                print(f'No level {spell.level} slots available.')
        elif spell.level==0:
            pass
        else:
            print(f'{spell.name} not prepared.')

    def long_rest(self):
        self.slots_used=[0]*9

    def to_json(self):
        return {
            'class':self.klasse,
            'level':self.level,
            'prepared':self.prepared,
            'cantrips':self.cantrips,
            'slots_used':self.slots_used
        }

    @staticmethod
    def from_json(data):
        level=data.get('level')
        prepared=data.get('prepared')
        cantrips=data.get('cantrips')
        slots_used=data.get('slots_used')

        return Cleric(level,prepared,cantrips,slots_used)

class Sorcerer(Klasse):
    def __init__(self,level=1,spells=None,slots_used=[0]*9):
        Klasse.__init__(self,level)
        self.klasse='sorcerer'
        self.spells=[] if spells is None else spells
        self.slots=get_spellslots('sorcerer',self.level)
        self.slots_used=slots_used

    def cast_spell(self,spell):
        if spell.name in self.spells:
            if spell.level==0:
                print(f'You cast {spell.name}.')
            if self.slots_used[spell.level-1]<self.slots[spell.level-1]:
                self.slots_used[spell.level-1]+=1
                print(f'You cast {spell.name}. {self.slots[spell.level-1]-self.slots_used[spell.level-1]} level {spell.level} slots remaining.')
            else:
                print(f'No level {spell.level} slots available.')
        else:
            print(f'{self.owner.name} doesn\'t know {spell.name}.')

    def long_rest(self):
        self.slots_used=[0]*9

    def to_json(self):
        return {
            'class':self.klasse,
            'level':self.level,
            'spells':self.spells,
            'slots_used':self.slots_used
        }

    @staticmethod
    def from_json(data):
        level=data.get('level')
        spells=data.get('spells')
        slots_used=data.get('slots_used')

        return Sorcerer(level,spells,slots_used)
