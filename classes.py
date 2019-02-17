import dataloaders

class Klasse():
    def __init__(self,level=1):
        self.level=level
        self.owner=None

    def prepare_spell(self,*args): # Overridden by classes that prepare spells
        print('This class can\'t prepare spells!')

    def cast_spell(self,*args): # Overridden by spellcasting classes
        print('This class can\'t cast spells!')

    def spend_sorcery_points(self,*args): # Overriden by sorcerer
        print('Only Sorcerers have sorcery points.')

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

        self.slots=dataloaders.get_spellslots('cleric',self.level)
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
    def __init__(self,level=1,spells=None,slots_used=[0]*9,sorcery_points_used=0):
        Klasse.__init__(self,level)
        self.klasse='sorcerer'
        self.spells=[] if spells is None else spells
        self.slots=dataloaders.get_spellslots('sorcerer',self.level)
        self.slots_used=slots_used
        self.sorcery_points_max=dataloaders.get_sorcery_points(self.level)
        self.sorcery_points_used=sorcery_points_used

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

    def spend_sorcery_points(self,points):
        if points<=self.sorcery_points_max-self.sorcery_points_used:
            self.sorcery_points_used+=points
            print(f'Spent {points} sorcery points. {self.sorcery_points_max-self.sorcery_points_used} points remaining.')
        else:
            print(f'Not enough sorcery points. Only {self.sorcery_points_max-self.sorcery_points_used} points remaining.')
    
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
