'''
Alex Knowlton
10/24

defines a CORDIC object capable of hyperbolic or linear
rotation or vectoring.
'''

from fp_logic import *

class CORDIC:
    '''
    CORDIC object
    '''

    def __init__(self, n_rotations=16, n_x=16, r_x=8, n_z=16, r_z=16):
        '''
        Object constructor. Defines what fixed point representation this object
        will use in Q(n_x, r_x) notation. Also defines how many times a
        rotation will be performed, defaults to 15 rotations and Q(16,8)
        '''
        self._n_x = n_x
        self._r_x = r_x
        self._n_z = n_z
        self._r_z = r_z
        self._n_rotations = n_rotations

    def rotate(self, x, y, z, is_hyperbolic=False):
        '''
        rotates x, y, and z towards z = 0. If is_hyperbolic is True, uses the
        arctanh lookup values instead of the arctan values.
        '''
        return self._cordic_rotate(x, y, z, False, is_hyperbolic)

    def vector(self, x, y, z, is_hyperbolic=False):
        '''
        rotates x, y, and z towards y = 0. If is_hyperbolic is True, uses the
        arctanh lookup values instead of the arctan values.
        '''
        return self._cordic_rotate(x, y, z, True, is_hyperbolic)
    
    def _cordic_rotate(self, x, y, z, is_vectoring, is_hyperbolic):
        '''
        Internal unified CORDIC logic. rotates x, y, and z based on whether
        CORDIC is in vectoring or hyperbolic mode and returns x, y, and z
        matrices based on iterations of the CORDIC. The first row is the input
        as it is passed to the function. The second is post-glue logic,
        followed by n_rotations rows of each value after iteration j. The last
        row is after scaling by the appropriate value of K.
        '''
        x_glue, y_glue, z_glue = self._glue_logic(x, y, z, is_vectoring)

        # create result arrays
        x_out = np.zeros((len(x), self._n_rotations + 3))
        y_out = np.zeros((len(x), self._n_rotations + 3))
        z_out = np.zeros((len(x), self._n_rotations + 3))
        sigma = np.zeros((len(x), self._n_rotations))

        x_out[1, :] = x
        y_out[1, :] = y
        z_out[1, :] = z

        x_out[2, :] = x_glue
        y_out[2, :] = y_glue
        z_out[2, :] = z_glue

        # rename for readability, now that things are saved
        x = x_out
        y = y_out
        z = z_out

        j = np.array(range(self._n_rotations))
        m = 1
        if is_hyperbolic:
            m = -1
            j += 1

        # set appropriate lookup table for the operation
        lut, K = self.get_rotation_constants(is_hyperbolic)

        # this all needs debugging
        for i in range(self._n_rotations):
            if is_vectoring:
                sigma[i, :] = (y[i, :] < 0) * 1
            else:
                sigma[i, :] = (z[i, :] >= 0) * 1
            
            x[i+3, :] = x[i+2, :] - m * sigma[i, :] * y[i+2, :]
            y[i+3, :] = y[i+2, :] - sigma[i, :] * x[i+2, :]
            z[i+3, :] = z[i+2, :] - sigma[i, :] * lut[i]

        x[-1, :] = x[-2, :] * K
        y[-1, :] = y[-2, :] * K
        return x, y, z, sigma
    
    def _glue_logic(self, x, y, z, is_vectoring):
        '''
        Shifts things to the right half plane as necessary
        '''
        ppi, npi, ppi_half, npi_half = self.get_pi_constants(False)
    
    def get_rotation_constants(self, is_hyperbolic):
        '''
        Returns the fixed point K and LUT values as decimal mantissa values 
        for this CORDIC based on whether this is hyperbolic or not
        '''
        pass

    def get_pi_constants(self):
        '''
        Returns pi, -pi, pi / 2, and -pi / 2 as fixed point constants
        '''
        pass



