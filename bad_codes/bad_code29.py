"""
PROBLÈMES IDENTIFIÉS:
1. Noms cryptiques (fn, ln, em, ph)
2. Import non utilisé (json, re)
3. Fonction monolithique
4. Conditions imbriquées excessives
5. Duplication de validation
"""

# CODE 3: Validation de formulaire
import json
import re
from typing import Dict

def validate(fn, ln, em, ph):
    errors = {}
    if fn:
        if len(fn) < 2:
            errors['fn'] = 'trop court'
        else:
            if len(fn) > 50:
                errors['fn'] = 'trop long'
            else:
                if not fn.isalpha():
                    errors['fn'] = 'caractères invalides'
    else:
        errors['fn'] = 'requis'
    
    if ln:
        if len(ln) < 2:
            errors['ln'] = 'trop court'
        else:
            if len(ln) > 50:
                errors['ln'] = 'trop long'
            else:
                if not ln.isalpha():
                    errors['ln'] = 'caractères invalides'
    else:
        errors['ln'] = 'requis'
    
    return errors

