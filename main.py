from os import remove
from functions import apply_pattern, get_elements, get_freq, init_matrix, read_netlists, remove_ground, solve_node


netlist = input("Insira o nome do arquivo 'netlist.txt':")
    
lines = read_netlists(netlist)
elements = get_elements(lines)
Gn_matrix, In_vector = init_matrix(elements)
freq = get_freq(elements)
apply_pattern(Gn_matrix, In_vector, elements, freq)
remove_ground(Gn_matrix,In_vector)
e = solve_node(Gn_matrix,In_vector)


print(Gn_matrix)
print(In_vector)
print(e)