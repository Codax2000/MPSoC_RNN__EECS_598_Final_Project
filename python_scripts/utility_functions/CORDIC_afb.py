import fp_logic as fp
import numpy as np
from CORDIC import CORDIC as cordic
import matplotlib.pyplot as plt

"""

Tanh calculation from cascading hyperbolic CORDIC processors to computer sinh and cosh

"""

import fp_logic as fp
import numpy as np
from CORDIC import CORDIC as cordic
import matplotlib.pyplot as plt

def Kh_extended_calc(M, N):
    product_neg = np.prod([np.sqrt(1 - (1 - 2**(i-2))**2) for i in range(-M, 1)])
    product_pos = np.prod([np.sqrt(1 - (2**-i)**2) for i in range(1, N+1)])
    return product_neg * product_pos

# Partition index calculation
def calculate_partition_index(N):
    return int(round((N - 2) / 3))

# On-the-fly bit extraction
def bit_slice(num, i):
    return ((num >> i) & 0x0001)

# Calculate rotation directions for the LSP using the last z value
def calculate_rotation_direction(z_in, n):
    directions = [0] * n
    directions[0] = 1 if z_in < 0 else -1

    for i in range(1, n):
        if bit_slice(z_in, n - i) == 0:
            directions[i] = 1
        else:
            directions[i] = -1

    return directions

# Cordic block 1


def cordic_calc_block1(x_i, y_i, z_i, cordic_block1, M, Kh):
    x_i, y_i, z_i = cordic_block1._fix_types(x_i, y_i, z_i)
    x_g, y_g, z_g = cordic_block1._glue_logic(x_i, y_i, z_i, is_vectoring=False)
    x, y, z = x_g, y_g, z_g
    m=-1
    print(x, y, z)
    for i in range (-M, 1):
        theta = np.arctanh(1 - 2**(i-2))
        theta_fp = fp.fp_quantize(theta, 16, 8)
        dir = -1 if z < 0 else 1
        factor = 1 - 2**(i-2)
        x_temp = x - m * dir * y * factor
        y_temp = y + dir * x * factor
        z = z - dir * theta_fp
        x, y = x_temp, y_temp
    
    print(x, y, z)
    for i in range(1, cordic_block1._n_rotations+1):
        theta = np.arctanh(2**(-i))
        theta_fp = fp.fp_quantize(theta, 16, 8)
        dir = -1 if z < 0 else 1
        factor = 2**(-i)
        x_temp = x - m * dir * y * factor
        y_temp = y + dir * x * factor
        z = z - dir * theta_fp
        x, y = x_temp, y_temp
        #print(x, y, z)

    return x, y, z
    
    
def cordic_calc_block2(x_i, y_i, z_i, end_MSP, LSP,  n_rots, directions, Kh):
    lut = [2**(-i-1) for i in range(end_MSP, n_rots)]
    lut = np.array(lut)
    lut = fp.fp_quantize(lut)

    x, y, z = x_i, y_i, z_i
    print(directions)
    for i in range(LSP):
        direction = directions[i]
        factor = lut[i]
        x_new = x - direction * y * factor
        y_new = y + direction * x * factor
        z_new = z - direction * factor
        x,y,z = x_new, y_new, z_new

    return x, y, z

def compute_tanh(z, n_rotations=16, n_x=16, r_x=8, n_z=16, r_z=8):
    
    partition_index = calculate_partition_index(n_rotations)
    M = 1
    MSP = partition_index
    LSP = n_rotations - partition_index

    cordic_block1 = cordic(n_rotations=MSP, n_x=n_x, r_x=r_x, n_z=n_z, r_z=r_z)
    cordic_block2 = cordic(n_rotations=n_rotations, n_x=n_x, r_x=r_x, n_z=n_z, r_z=r_z)
    cordic_block3 = cordic(n_rotations=n_rotations, n_x=n_x, r_x=r_x, n_z=n_z, r_z=r_z)



    lut, K_fp, index, m = cordic_block3.get_rotation_constants(is_hyperbolic=True)

    Kh = Kh_extended_calc(M, n_rotations)

    x_in = fp.fp_quantize(1 / Kh, n_x, r_x)
    y_in = 0
    z_in = fp.fp_quantize(z, n_z, r_z)

    x1, y1, z1 = cordic_calc_block1(x_in, y_in, z_in, cordic_block1, M, K_fp)

    last_z_value = int(z1)  
    directions = calculate_rotation_direction(last_z_value, LSP)
    
    x2, y2, z2= cordic_calc_block2(x1, y1, z1, MSP, LSP, n_rotations, directions, K_fp)

    #x2_test, y2_test, z2_test, _ = cordic_block2.rotate(x1, y1, z1, is_hyperbolic=True)

    x_final, y_final, z_final, _ = cordic_block3.vector(x2, y2, 0, is_hyperbolic=False)
    #z_final = y2/x2
    #print(z_final)
    return z_final[-1, :]


# Testbench for z_values from 
def testbench(z_values):
    cordic_results = []
    actual_results = []
    for z in z_values:

        cordic_tanh_result = compute_tanh(z)
        
        cordic_tanh_float = cordic_tanh_result / (2 ** 8)
        cordic_results.append(cordic_tanh_float)

        numpy_tanh_result = np.tanh(z)
        actual_results.append(numpy_tanh_result)

        error = abs(cordic_tanh_float - numpy_tanh_result)

        print(f"input z {z} | Cordic Out:{cordic_tanh_float} | Expected Out:{numpy_tanh_result} | error:{error}")
    plt.figure(figsize=(10, 6))
    plt.plot(z_values, actual_results, label="numpy tanh", color="red")
    plt.plot(z_values, cordic_results, label="CORDIC tanh", color="black", marker="o")
    plt.xlabel("Input z")
    plt.ylabel("tanh(z)")
    plt.title("CORDIC tanh vs numpy tanh")
    plt.legend()
    plt.grid(True)
    plt.show()

z_test_values = np.linspace(-3,3)
testbench(z_test_values)

#compute_tanh(1)
#print(np.tanh(1))
# 166