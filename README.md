# projet

http://lipas.uwasa.fi/~timan/sudoku/
lien des sudoku choisi

## Résoudre plusieurs Sudoku avec l'algorithme séquentiel
```bash
python single.py
```
## Résoudre plusieurs Sudoku avec l'algorithme parallèle
```bash
mpirun -np 10 python multi.py
```
## Alternative pour exécuter les deux avec un script *bash*
Exécute les deux commande ci-haut et donne le temps d'exécution.

**Note**: Le script contient une variable `pythonCommand` pour modifier `python3` par une autre version de *python*.
```bash
./start.sh
```