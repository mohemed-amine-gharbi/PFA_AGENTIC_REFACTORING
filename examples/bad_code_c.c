/*
PROBLÈMES IDENTIFIÉS:
1. Noms de variables non descriptifs (a, b, c, x, y)
2. Headers inutilisés (#include <math.h>, <time.h>)
3. Fonction trop longue avec multiples responsabilités
4. Complexité cyclomatique élevée (if/else imbriqués)
5. Duplication de code dans les calculs
*/

// CODE 1: Calcul de statistiques
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

int calc(int a, int b, int c) {
    int x = 0;
    if (a > 0) {
        if (b > 0) {
            if (c > 0) {
                x = a + b + c;
                x = x * 2;
                x = x / 3;
                x = x + 10;
            } else {
                x = a + b;
                x = x * 2;
                x = x / 3;
                x = x + 10;
            }
        } else {
            if (c > 0) {
                x = a + c;
                x = x * 2;
                x = x / 3;
                x = x + 10;
            }
        }
    }
    return x;
}