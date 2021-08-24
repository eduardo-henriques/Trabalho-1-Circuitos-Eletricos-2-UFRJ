import numpy as np
import math

def read_netlists(file_name):

    with open(f'{file_name}') as f:
        lines = f.read().splitlines()

    return lines


def get_elements(lines):

    elements = []

    for line in lines:
        line=line.split(' ')
        if line[0]!= '*':
            element = {'id':line[0],'nodeA':int(line[1]),'nodeB':int(line[2]),'value':line[3]}
            if line[0][0] == "I":
                element['type']= line[3]
                if element['type'] == 'sin' or element['type']== 'SIN':
                    del element['value']
                    element['amp'] = float(line[4])
                    element['freq'] = float(line[5])
                    element['phase']= float(line[6])
                else:
                    element['value'] = float(line[4])
                
            elif line[0][0] == "G":
                element['nodeC'] = int(line[3])
                element['nodeD'] = int(line[4])
                element['value'] = float(line[5])
            elif line[0][0] == "K":
                del element['value']
                element['L1'] = float(line[3])
                element['nodeC'] = int(line[4])
                element['nodeD'] = int(line[5])
                element['L2'] = float(line[6])
                element['M'] = float(line[7])
            else:
                element['value'] = float(element['value'])

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

    for line in range(0, biggest_node+1, 1):
        Gn_matrix.append([])
        In_vector.append(0)
        for column in range(0,biggest_node+1,1):
            Gn_matrix[line].append(0)

    return Gn_matrix, In_vector


def current_pattern(In_vector, element):

    if element['type'] == 'DC' or element['type'] == 'dc':
        In_vector[element['nodeA']] += -element['value']
        In_vector[element['nodeB']] += element['value']
    else:
        In_vector[element['nodeA']] += -element['amp']*math.e**(element['phase']*1j)
        In_vector[element['nodeB']] += element['amp']*math.e**(element['phase']*1j)


def dependent_current_pattern(Gn_matrix, element):

    Gn_matrix[element['nodeA']][element['nodeC']] += element['value']
    Gn_matrix[element['nodeB']][element['nodeC']] += -element['value']
    Gn_matrix[element['nodeA']][element['nodeD']] += -element['value']
    Gn_matrix[element['nodeB']][element['nodeD']] += element['value']

def resistor_pattern(Gn_matrix, element):

    Gn_matrix[element['nodeA']][element['nodeA']] += 1/(element['value'])
    Gn_matrix[element['nodeB']][element['nodeB']] += 1/(element['value'])
    Gn_matrix[element['nodeA']][element['nodeB']] += -1/(element['value'])
    Gn_matrix[element['nodeB']][element['nodeA']] += -1/(element['value'])


def inductor_pattern(Gn_matrix, element, freq):

    if freq == 0:
        print('frequencia zero')
    else:
        Gn_matrix[element['nodeA']][element['nodeA']] += 1/(1j*freq*element['value'])
        Gn_matrix[element['nodeB']][element['nodeB']] += 1/(1j*freq*element['value'])
        Gn_matrix[element['nodeA']][element['nodeB']] += -1/(1j*freq*element['value'])
        Gn_matrix[element['nodeB']][element['nodeA']] += -1/(1j*freq*element['value'])


def capacitor_pattern(Gn_matrix, element, freq):

    if freq == 0:
        print('frequencia zero')
    else:
        Gn_matrix[element['nodeA']][element['nodeA']] += 1j*freq*element['value']
        Gn_matrix[element['nodeB']][element['nodeB']] += 1j*freq*element['value']
        Gn_matrix[element['nodeA']][element['nodeB']] += -1j*freq*element['value']
        Gn_matrix[element['nodeB']][element['nodeA']] += -1j*freq*element['value']


def transformer_pattern(Gn_matrix, element, freq):

    denominator = element['L1']*element['L2'] - element['M']**2
    T11 = element['L2']/denominator
    T22 = element['L1']/denominator
    T12 = -element['M']/denominator

    Gn_matrix[element['nodeA']][element['nodeA']] += T11/(1j*freq)
    Gn_matrix[element['nodeA']][element['nodeB']] += -T11/(1j*freq)
    Gn_matrix[element['nodeA']][element['nodeC']] += T12/(1j*freq)
    Gn_matrix[element['nodeA']][element['nodeD']] += -T12/(1j*freq)

    Gn_matrix[element['nodeB']][element['nodeA']] += -T11/(1j*freq)
    Gn_matrix[element['nodeB']][element['nodeB']] += T11/(1j*freq)
    Gn_matrix[element['nodeB']][element['nodeC']] += -T12/(1j*freq)
    Gn_matrix[element['nodeB']][element['nodeD']] += T12/(1j*freq)

    Gn_matrix[element['nodeC']][element['nodeA']] += T12/(1j*freq)
    Gn_matrix[element['nodeC']][element['nodeB']] += -T12/(1j*freq)
    Gn_matrix[element['nodeC']][element['nodeC']] += T22/(1j*freq)
    Gn_matrix[element['nodeC']][element['nodeD']] += -T22/(1j*freq)

    Gn_matrix[element['nodeD']][element['nodeA']] += -T12/(1j*freq)
    Gn_matrix[element['nodeD']][element['nodeB']] += T12/(1j*freq)
    Gn_matrix[element['nodeD']][element['nodeC']] += -T22/(1j*freq)
    Gn_matrix[element['nodeD']][element['nodeD']] += T22/(1j*freq)


def get_freq(elements):

    freq = 0

    for element in elements:
        if 'freq' in element.keys():
            freq = element['freq']
            break
    return freq



def apply_pattern(Gn_matrix, In_vector, elements, freq):

    for element in elements:
        if element['id'][0] == 'I':
            current_pattern(In_vector, element)
        elif element['id'][0] == 'G':
            dependent_current_pattern(Gn_matrix, element)
        elif element['id'][0]=='R':
            resistor_pattern(Gn_matrix, element)
        elif element['id'][0]=='L':
            inductor_pattern(Gn_matrix, element, freq)
        elif element['id'][0]=='C':
            capacitor_pattern(Gn_matrix, element, freq)
        elif element['id'][0] =='K':
            transformer_pattern(Gn_matrix, element, freq)


def remove_ground(Gn_matrix, In_vector):

    Gn_matrix.pop(0)
    In_vector.pop(0)

    for index in range(0,len(Gn_matrix),1):
        Gn_matrix[index].pop(0)


def solve_node(Gn_matrix, In_vector):

     Y = np.array(Gn_matrix)
     I = np.array(In_vector)
     e = np.linalg.solve(Y,I)

     return e














