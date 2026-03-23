"""
PROBLÈMES IDENTIFIÉS:
1. Noms de variables non descriptifs (x, y, z, a, b)
2. Importations inutilisées (random, datetime)
3. Fonction trop longue (calculate_stuff)
4. Complexité cyclomatique élevée (trop de if/else imbriqués)
5. Duplication de code (calculs répétés)
"""
import random
import datetime
from typing import List
def calculate_stuff(x, y, z):
    a = 0
    if x > 0:
        if y > 0:
            if z > 0:
                a = x + y + z
                b = a * 2
                c = b / 3
                d = c + 10
                e = d - 5
                f = e * 1.5
            else:
                a = x + y
                b = a * 2
                c = b / 3
                d = c + 10
                e = d - 5
                f = e * 1.5
        else:
            if z > 0:
                a = x + z
                b = a * 2
                c = b / 3
                d = c + 10
                e = d - 5
                f = e * 1.5
            else:
                a = x
                b = a * 2
                c = b / 3
                d = c + 10
                e = d - 5
                f = e * 1.5
    return f