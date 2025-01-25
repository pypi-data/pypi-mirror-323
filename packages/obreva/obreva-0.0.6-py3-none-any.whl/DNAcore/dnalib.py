parameters = [
            'hp','maxhp','mana','maxmana','iq','brutal','libido','beauty','atk','def','true_atk','true_def','absorb','mana_atk','mana_def','armor','weight','luck','wisdom'
                ]
class dna_class():
    name = 'A'
    usage = {
            #'<par>':<par_bonus>,
            }
    def __repr__(d):
        return f"<dna:{d.name}>"
    def check(d,letter):
        a = letter.upper()
        b = d.name.upper()
        if a in b or b in a:return True
        return False
    def __init__(d,name,usage):
        d.usage=usage
        d.name = name
sbp = dna_class
dna = [
        sbp('A',{})
        ]
