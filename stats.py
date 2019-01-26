
class Stats():
    def __init__(self,STR,DEX,CON,INT,WIS,CHA):
        self.STR=STR
        self.DEX=DEX
        self.CON=CON
        self.INT=INT
        self.WIS=WIS
        self.CHA=CHA

    def to_json(self):
        data={
            'STR':self.STR,
            'DEX':self.DEX,
            'CON':self.CON,
            'INT':self.INT,
            'WIS':self.WIS,
            'CHA':self.CHA
        }
        return data
        
    @staticmethod
    def from_json(data):
        STR=data.get('STR')
        DEX=data.get('DEX')
        CON=data.get('CON')
        INT=data.get('INT')
        WIS=data.get('WIS')
        CHA=data.get('CHA')
        return Stats(STR,DEX,CON,INT,WIS,CHA)

    @property
    def strmod(self):
        return (self.STR-10)//2
    @property
    def dexmod(self):
        return (self.DEX-10)//2
    @property
    def conmod(self):
        return (self.CON-10)//2
    @property
    def intmod(self):
        return (self.INT-10)//2
    @property
    def wismod(self):
        return (self.WIS-10)//2
    @property
    def chamod(self):
        return (self.CHA-10)//2