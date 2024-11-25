'''
Alex Knowlton
11/1/2024

Defines functions to write .mem files.
'''
import numpy as np


def write_matrix_to_files(A, path, n, layer_num):
    '''
    writes a quantized matrix to a file
    '''
    for i in range(len(A)):
        current_vector = A[i, :]
        padded_string = str(i).zfill(3)
        write_mem_file(current_vector, f'{path}/{layer_num}_{padded_string}', n)


def write_mem_file(x, path, n_bits):
    '''
    given an iterable x of signed integers, opens a file defined at path 
    (erasing whatever was there previously), and writes a .mem file with
    x[0] at the LSB.

    Inputs:
        x - iterable of signed integers
        path - relative path to save location
        n_bits - number of binary bits to convert x to

    Output:
        writes a file at {path}.mem with x[0] at the LSB index in hex
        notation, with n_bits of representation in signed 2's complement form
    '''
    write_to_file(x, f'{path}.mem', n_bits)


def write_mif_file(x, path, n_bits):
    '''
    given an iterable x of signed integers, opens a file defined at path 
    (erasing whatever was there previously), and writes a .mif file with
    x[0] at the LSB.

    Inputs:
        x - iterable of signed integers
        path - relative path to save location
        n_bits - number of binary bits to convert x to

    Output:
        writes a file at {path}.mif with x[0] at the LSB index in hex
        notation, with n_bits of representation in signed 2's complement form
    '''
    write_to_file(x, f'{path}.mif', n_bits)


def write_to_file(x, path, n_bits):
    '''
    given an iterable x of signed integers, opens a file defined at path 
    (erasing whatever was there previously), and writes a file with
    x[0] at the LSB.

    Inputs:
        x - iterable of signed integers
        path - relative path to save location
        n_bits - number of binary bits to convert x to

    Output:
        writes a file at path with x[0] at the LSB index in hex
        notation, with n_bits of representation in signed 2's complement form
    '''
    with open(path, 'w') as fd:
        for x_i in x:
            hex_string = get_2s_complement_hex_string(x_i, n_bits)
            print(hex_string, file=fd)


def int_to_signed_bits(xin, bit_width=16):
    '''
    Given a signed number n, return an array representing the bits of n
    '''
    if xin < 0:
        xin = (1 << bit_width) + xin  # Add 2^bit_width to get the 2's complement representation
    
    # Convert to binary string and pad with leading zeros
    binary_str = format(xin, '0{}b'.format(bit_width))[-bit_width:]
    
    # Convert the binary string to a numpy array of integers (0 and 1)
    bits_array = np.array([int(bit) for bit in binary_str], dtype=int)
    
    return bits_array[::-1]


def get_2s_complement_hex_string(x, n_bits):
    '''
    given a value x, quantizes x to n_bits in 2's complement and returns
    a hex string of n_bits.
    '''
    if x < 0:
        x = (1 << n_bits) + x
    x_signed = x & ((1 << n_bits) - 1)
    hex_string = hex(x_signed)
    return hex_string.upper()[2:].zfill(int(np.ceil(n_bits / 4)))


def main():
    '''
    Test functions by writing 5, 6, -5 with 4 bits to "./test.mif"
    '''
    x = [5, 6, -5]
    write_mif_file(x, './test', 4)


if __name__ == '__main__':
    main()