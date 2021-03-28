from mpi4py import MPI

def sudokuSolverM(sudokus):
    print("inside1")
    
    print("\n")

    print(MPI.COMM_WORLD.size)

    print("\n")

    print(MPI.COMM_WORLD.rank)

    return sudokus