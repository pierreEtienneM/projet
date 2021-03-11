import csv, os, time
from multi import *
from single import *

sudokus = []
filenameMulti = "outputMulti.txt"
filenameSingle = "outputSingle.txt"
def print_sudoku(board,file):
    with open(file, 'a') as f:
        f.write("-"*37+"\n")
        for i, row in enumerate(board):
            f.write(("|" + " {}   {}   {} |"*3+"\n").format(*[x if x != 0 else " " for x in row]))
            if i == 8:
                f.write("-"*37+"\n")
            elif i % 3 == 2:
                f.write("|" + "---+"*8 + "---|\n")
            else:
                f.write("|" + "   +"*8 + "   |\n")


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
            print_sudoku(current_sudoku,filenameMulti)
            print_sudoku(current_sudoku,filenameSingle)
            sudokus.append(current_sudoku)
            current_sudoku = []
        row = []

#multi
tStart = time.time()
finishedSudokus = sudokuSolverM(sudokus)
tEnd = time.time()
finalTime = tEnd - tStart
with open(filenameMulti, 'a') as f:
        f.write("Temps : "+ str(finalTime) +"\n")

for current_sudoku in finishedSudokus :
    print_sudoku(current_sudoku,filenameMulti)

#single
tStart = time.time()
finishedSudokus = sudokuSolverS(sudokus)
tEnd = time.time()
finalTime = tEnd - tStart
with open(filenameSingle, 'a') as f:
        f.write("Temps : "+ str(finalTime) +"\n")

for current_sudoku in finishedSudokus :
    print_sudoku(current_sudoku,filenameSingle)