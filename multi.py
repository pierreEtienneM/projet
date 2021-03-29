#https://github.com/pierreEtienneM/projet/
#https://stackoverflow.com/questions/21088420/mpi4py-send-recv-with-tag/22952258#22952258

from mpi4py import MPI
from enum import Enum
from copy import deepcopy

enum_p2BeginIndex = 10
enum_p3BeginIndex = 20

class Tags(Enum):
    READY = 1
    DONE = 2
    EXIT = 3
    START = 4
    # POSSIBLES VALUES
    NOTES = 5
    NOTES_FIN = 6
    NOTES_KILL = 7
    NOTES_VALIDATE = 8
    NOTES_VALIDATE_DONE = 9
    # LONE RANGERS
    READY_P2 = enum_p2BeginIndex + 0
    KILL_P2 = enum_p2BeginIndex + 1
    SEND_P2 = enum_p2BeginIndex + 2
    RECV_P2 = enum_p2BeginIndex + 3
    LAST_P2 = enum_p2BeginIndex + 4
    # TWINS
    READY_P3 = enum_p3BeginIndex + 0
    KILL_P3 = enum_p3BeginIndex + 1
    LAST_P3 = enum_p3BeginIndex + 2

assert Tags.READY_P3.value > Tags.LAST_P2.value

comm = MPI.COMM_WORLD
size = comm.size
rank = comm.rank
stts = MPI.Status()

# LONE RANGER
# TWINS
# TRIPLETS

def findLoneRanger():
    pass
def findTwins():
    pass
def findTriplets():
    pass

def printflush(message):
    print(message, flush=True)

def printbinarydoku(sudoku, printtype=None):
    for row in sudoku:
        countfixed = 0
        for cell in row:
            if cell % 2 == 1:
                countfixed += 1
                print(" {:3} ".format(cell), end=" ")
            else:
                print("({:3})".format(cell), end=" ")
        print("{}/9".format(countfixed))
    pass

def binaryku(sudoku):
    binarydoku = deepcopy(sudoku)

    for rowindex, row in enumerate(sudoku):
        for colindex, cell in enumerate(row):
            if cell > 0:
                binarydoku[rowindex][colindex] = 2**cell + 1

    return binarydoku

