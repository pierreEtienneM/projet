#https://github.com/pierreEtienneM/projet/
#https://stackoverflow.com/questions/21088420/mpi4py-send-recv-with-tag/22952258#22952258
#https://cse.buffalo.edu/faculty/miller/Courses/CSE633/Sankar-Spring-2014-CSE633.pdf

from mpi4py import MPI
from enum import Enum
from copy import deepcopy

from math import log

# % 2 = 0, SEND TO WORKER
# % 2 = 1, SEND TO ADMIN
class Tags(Enum):
    READY = 1
    KILL = 2
    POSSIBLE_VALUE = 4
    LONE_RANGER = 6
    ELIMINATION = 8
    TWIN = 10
    TRIPLET = 12

comm = MPI.COMM_WORLD
size = comm.size
rank = comm.rank
stts = MPI.Status()

class AdminUtils():    
    def executeProcess(sudokuBoard):
        binaryBoard = AdminUtils.convertBinary(sudokuBoard)
        
        redoSteps = True
        nbLoops = 0
        old = None
        new = None
        while redoSteps:

            #for callingIndex, calling in enumerate([AdminUtils.doPossibleValue, AdminUtils.doElimination, AdminUtils.doLoneRanger, AdminUtils.doTwin, AdminUtils.doNotReach]):#, AdminUtils.doTriplet]):
            for callingIndex, calling in enumerate([AdminUtils.doPossibleValue, AdminUtils.doElimination, AdminUtils.doLoneRanger, AdminUtils.doTwin, AdminUtils.doTriplet, AdminUtils.doNotReach]):
                backup, redoSteps = calling(binaryBoard)
                if redoSteps or callingIndex == 4:
                    old = deepcopy(new)
                    new = deepcopy(backup)
                    redoSteps = not new == old
                    print(callingIndex, calling, new == old)
                    print(old)
                    print(new)
                    if callingIndex == 4:
                        redoSteps = False
                    break
            
            nbLoops += 1
            if nbLoops == 2 ** 6 and not False:
                break
        
        print()
        print(AdminUtils.isSolved(binaryBoard), binaryBoard, nbLoops)
        print()

    def convertBinary(sudokuBoard):
        binaryBoard = [[0 for y in range(9)] for x in range(9)]

        for rowIndex, row in enumerate(sudokuBoard):
            for columnIndex, boxValue in enumerate(row):
                if boxValue > 0:
                    binaryBoard[rowIndex][columnIndex] = 2 ** boxValue + 1
        
        return binaryBoard

    def killWorkers():
        status = MPI.Status()

        for workerIndex in range(size - 1):
            comm.recv(source = MPI.ANY_SOURCE, tag = Tags.READY.value, status = status)
            comm.send(None, dest = status.Get_source(), tag = Tags.KILL.value)

    def doAlgorithm(binaryBoard, tag, lambdaFunc):
        status = MPI.Status()
        nbMessages = 0

        for rowIndex, row in enumerate(binaryBoard):
            for columnIndex, boxValue in enumerate(row):
                if boxValue % 2 == 0:
                    comm.recv(source = MPI.ANY_SOURCE, tag = Tags.READY.value, status = status)
                    source = status.Get_source()

                    _row = row
                    _column = [x[columnIndex] for x in binaryBoard]
                    
                    __square = [x[(columnIndex // 3 + 0) * 3 : (columnIndex // 3 + 1) * 3] for x in binaryBoard[(rowIndex // 3 + 0) * 3 : (rowIndex // 3 + 1) * 3]]
                    
                    _square = []
                    _square[0:3] = __square[0]
                    _square[3:6] = __square[1]
                    _square[6:9] = __square[2]

                    nbMessages += 1

                    comm.send(((rowIndex, columnIndex), (_row, _column, _square), (boxValue)), dest = source, tag = tag)

        changed = False
        for messageIndex in range(nbMessages):
            data = comm.recv(source = MPI.ANY_SOURCE, tag = tag + 1)
            if data[0]:
                changed = True
                lambdaFunc(binaryBoard, data[1:])
        
        return binaryBoard, changed

    def assignDirectly(binaryBoard, args):
        binaryBoard[args[1][0]][args[1][1]] = args[0]

    def doPossibleValue(binaryBoard):
        resultAlgorithm = AdminUtils.doAlgorithm(binaryBoard, Tags.POSSIBLE_VALUE.value, AdminUtils.assignDirectly)
        return resultAlgorithm

    def doElimination(binaryBoard):
        resultAlgorithm = AdminUtils.doAlgorithm(binaryBoard, Tags.ELIMINATION.value, AdminUtils.assignDirectly)
        return resultAlgorithm

    def doLoneRanger(binaryBoard):
        resultAlgorithm = AdminUtils.doAlgorithm(binaryBoard, Tags.LONE_RANGER.value, AdminUtils.assignDirectly)
        return resultAlgorithm

    def doTwin(binaryBoard):
        resultAlgorithm = AdminUtils.doAlgorithm(binaryBoard, Tags.TWIN.value, AdminUtils.assignDirectly)
        return resultAlgorithm

    def doTriplet(binaryBoard):
        resultAlgorithm = AdminUtils.doAlgorithm(binaryBoard, Tags.TRIPLET.value, AdminUtils.assignDirectly)
        return resultAlgorithm

    def doNotReach(binaryBoard):
        print("REACHED DONOTREACH")
        return binaryBoard, False

    def isSolved(binaryBoard):
        for row in binaryBoard:
            for box in row:
                if box % 2 == 0:
                    return False
        return True

class WorkerUtils():
    def executeProcess():
        workerAlive = True

        while workerAlive:
            WorkerUtils.sendReady()
            tag, task = WorkerUtils.receiveTask()

            taskReturn = None
            if tag == Tags.POSSIBLE_VALUE.value:
                taskReturn = WorkerUtils.doPossibleValue(task)
            elif tag == Tags.ELIMINATION.value:
                taskReturn = WorkerUtils.doElimination(task)
            elif tag == Tags.LONE_RANGER.value:
                taskReturn = WorkerUtils.doLoneRanger(task)
            elif tag == Tags.TWIN.value:
                taskReturn = WorkerUtils.doTwin(task)
            elif tag == Tags.TRIPLET.value:
                taskReturn = WorkerUtils.doTriplet(task)
            elif tag == Tags.KILL.value:
                workerAlive = False
            else:
                assert False, f"Tag ({tag}) not supported, exiting..."

            if tag != Tags.KILL.value:
                comm.send(taskReturn, dest = 0, tag = tag + 1)

    def sendReady():
        comm.send(None, dest = 0, tag = Tags.READY.value)

    def receiveTask():
        status = MPI.Status()
        task = comm.recv(source = 0, status = status)
        return (status.Get_tag(), task)

    def doPossibleValue(task):
        currentValue = 0
        nbFound = 0

        for power in range(1, 10):
            number = 2 ** power + 1

            found = False
            for columnIndex in range(9):
                if task[1][0][columnIndex] == number or task[1][1][columnIndex] == number or task[1][2][columnIndex] == number:
                    found = True
                    break
            
            if not found:
                nbFound += 1
                currentValue += 2 ** power

        needChange = task[2] == 0
        if not needChange:
            currentValue &= task[2]
            needChange = not currentValue == task[2]

        return (needChange, currentValue, task[0])

    def doElimination(task):
        isAlone = False
        newValue = task[2]
        for power in range(1, 10):
            number = 2 ** power
            if newValue == number:
                newValue += 1
                isAlone = True
                break
        
        return isAlone, newValue, task[0]

    def doLoneRanger(task):
        return WorkerUtils.doUpdatedTuple(task, 1)
        return WorkerUtils.doTuple(task, 1)
        isAlone = False
        currentValue = task[2]
        newValue = 0
        for power in range(1, 10):
            number = 2 ** power
            nbFind = [0, 0, 0]
            if currentValue > number and currentValue & number == number:
                for index in range(9):
                    for findIndex in range(3):
                        if task[1][findIndex][index] > number and task[1][findIndex][index] & number == number:
                            nbFind[findIndex] += 1
            if nbFind[0] == 1 or nbFind[1] == 1 or nbFind[2] == 1:
                newValue = number + 1
                break
        return newValue > 0, newValue, task[0]

    def doUpdatedTuple(task, toFind):
        newValue = 0
        updateValue = False
        #--
        unknowns = []
        for power in range(1, 10):
            number = 2 ** power
            if task[2] >= number and task[2] & number == number:
                unknowns.append([number, 0, 0, 0])
        #--
        for unknown in unknowns:
            for index in range(9):
                for findIndex in range(3):
                    if task[1][findIndex][index] >= unknown[0] and task[1][findIndex][index] & unknown[0] == unknown[0]:
                        unknown[1 + findIndex] += 1
        updateValue = not len(unknowns) == toFind
        #--
        realUnknowns = []
        for unknown in unknowns:
            if unknown[0] == toFind or unknown[1] == toFind or unknown[2] == toFind:
                realUnknowns.append(unknown)
        #--
        if len(realUnknowns) == toFind:
            for value in realUnknowns:
                newValue += value[0]
        else:
            newValue = task[2]

        #print(realUnknowns, toFind, task, newValue, unknowns)
        #return len(realUnknowns) == toFind, newValue, task[0]
        #return updateValue, newValue, task[0]
        #return len(realUnknowns) > 0, newValue, task[0]
        return not newValue == task[2], newValue, task[0]

    def doTuple(task, toFind):
        newValue = 0
        #--
        unknowns = []
        for power in range(1, 10):
            number = 2 ** power
            if task[2] >= number and task[2] & number == number:
                unknowns.append([number, 0, 0, 0])
        #--
        for unknown in unknowns:
            for index in range(9):
                for findIndex in range(3):
                    if task[1][findIndex][index] >= unknown[0] and task[1][findIndex][index] & unknown[0] == unknown[0]:
                        unknown[1 + findIndex] += 1
        #--
        realUnknown = []
        for unknown in unknowns:
            if unknown[1] == toFind or unknown[2] == toFind or unknown[3] == toFind:
                realUnknown.append(unknown)
        #--
        if len(realUnknown) != toFind:
            newValue = task[2]
        else:
            for unknown in realUnknown:
                newValue += unknown[0]

        return newValue != task[2], newValue, task[0]

    def doTwin(task):
        return WorkerUtils.doUpdatedTuple(task, 2)
        return WorkerUtils.doTuple(task, 2)

    def doTriplet(task):
        return WorkerUtils.doTuple(task, 3)


# ELIMINATION:
#   EX: (1,2) (3) (1,2) (2,4) -> (1,2) (3) (1,2) (2,4)
# LONE-RANGER:
#   EX: (1,2,3) (1,2,3) (1,2,4) (1,2,3) -> (1,2,3) (1,2,3) (4) (1,2,3)
# TWINS:
#   EX: (1,2,3) (1) (2,3,4) (4) -> (2,3) (1) (2,3) (4) # NOT VISIBLE
#   EX: (2,3) (2,3) (1,2) (4) -> (2,3) (2,3) (1) (4) # VISIBLE

# 0. POSSIBLE-VALUES
# 1. ELIMINATION
# 2. LONE-RANGER
# ((01)+2)+

def sudokuSolverM(sudokus):
    solved_sudokus = []
    if rank == 0:
        for sudoku in sudokus:
            AdminUtils.executeProcess(sudoku)
            #solved_sudokus.append(AdminUtils.execute(Sudoku(sudoku)))

        AdminUtils.killWorkers()
    else:
        WorkerUtils.executeProcess()
    
    return solved_sudokus
    
if __name__ == "__main__":
    with open('input.txt', 'r') as f:
        sudokus = []
        current_sudoku = []
        row = []
        for line in f:
            for num in line.split(','):
                if num != '\n':
                    row.append(int(num))
            if row != []:
                current_sudoku.append(row)
            if len(current_sudoku) == 9:
                sudokus.append(current_sudoku)
                current_sudoku = []
            row = []
        sudokuSolverM([sudokus[6]])
        #sudokuSolverM(sudokus[:6])