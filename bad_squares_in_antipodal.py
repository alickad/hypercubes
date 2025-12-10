import subprocess
from argparse import ArgumentParser


DIMENSION = int(input())

def call_solver(cnf, nr_vars, output_name, solver_name, verbosity):
    # print CNF into formula.cnf in DIMACS format
    with open(output_name, "w") as file:
        file.write("p cnf " + str(nr_vars) + " " + str(len(cnf)) + '\n')
        for clause in cnf:
            file.write(' '.join(str(lit) for lit in clause) + " 0\n") # maybe 0 at the end??

    # call the solver and return the output
    return subprocess.run(['./' + solver_name, '-model', '-verb=' + str(verbosity) , output_name], stdout=subprocess.PIPE)

def E(u, v):
    if (u > v): 
        u,v = v,u
    if (u ^ v).bit_count() != 1:
        raise Exception("vertices", u, ",", v, "do not share an edge")
    e = (u << DIMENSION) + v - u - 1
MAX_E = E((1 << DIMENSION) - 2, (1 << DIMENSION) - 1)

def R(v):
    return MAX_E + v + 1
MAX_R = R((1 << DIMENSION) - 1)

def H(u, v):
    if (u ^ v).bit_count() != 1:
        raise Exception("vertices", u, ",", v, "do not share an edge")
    h = (u << DIMENSION) + v - u
    if v > u: h -= 1
    return MAX_R + h
MAX_H = H((1 << DIMENSION) - 2, (1 << DIMENSION) - 1)

def antipodalLogic():
    ...

def pathLogic():
    ...

def getTrueColors(result):
    ...


if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        default="input.in",
        type=str,
        help=(
            "The instance file."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help=(
            "Output file for the DIMACS format (i.e. the CNF formula)."
        ),
    )
    parser.add_argument(
        "-s",
        "--solver",
        default="glucose-4.2.1/sources/simp/glucose",
        type=str,
        help=(
            "The SAT solver to be used."
        ),
    )
    parser.add_argument(
        "-v",
        "--verb",
        default=1,
        type=int,
        choices=range(0,2),
        help=(
            "Verbosity of the SAT solver used."
        ),
    )
    args = parser.parse_args()

    # get the input instance

    cnf = []
    cnf.extend(antipodalLogic())
    cnf.extend(pathLogic())
    nr_vars = MAX_H

    # now we know the max clique has size smallEnd
    # we run the  SAT solver one last time to get the vertices of the clique
    result = call_solver(cnf, nr_vars, args.output, args.solver, args.verb)
    if result.returncode != 10:
        print("There is no antipodal coloring with a bad square in a cube with dimension", DIMENSION)
    
    else:
        print("the following coloring makes a bad square 0, 1, 2, 3:")
        redEdges = getTrueColors(result)
        print("red edges")
        print(*redEdges)
        print("the rest is blue")
  