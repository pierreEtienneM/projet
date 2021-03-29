import csv, os, time, copy, sys

def write_sudoku(board,file):
    with open(file, 'a') as f:
        f.write("-"*25+"\n")
        for i, row in enumerate(board):
            f.write(("|" + " {} {} {} |"*3+"\n").format(*[x if x != 0 else " " for x in row]))
            if i == 8:
                f.write("-"*25+"\n")
            elif i % 3 == 2:
                f.write("|" + "---"*7 + "--|\n")


def getSudoku(file):
    if os.path.exists(file): os.remove(file)
    sudokus = []

    with open('input.txt', 'r') as f:
        current_sudoku = []
        row = []
        for line in f:
            if len(line) == 19:
                for num in line.split(','):
                    if num != '\n':
                        row.append(int(num))
                if row != []:
                    current_sudoku.append(row)
                if len(current_sudoku) == 9:
                    write_sudoku(current_sudoku,file)
                    sudokus.append(current_sudoku)
                    current_sudoku = []
                row = []
    return sudokus