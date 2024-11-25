from fp_logic import *
import numpy

infilepath = 'python_scripts\\MLmodel\\Dataset\\all_data\\data.txt'
outfilepath = 'python_scripts\\MLmodel\\Dataset\\all_data_q\\data_q.txt'
matrix = np.loadtxt(infilepath, delimiter=',')
quantizedMat = fp_quantize(matrix, n=16,r=12) * (2** -12) 
np.savetxt(outfilepath, quantizedMat, delimiter=',', fmt='%f')  # Change fmt if needed

