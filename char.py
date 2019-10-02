import constants
import cli

class Char():
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', '<no name>')
        self.klasses = kwargs.get('classes', [])
        self.caster_level = sum([int(k.get('caster') * k.get('level')) for k in self.klasses])
        self.spell_slots = constants.spellslots[self.caster_level]
        self.spell_slots_used = kwargs.get('spell_slots_used', [0] * 9)
        self.prepared = kwargs.get('prepared', [])
    
    def long_rest(self):
        for klasse in self.klasses:
            klasse.long_rest()

    def has_spell_slot(self,level):
        if level == 0:
            return True
        if self.spell_slots_used[level - 1] < self.spell_slots[level - 1]:
            return True
        else:
            return False

    def prepare_spell(self, spell):
        if spell in self.spells:
            self.spells.remove(spell)
            print(f'Forgot the spell {spell.name}.')
        else:
            self.spells.append(spell)
            print(f'Learnt the spell {spell.name}.')
            
    def cast_spell(self,spell):
        if spell in self.prepared or cli.get_decision(f'{spell.name} isn\'t prepared. Cast anyway?'):
            if self.has_spell_slot(spell.level) or cli.get_decision(f'No level {spell.level} slots available. Cast anyway?'):
                self.slots_used[spell.level - 1] += 1
                print(f'You cast {spell.name}. {self.spell_slots[spell.level - 1] - self.spell_slots_used[spell.level - 1]} level {spell.level} slots remaining.') 
        elif spell.level==0:
            pass
        else:
            print(f'{spell.name} not prepared.')
                    
    def level_up(self, klasse = None):
        if cli.get_decision('Add level to already present class?'):
            klasse = cli.get_choice('In which class was a level gained?', [k['name'] for k in self.klasses])
            [k for k in self.klasses if k.name == klasse][0]['level'] += 1
        else:
            klasse = input('In which class was a level gained? > ')
            if klasse in constants.caster_types:
                self.klasses.append({
                    'name': klasse,
                    'level': 1,
                    'caster': constants.caster_types[klasse]
                })
            

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
        data = {
            'name': input('What is you character\'s name? > '),
            'classes': []
        }

        classes_done = False
        prompt = 'Enter your character\'s classes and levels: <class> <level> <class> <level> '
        while not classes_done:
            inpt = cli.get_input(prompt)
            if len(inpt) % 2 == 0 and len(inpt) != 0:
                for i in range(0, len(inpt), 2):
                    if inpt[i] not in constants.caster_types:
                        caster_type = input(f'Class {inpt[i]} not found. Is this class a full, half or non caster? > ')
                        if input(f'Confirm class {inpt[i]} ({caster_type} caster) (y/n) > ').strip() != 'y':
                            prompt = 'Enter your character\'s classes and levels: <class> <level> <class> <level> '
                            break
                    else:
                        caster_type = inpt[i]

                    if inpt[i + 1].isnumeric():
                        data['classes'].append({
                                'name': inpt[i], 
                                'level': int(inpt[i + 1]),
                                'caster': constants.caster_types[caster_type]
                            })
                    else:
                        prompt = 'Enter the characters classes and levels: e.g. "Cleric 1 wizard 2" > '
                else:
                    classes_done = True

            else:
                prompt = 'Enter the characters classes and levels: e.g. "Cleric 1 wizard 2" > '

        print(data)
