from mpi4py import MPI
import time
from utils import getSudoku, write_sudoku
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
status=MPI.Status()
filenameMulti = "outputMulti.txt"

#retourne le prochain element egal a 0 (vide)
def getNextEmpty(sudoku):
    for i in range(len(sudoku)):
        for j in range(len(sudoku[0])):
            if sudoku[i][j] == 0:  
                return (i,j) 

    return False



#retourne vrai ou faux selon la validite du sudoku
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



#recursivement fait du backtracking en ajoutant les elements 1-9 dans chaque case et lorsqu'une case n'est pas valide pour tout les nombre 1-9
#on recule en arriere jusqu'a ce qu'une case soit valide. On termine lorsqu'il n'y a plus de case vide.

def solveSudoku(sudoku):
    nextCell = getNextEmpty(sudoku)
    while nextCell != False:
        #si getNextEmpty retourne False on a termine, tout les cell ne contiennent plus 0
        if nextCell == False:
            return sudoku
        else:
            (row,col) = nextCell 

        for num in range(1,10):
            comm.send(sudoku, dest=num, tag =num)
            comm.send((row,col), dest=num, tag =num)
    
    
        listPcs = list(range(1,10))
        found = False
        while len(listPcs) > 1:
            for i in listPcs:
                if comm.Iprobe(source=i,tag=99):
                    comm.recv(source=i,tag=99)
                    listPcs.remove(i)
                elif comm.Iprobe(source=listPcs[0],tag=200):
                    sudoku = comm.recv(source=listPcs[0],tag=200)
                    found = True
                    listPcs= []
                    break

        if found == True:
            break

        if comm.Iprobe(source=listPcs[0],tag=200):
            sudoku = comm.recv(source=listPcs[0],tag=200)
            break

        #envoie au dernier pcs qui travaille et le restart avec 9 pcs
        comm.send(None,dest=listPcs[0],tag=101)
                
        sudoku[row][col] = listPcs[0]
        
        nextCell = getNextEmpty(sudoku)

    return sudoku

def solveMulti(sudoku):
    if comm.Iprobe(source = 0, tag=101):
        comm.recv(source=0,tag=101)
        return True
    nextCell = getNextEmpty(sudoku)

    if nextCell == False:
        comm.send(sudoku,dest=0,tag=200)
        return True
    else:
        (row,col) = nextCell

    for num in range(1,10):
        if is_valid(sudoku, num, row, col):
            sudoku[row][col] = num

            if solveMulti(sudoku):
                return True

            #si is_valid retourne faux on backtrack jusqu'a ce qu'il donne vrai
            sudoku[row][col] = 0

    return False

#master
if rank == 0:
    list_sudoku = []
    sudokus = getSudoku(filenameMulti)
    print("starting Multi")
    tStart = time.time()
    
    for sudoku in sudokus:
        s = solveSudoku(sudoku)
        list_sudoku.append(s)
        print("Sudoku Done")

    tEnd = time.time()
    finalTime = tEnd - tStart
    print("ending Multi")

    for i in range(1,10):
        print("killing worker : " + str(i))
        comm.send("kill", dest = i, tag=i)

    with open(filenameMulti, 'a') as f:
        f.write("Temps : "+ str(finalTime) +"\n")

    for current_sudoku in list_sudoku :
        write_sudoku(current_sudoku,filenameMulti)

#workers
elif rank > 0:
    while True:
        sudoku = comm.recv(source=0, tag=rank)

        if sudoku == "kill":
            break

        (row,col) = comm.recv(source=0,tag=rank)

        if is_valid(sudoku, rank, row, col):
            sudoku[row][col] = rank
            result = solveMulti(sudoku)

            if result == False:
                comm.send(None,dest=0,tag=99)
        else:
            comm.send(None, dest=0, tag=99)