def adminProcess(sudoku): # rank == 0

    binary = binaryku(sudoku)

    # PART 1: POSSIBLE VALUES
    printflush(binary)
    nbzeros = 0
    for rowindex, row in enumerate(binary):
        for colindex, cell in enumerate(row):
            if cell == 0:
                comm.recv(source=MPI.ANY_SOURCE, tag=Tags.READY.value, status=stts)
                source = stts.Get_source()

                p1_box = [row[(colindex//3+0)*3:(colindex//3+1)*3] for row in binary[(rowindex//3+0)*3:(rowindex//3+1)*3]]
                p1_column = [row[colindex] for row in binary]
                p1_package = [p1_box, row, p1_column, (rowindex, colindex)]
                
                comm.send(p1_package, dest=source, tag=Tags.NOTES.value)
                nbzeros += 1
    
    # PART 1: RECEIVE DATA FROM WORKERS
    for i in range(nbzeros):
        dataP1 = comm.recv(source=MPI.ANY_SOURCE, tag=Tags.NOTES_FIN.value, status=stts)
        source = stts.Get_source()
        binary[dataP1[0][0]][dataP1[0][1]] = dataP1[1]
    
    # PART 1: VALIDATE DATA: ROWS, COLUMNS AND BOXES
    redosteps = True
    while redosteps:
        sendedmessage = 0
        for rowindex, row in enumerate(binary):
            comm.recv(source=MPI.ANY_SOURCE, tag=Tags.READY.value, status=stts)
            comm.send([rowindex, row, 1], dest=stts.Get_source(), tag=Tags.NOTES_VALIDATE.value)
            # --
            comm.recv(source=MPI.ANY_SOURCE, tag=Tags.READY.value, status=stts)
            comm.send([rowindex, [rv[rowindex] for rv in binary], 2], dest=stts.Get_source(), tag=Tags.NOTES_VALIDATE.value)
            sendedmessage += 2
            # --
            if rowindex // 3 == 0:
                sendedmessage += 3
                for colindex in range(0,9,3):
                    comm.recv(source=MPI.ANY_SOURCE, tag=Tags.READY.value, status=stts)
                    subbox = [rv[colindex:colindex+3] for rv in binary[(rowindex+0)*3:(rowindex+1)*3]]
                    box = []
                    box[0:3] = subbox[0]
                    box[3:6] = subbox[1]
                    box[6:9] = subbox[2]
                    comm.send([((rowindex+0)*3,colindex), box, 3], dest=stts.Get_source(), tag=Tags.NOTES_VALIDATE.value)

        redosteps = False
        # PART 1: VERIFY IF WE NEED TO REDO STEPS
        for indexmessage in range(sendedmessage):
            data = comm.recv(source=MPI.ANY_SOURCE, tag=Tags.NOTES_VALIDATE_DONE.value, status=stts)
            if data[0] == True: # we will need to redo the steps
                redosteps = True
                print("HERE------")
                if data[3] == 1:
                    binary[data[1]] = data[2]
                elif data[3] == 2:
                    for i in range(9):
                        binary[i][data[1]] = data[2][i]
                else:# data[3] == 3:
                    for i in range(9):
                        binary[data[1][0]+(i//3)][data[1][1]+(i%3)] = data[2][i]

        if redosteps:
            continue

        #########
        ## PART 2: LONE RANGERS
        #########
        # ONE VALUE POSSIBLE HIDDEN WITH MULTIPLE VALUES

        # SEND ROWS, COLUMS AND BOXES
        for i in range(9):
            # ROWS
            comm.recv(source=MPI.ANY_SOURCE, tag=Tags.READY.value, status=stts)
            row = binary[i]
            comm.send([row, i, 1], dest=stts.Get_source(), tag=Tags.SEND_P2.value)
            
            # COLUMNS
            comm.recv(source=MPI.ANY_SOURCE, tag=Tags.READY.value, status=stts)
            col = [row[i] for row in binary]
            comm.send([col, i, 2], dest=stts.Get_source(), tag=Tags.SEND_P2.value)
            
            # BOXES
            comm.recv(source=MPI.ANY_SOURCE, tag=Tags.READY.value, status=stts)
            subbox = [row[(i%3+0)*3:(i%3+1)*3] for row in binary[(i//3+0)*3:(i//3+1)*3]]
            box = []
            box[0:3] = subbox[0]
            box[3:6] = subbox[1]
            box[6:9] = subbox[2]
            comm.send([box, (i//3,i%3), 3], dest=stts.Get_source(), tag=Tags.SEND_P2.value)

        # RECEIVE DATA
        
        printflush(("BEFORE", binary))

        for i in range(9*3):
            data = comm.recv(source=MPI.ANY_SOURCE, tag=Tags.RECV_P2.value, status=stts)
            
            if data[2] == True:
                redosteps = True
                
                print(data)
                for update in data[3]:
                    if data[1] == 1:
                        binary[data[0]][update[0]] = update[1]
                    elif data[1] == 2:
                        binary[update[0]][data[0]] = update[1]
                    else:
                        binary[data[0][0]*3+update[0]//3][data[0][1]*3+update[0]%3] = update[1]

        printflush(("AFTER-", binary))
        printbinarydoku(binary)
        #printflush("looop")

        #########
        ## PART 2: END
        #########




    #printflush(binary)

    stillalive = size - 1
    while stillalive > 0:
        comm.recv(source=MPI.ANY_SOURCE, tag=Tags.READY.value, status=stts)
        comm.send(None, dest=stts.Get_source(), tag=Tags.NOTES_KILL.value)
        stillalive -= 1

    # PART 2: LONE RANGER
    # (UN CHIFFRE QUI NE PEUT ETRE QU'A UNE SEULE PLACE)
    # P2


    stillalive = size - 1
    stillalive = 0
    while stillalive > 0:
        comm.recv(source=MPI.ANY_SOURCE, tag=Tags.READY.value, status=stts)
        comm.send(None, dest=stts.Get_source(), tag=Tags.EXIT.value)
        stillalive -= 1


def workerProcess(): # rank != 0
    def workerNotes(box, row, col, pos):
        boxpos = (pos[0]%3,pos[1]%3)
        currentBox = box[boxpos[0]][boxpos[1]]
        
        nb = 0
        for i in range(1,10):
            num = 2**i+1

            found = False
            for j in range(9):
                if num == row[j] or num == col[j] or num == box[j%3][j//3]:
                    found = True
                    break

            if not found:
                nb += 1
                currentBox += (num - 1)
            
        if nb == 1:
            currentBox += 1
        
        return (pos, currentBox)
    def workerValidateNote(row):
        # 1. trouver les nombre fixes
        # 2. bitwise or pour enlever des notes
        # 3. bitwise and pour trouver les puissance de 2
        # 4. recommencer tant qu'il y a un changement
        
        fixednumber = []
        originalnotes = []
        for numberindex, number in enumerate(row):
            if number % 2 == 1:
                fixednumber.append([number, numberindex])
            else:
                originalnotes.append([number, numberindex])

        #printflush((1,fixednumber, originalnotes))
        gotchanged, gotchangedonce = True, False
        
        while gotchanged:
            gotchanged = False
            for noteindex, note in enumerate(originalnotes):
                for fixed in fixednumber:
                    if note[0] >= fixed[0] and note[0] | fixed[0] == note[0]:
                        updatednote = originalnotes[noteindex][0] | fixed[0]
                        originalnotes[noteindex][0] = updatednote
                        gotchanged = True
                        gotchangedonce = True
                        if updatednote > 0 and updatednote & (updatednote - 1) == 0:
                            fixednumber.append(originalnotes[noteindex])
                        break
                if gotchanged:
                    break
        if not gotchangedonce:
            return (gotchangedonce, row)
        else:
            newrow = []
            for x in originalnotes:
                newrow[x[1]] = x[0]
            for x in fixednumber:
                newrow[x[1]] = x[0]
            printflush(("IT HAPPENED-----------------", row, newrow, originalnotes, fixednumber))
            return (gotchangedonce, newrow)
    def workerFindLR(row):
        # trouve un nombre et compte combien de fois il le trouve dans la ligne
        # si == 1, lone ranger
        # recommencer car possible davoir plus que un ou que un lone ranger
        # donne un autre lone ranger

        foundlr = False
        newrow = deepcopy(row)
        reloop = True
        lrindex = []

        while reloop:
            reloop = False
            for i in range(1,10):
                lr = 0
                occ = 0
                memindexj = None
                num = 2**i
                for j in range(9):
                    if newrow[j] >= num and newrow[j] & num == num:
                        occ += 1
                    if newrow[j] % 2 == 0 and newrow[j] >= num and newrow[j] & num == num:
                        lr += 1
                        memindexj = j
                if lr == 1 and occ == 1: # quick & wierd fix but working
                    lrindex.append([memindexj, num + 1, newrow[memindexj], occ])
                    newrow[memindexj] = num + 1 # fixed
                    foundlr = True 
                    reloop = True
                    break

        return (foundlr, lrindex)

    # PARTIE 1

    while True:
        comm.send(None, dest=0, tag=Tags.READY.value)
        task = comm.recv(source=0, status=stts)
        tag = stts.Get_tag()

        if tag == Tags.NOTES.value:
            worker_package1 = workerNotes(task[0], task[1], task[2], task[3])
            comm.send(worker_package1, dest=0, tag=Tags.NOTES_FIN.value)
        elif tag == Tags.NOTES_VALIDATE.value:
            result = workerValidateNote(task[1])
            comm.send((result[0], task[0], result[1], task[2]), dest=0, tag=Tags.NOTES_VALIDATE_DONE.value)
        elif tag == Tags.NOTES_KILL.value:
            break
        elif tag == Tags.SEND_P2.value:
            #task[0]: line
            #task[1]: position (send back)
            #task[2]: type (send back)
            result = workerFindLR(task[0])
            #result[0]: found lr
            #result[1]: indexes of news
            comm.send((task[1],task[2],result[0],result[1],task[0]), dest=0, tag=Tags.RECV_P2.value)

    # PARTIE 2



def sudokuSolverM(sudokus):
    if rank == 0:
        for sudoku in sudokus:
            adminProcess(sudoku)
            break
    else:
        workerProcess()

    return sudokus

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
                if len(sudokus) == 1:
                    sudokuSolverM(sudokus)
                current_sudoku = []
            row = []