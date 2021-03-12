import time
list_sudoku = []

#retourne le prochain élément égal à 0 (vide)
def getNextEmpty(sudoku):
    for i in range(len(sudoku)):
        for j in range(len(sudoku[0])):
            if sudoku[i][j] == 0:  
                return (i,j)
    
    return False

#retourne vrai ou faux selon la validité du sudoku
def is_valid(sudoku, num, row, col):
    #on regarde les colonnes vertical 9x1
    for i in range(len(sudoku)):
        if sudoku[i][col] == num:
            return False

    #on regarde les range horizontal 9x1
    for i in range(len(sudoku[0])):
        if sudoku[row][i] == num:
            return False
    
    #on regarde les boites 3x3
    for i in range((row // 3 ) * 3,(row // 3 ) * 3 + 3):
        for j in range((col // 3 ) * 3,(col // 3 ) * 3 + 3):
            if sudoku[i][j] == num:
                return False
    
    return True

#recursivement fait du backtracking en ajoutant les éléments 1-9 dans chaque case et lorsqu'une case n'est pas valide pour tout les nombre 1-9
#on recule en arrière jusqu'à ce qu'une case soit valide. On termine lorsqu'il n'y a plus de case vide.
def solveSudoku(sudoku):
    nextCell = getNextEmpty(sudoku)

    #si getNextEmpty retourne False on a terminé, tout les cell ne contiennent plus 0
    if nextCell == False:
        return True
    else:
        (row,col) = nextCell

    for num in range(1,10):
        if is_valid(sudoku, num, row, col):
            sudoku[row][col] = num

            if solveSudoku(sudoku):
                return True

            #si is_valid retourne faux on backtrack jusqu'à ce qu'il donne vrai
            sudoku[row][col] = 0

    return False
    
#boucle sur la liste de sudoku en entré et retourne les sudoku terminés    
def sudokuSolverS(sudokus):
    print("starting Single")
    for sudoku in sudokus:
        solveSudoku(sudoku)
        list_sudoku.append(sudoku)

    print("ending Single")
    return list_sudoku