'''
Alex Knowlton
11/1/2024

Defines functions to write .mem files.
'''


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


def get_2s_complement_hex_string(x, n_bits):
    '''
    given a value x, quantizes x to n_bits in 2's complement and returns
    a hex string of n_bits.
    '''
    if x < 0:
        x = (1 << n_bits) + x
    x_signed = x & ((1 << n_bits) - 1)
    hex_string = hex(x_signed)[2:]
    return hex_string.upper()


def main():
    '''
    Test functions by writing 5, 6, -5 with 4 bits to "./test.mif"
    '''
    x = [5, 6, -5]
    write_mif_file(x, './test', 4)


if __name__ == '__main__':
    main()