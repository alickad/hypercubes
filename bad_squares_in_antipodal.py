import subprocess
from argparse import ArgumentParser


DIMENSION = int(input())
NUM_OF_VERTICES = 1 << DIMENSION
NUM_OF_EDGES = NUM_OF_VERTICES * DIMENSION / 2

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
    e = (u << DIMENSION) + v - u
    return int(e)
MAX_E = E(NUM_OF_VERTICES - 2, NUM_OF_VERTICES - 1)

def H(u, v, color, start):
    if (u ^ v).bit_count() != 1:
        raise Exception("vertices", u, ",", v, "do not share an edge")
    if (v == start):
        raise Exception("edge", u, ",", v, "goes to the start vertex")
    h = (u << DIMENSION) + v - u


    if color == "red" and start == 0:
        return int(MAX_E + h)
    elif color == "blue" and start == 0:
        return int(MAX_E + NUM_OF_EDGES + h)
    elif color == "red" and start == 1:
        return int(MAX_E + 2*NUM_OF_EDGES + h)
    elif color == "blue" and start == 1:
        return int(MAX_E + 3*NUM_OF_EDGES + h)
    else: raise Exception("the input value of color or start is wrong")
MAX_H = H(NUM_OF_VERTICES - 1, NUM_OF_VERTICES - 2, "blue", 1)

# is vertex v reachable from 0 or 1 only using blue or red edges?
def V(v, color, start):
    if color == "red" and start == 0:
        return int(MAX_H + v + 1)
    elif color == "blue" and start == 0:
        return int(MAX_H + NUM_OF_VERTICES + v + 1)
    elif color == "red" and start == 1:
        return int(MAX_H + 2*NUM_OF_VERTICES + v + 1)
    elif color == "blue" and start == 1:
        return int(MAX_H + 3*NUM_OF_VERTICES + v + 1)
    else: raise Exception("the input value of color or start is wrong")
MAX_V = V(NUM_OF_VERTICES - 1, "blue", 1)

def anti(u):
    return int(NUM_OF_VERTICES - 1 - u)

def antipodalLogic():
    logic = []
    for u in range(NUM_OF_VERTICES):
        for d in range(DIMENSION):
            v = u ^ (1 << d)
            logic.append([E(u,v), E(anti(u), anti(v))])
            logic.append([- E(u,v), - E(anti(u), anti(v))])
    return logic


def pathLogic():
    logic = []
    for color in ["red", "blue"]:
        for start in [0, 1]:
            logic.append([V(start, color, start)])
            # TODO vyriesit H sem... ci netreba?
            logic.append([ - V(start ^ 3, color, start)])
            c = (-1)**(color == "blue")
            for u in range(NUM_OF_VERTICES):
                for d in range(DIMENSION):
                    v = u ^ (1 << d)
                    if (v == start):
                        continue
                    logic.append([ - H(u, v, color, start), V(u, color, start)])
                    logic.append([ - H(u, v, color, start), E(u, v) * c])
                    logic.append([H(u, v, color, start), - V(u, color, start), -E(u,v) * c])

            for v in range(NUM_OF_VERTICES):
                if (v == start):
                        continue
                big_clause = [-V(v, color, start)]
                for d in range(DIMENSION):
                    u = v ^ (1 << d)
                    logic.append([V(v, color, start), - H(u, v, color, start)])
                    big_clause.append(H(u, v, color, start))
                logic.append(big_clause)

    return logic
    


def getTrueColors(result):
    model = []
    for line in result.stdout.decode('utf-8').split('\n'):
        if line.startswith("v"):    # there might be more lines of the model, each starting with 'v'
            vars = line.split(" ")
            vars.remove("v")
            model.extend(int(v) for v in vars)      
    #model.remove(0) # 0 is the end of the model, just ignore it
    red = []
    for m in model:
        if (abs(m) <= MAX_E and m > 0): 
            u = m >> DIMENSION
            v = (m - (u << DIMENSION)) + u
            red.append([u, v])
    return red

def write_red_edges(redEdges):
    with open("red_edges.txt", "w") as file:
        for edge in redEdges:
            file.write(str(edge[0]) + " " + str(edge[1]) + "\n")


if __name__ == "__main__":

    parser = ArgumentParser()

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
    nr_vars = MAX_V

    #print(cnf)

    # now we know the max clique has size smallEnd
    # we run the  SAT solver one last time to get the vertices of the clique
    result = call_solver(cnf, nr_vars, args.output, args.solver, args.verb)
    if result.returncode != 10:
        print("There is no antipodal coloring with a bad square in a cube with dimension", DIMENSION)
    
    else:
        #print("the following coloring makes a bad square 0, 1, 2, 3:")
        redEdges = getTrueColors(result)
        #print("red edges")
        #print(*redEdges)
        write_red_edges(redEdges)
        #print("the rest is blue")
        print("There is an antipodal coloring with a bad square in a cube with dimension", DIMENSION)
  