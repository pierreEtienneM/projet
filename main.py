import csv, os, time, copy
from multi import *
from single import *
from mpi4py import MPI as mpi

comm = mpi.COMM_WORLD
size = comm.size
rank = comm.rank

sudokus = []
filenameMulti = "outputMulti.txt"
filenameSingle = "outputSingle.txt"
def write_sudoku(board,file):
    with open(file, 'a') as f:
        f.write("-"*25+"\n")
        for i, row in enumerate(board):
            f.write(("|" + " {} {} {} |"*3+"\n").format(*[x if x != 0 else " " for x in row]))
            if i == 8:
                f.write("-"*25+"\n")
            elif i % 3 == 2:
                f.write("|" + "---"*7 + "--|\n")

if rank == 0:
    if os.path.exists(filenameMulti): os.remove(filenameMulti)
    if os.path.exists(filenameSingle): os.remove(filenameSingle)
    with open('input.txt', 'r') as f:
        current_sudoku = []
        row = []
        for line in f:
            for num in line.split(','):
                if num != '\n':
                    row.append(int(num))
            if row != []:
                current_sudoku.append(row)
            if len(current_sudoku) == 9:
                write_sudoku(current_sudoku,filenameMulti)
                write_sudoku(current_sudoku,filenameSingle)
                sudokus.append(current_sudoku)
                current_sudoku = []
            row = []

#single
sudokusCopy = copy.deepcopy(sudokus)

if rank == 0:
    tStart = time.time()
    finishedSudokus = sudokuSolverS(sudokus)
    tEnd = time.time()
    finalTime = tEnd - tStart
    with open(filenameSingle, 'a') as f:
            f.write("Temps : "+ str(finalTime) +"\n")

    for current_sudoku in finishedSudokus :
        write_sudoku(current_sudoku,filenameSingle)

#multi
if rank == 0:
    tStart = time.time()

comm.barrier()

finishedSudokus = sudokuSolverM(sudokusCopy)

comm.barrier()

if rank == 0:
    tEnd = time.time()
    finalTime = tEnd - tStart
    with open(filenameMulti, 'a') as f:
            f.write("Temps : "+ str(finalTime) +"\n")

    for current_sudoku in finishedSudokus :
        write_sudoku(current_sudoku,filenameMulti)