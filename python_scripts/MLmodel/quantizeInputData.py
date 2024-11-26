from fp_logic import *
import numpy

infilepath = 'python_scripts\\MLmodel\\Dataset\\all_data\\data.txt'
outfilepath = 'python_scripts\\MLmodel\\Dataset\\all_data\\data_q.txt'
matrix = np.loadtxt(infilepath, delimiter=',')
quantizedMat = fp_quantize(matrix) * (2** -8) 
np.savetxt(outfilepath, matrix, delimiter=',', fmt='%f')  # Change fmt if needed

