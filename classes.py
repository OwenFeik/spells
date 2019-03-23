import constants

class Klasse():
    def __init__(self,level=1):
        self.level=level
        self.owner=None

    @staticmethod
    def klasse_list():
        return ['cleric','sorcerer']

    @staticmethod
    def from_json(data,sb=None):
        klasse=data.pop('class')
        
        if klasse in ['Cleric','cleric']:
            return Cleric.from_json(data,sb)
        elif klasse in ['Sorcerer','sorcerer']:
            return Sorcerer.from_json(data,sb)

    @staticmethod
    def from_str(klasse):
        if klasse=='Cleric' or klasse=='cleric':
            return Cleric()
        elif klasse=='Sorcerer' or klasse=='sorcerer':
            return Sorcerer()
        else:
            return None

class Cleric(Klasse):
    def __init__(self,level=1,prepared=None,cantrips=None,slots_used=None):
        Klasse.__init__(self,level)
        self.klasse='cleric'
        self.prepared=[] if prepared is None else prepared
        self.cantrips=[] if cantrips is None else cantrips

        self.slots=constants.spellslots[self.level]
        self.slots_used=slots_used if slots_used is not None else [0]*9

    @property
    def spells(self):
        spells=self.cantrips[:]
        spells.extend(self.prepared)
        return spells

    def has_spell_slot(self,level):
        if level==0:
            return True
        if self.slots_used[level-1]<self.slots[level-1]:
            return True
        else:
            return False

    def prepare_spell(self,spell):
        if spell.level==0:
            if spell in self.cantrips:
                self.cantrips.remove(spell)
                print(f'Forgot the cantrip {spell.name}.')
            else:
                self.cantrips.append(spell)
                print(f'Learnt the cantrip {spell.name}.')
        elif spell in self.prepared:
            self.prepared.remove(spell)
            print(f'Removed {spell.name} from prepared.')
        else:
            self.prepared.append(spell)
            print(f'Prepared {spell.name}.')

    def cast_spell(self,spell):
        if spell in self.prepared:
            if self.has_spell_slot(spell.level):
                self.slots_used[spell.level-1]+=1
                print(f'You cast {spell.name}. {self.slots[spell.level-1]-self.slots_used[spell.level-1]} level {spell.level} slots remaining.')
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
            'prepared':sorted([spell.name for spell in self.prepared]),
            'cantrips':sorted([spell.name for spell in self.cantrips]),
            'slots_used':self.slots_used
        }

    @staticmethod
    def from_json(data,sb=None):
        if sb:
            level=data.get('level')
            prepared=[sb.get_spell(spell) for spell in data.get('prepared')]
            cantrips=[sb.get_spell(spell) for spell in data.get('cantrips')]
            slots_used=data.get('slots_used')
        else:
            level=data.get('level')
            prepared=[]
            cantrips=[]
            slots_used=data.get('slots_used')

        return Cleric(level,prepared,cantrips,slots_used)

class Sorcerer(Klasse):
    def __init__(self,level=1,spells=None,slots_used=None,sorcery_points_used=0):
        Klasse.__init__(self,level)
        self.klasse='sorcerer'
        self.spells=[] if spells is None else spells
        self.slots=constants.spellslots[self.level]
        self.slots_used=slots_used if slots_used is not None else [0]*9
        self.sorcery_points_max=self.level if self.level>1 else 0
        self.sorcery_points_used=sorcery_points_used

    def prepare_spell(self,spell):
        if spell in self.spells:
            self.spells.remove(spell)
            print(f'Forgot the spell {spell.name}.')
        else:
            self.spells.append(spell)
            print(f'Learnt the spell {spell.name}.')

    def has_spell_slot(self,level):
        if level==0:
            return True
        if self.slots_used[level-1]<self.slots[level-1]:
            return True
        else:
            return False

    def cast_spell(self,spell):
        if spell in self.spells:
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
    
    def convert_spell_slots(self,level):
        if self.has_spell_slot(level):
            if self.sorcery_points_used-level>=0:
                self.sorcery_points_used-=level
            else:
                self.sorcery_points_used=0
            self.slots_used[level-1]+=1
            print(f'Converted a level {level} slot. {self.sorcery_points_max-self.sorcery_points_used}/{self.sorcery_points_max} points available. {self.slots[level-1]-self.slots_used[level-1]} level {level} slots remaining.')
        else:
            print(f'No spell slot of level {level} available.')

    def handle_special_action(self,args):
        command=args[0]

        if command=='spend':
            arg=int(args[1])
            self.spend_sorcery_points(arg)
        elif command=='make':
            arg=int(args[1])
            self.convert_spell_slots(arg)
        elif command=='points':
            print(f'Currently have {self.sorcery_points_max-self.sorcery_points_used}/{self.sorcery_points_max} sorcery points.')
        else:
            print('That command is not available. Sorcerer commands: "spend", "make", "points".')

    def long_rest(self):
        self.slots_used=[0]*9
        self.sorcery_points_used=0

    def to_json(self):
        return {
            'class':self.klasse,
            'level':self.level,
            'spells':sorted([spell.name for spell in self.spells]),
            'slots_used':self.slots_used,
            'sorcery_points_used':self.sorcery_points_used
        }

    @staticmethod
    def from_json(data,sb=None):
        if sb:
            spells=[sb.get_spell(spell) for spell in data.get('spells')]            
        else:
            spells=[]
            
        level=data.get('level')
        slots_used=data.get('slots_used')
        sorcery_points_used=data.get('sorcery_points_used')

        return Sorcerer(level,spells,slots_used,sorcery_points_used)
