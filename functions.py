import numpy as np

def read_netlists():

    with open('netlists.txt') as f:
        lines = f.read().splitlines()

    return lines


def get_elements(lines):

    elements = []

    for line in lines:
        element = {'id':line[0],'nodeA':line[1],'nodeB':line[2],'value':line[3]}
        if line[0][0] == "I":
            element['type']= line[3]
            if element['type'] == 'sin':
                element['amp'] = line[4]
                element['freq'] = line[5]
                element['phase']= line[6]
            else:
                element['value'] = line[4]
            
        elif line[0][0] == "G":
            element['nodeC'] = line[3]
            element['nodeD'] = line[4]
            element['value'] = line[5]
        elif line[0][0] == "K":
            element['L1'] = line[3]
            element['nodeC'] = line[4]
            element['nodeD'] = line[5]
            element['L2'] = line[6]
            element['M'] = line[7]

        elements.append(element)

    return elements



def init_matrix(elements):

    biggest_node = 0
    for element in elements:
        if element['nodeA'] > biggest_node:
            biggest_node =  element['nodeA']
        if element['nodeB'] > biggest_node:
            biggest_node =  element['nodeB']

    Gn_matrix = []
    In_vector = []

    