import numpy as np
from scipy.special import spherical_jn
from scipy.special import spherical_yn
from scipy.special import jv
from scipy.special import yv
from .spectrum_driver import SpectrumDriver


class MieDriver(SpectrumDriver):
    """ Compute the absorption, scattering, and extinction spectra of a sphere using Mie theory

        Attributes
        ----------
        radius : float
            the radius of the sphere
                
        number_of_wavelengths : int
            the number of wavelengths over which the cross sections / efficiencies will be computed
                
        wavelength_array : 1 x number_of_wavelengths numpy array of floats
            the array of wavelengths in meters over which you will compute the spectra
                
        _size_factor_array : 1 x number_of_wavelengths numpy array of floats
            size factor of the sphere
           
        _relative_refractive_index_array : 1 x number_of_wavelengths numpy array of complex floats
            the array of refractive index values corresponding to wavelength_array
                
        _medium_refractive_index : float
            the refractive index of the surrounding medium - assumed to be real and wavelength-independent

        q_scat : numpy array of floats
            the scattering efficiency as a function of wavelength

        q_ext : numpy array of floats
            the extenction efficiency as a function of wavelength

        q_abs : 1 x number_of_wavelengths numpy array of floats
            the absorption efficiency as a function of wavelength
                 
        c_scat : numpy array of floats
            the scattering cross section as a function of wavelength

        c_ext : numpy array of floats
            the extinction cross section as a function of wavelength

        c_abs : 1 x number_of_wavelengths numpy array of floats
            the absorption efficiency as a function of wavelength
                 
        _max_coefficient_n : int
            the maximum coefficient to be computed in the Mie expansion
                
        _n_array : 1 x _max_coefficient_n array of ints
            array of indices for the terms in the Mie expansion
                 
        _an : _max_coefficient x number_of_wavelengths numpy array of complex floats
            the array of a coefficients in the Mie expansion
                 
        _bn : _max_coefficientx x number_of_wavelengths numpy array of complex floats
            the array of b coefficients in the Mie expansion
                 
        _cn : _max_coefficientx x number_of_wavelengths numpy array of complex floats
            the array of c coefficients in the Mie expansion
                 
        _dn : _max_coefficientx x number_of_wavelengths numpy array of complex floats
            the array of d coefficients in the Mie expansion
             

        Returns
        -------
        None
    
        Examples
        --------
        >>> fill_in_with_actual_example!
    """

    def __init__(self, args):
        self.parse_input(args)
        print('Radius of the sphere is ', self.radius)
        self.ci = 0+1j
        
    def parse_input(self, args):
        if 'radius' in args:
            self.radius = args['radius']
        else:
            self.radius = 100e-9
        if 'wavelength_list' in args:
            lamlist = args['wavelength_list']
            self.wavelength_array = np.linspace(lamlist[0],lamlist[1],int(lamlist[2]))
            self.number_of_wavelengths = int(lamlist[2])
        else:
            self.wavelength_array = np.linspace(400e-9,800e-9,10)
            self.number_of_wavelengths = 10
        
        # hard-code the RI data
        self.sphere_refractive_index_array = (1.5+0j) * np.ones(self.number_of_wavelengths)
        self._medium_refractive_index = 1.0+0j
        self._relative_refractive_index_array = self.sphere_refractive_index_array / self._medium_refractive_index
        self._relative_permeability = 1.0+0j
        self._size_factor_array = np.pi * 2 * self.radius / self.wavelength_array
        
        
    def compute_spectrum(self):
        """ Will prepare the attributes forcomputing q_ext, q_abs, q_scat, c_abs, c_ext, c_scat
            via computing the mie coefficients
            
            Attributes
            ---------
            TBD
            
            
            Returns
            -------
            TBD
            
        """

        pass
    
    def _compute_s_jn(self, n, z):
        """ Compute the spherical bessel function from the Bessel function
            of the first kind
            
            Arguments
            ---------
            n : 1 x _max_coefficient numpy array of ints
                orders of the bessel function
                
            z : float
                size parameter of the sphere
            
            
            Returns
            -------
            _s_jn

            Test Implemented
            ----------------
            Yes
            
        """
        ns = n+0.5
        return np.sqrt(np.pi / (2 * z)) * jv(ns, z)
        
        
    def _compute_s_yn(self, n, z):
        """ Compute the spherical bessel function from the Bessel function
            of the first kind
            
            Arguments
            ---------
            n : 1 x _max_coefficient numpy array of ints
                orders of the bessel function
                
            z : float
                variable passed to the bessel function
            
            
            Returns
            -------
            _s_jn

            Test Implemented
            ----------------
            Yes
            
        """
        ns = n+0.5
        return np.sqrt(np.pi / (2 * z)) * yv(ns, z)
        
    def _compute_s_hn(self, n, z):
        """ Compute the spherical bessel function h_n^{(1)}
            
            Arguments
            ---------
            n : 1 x _max_coefficient array of int
                orders of the bessel function
                
            z : float
                variable passed to the bessel function
            
            
            Returns
            -------
            _s_hn

            Test Implemented
            ----------------
            Yes
        """
        return spherical_jn(n, z) + self.ci * spherical_yn(n, z)
        

    def _compute_z_jn_prime(self, n, z):
        """ Compute derivative of z*j_n(z) using recurrence relations
        
            Arguments
            ---------
            n : 1 x _max_coefficient array of int
                orders of the bessel functions
            z : float
                variable passed to the bessel function
                
            Returns
            -------
            _z_jn_prime
            
            Test Implemented
            ----------------
            Yes
            
        """
        return z * spherical_jn( n - 1, z) - n * spherical_jn(n , z)
        
    def _compute_z_hn_prime(self, n, z):
        """ Compute derivative of z*h_n^{(1)}(z) using recurrence relations
           
            Arguments
            ---------
            n : 1 x _max_coefficient array of int
                orders of the bessel functions
            z : float
                variable passed to the bessel function
                
            Returns
            -------
            _z_hn_prime
        
        """

                

        return z *  self._compute_s_hn( n - 1, z) - n * self._compute_s_hn( n , z)
        
    def _compute_mie_coeffients(self, m, mu, x):
        """ computes the Mie coefficients given relative refractive index, 
           
            Arguments
            ---------
            n : 1 x _max_coefficient array of ints
                order of the mie coefficients functions
            m : complex float
                relative refractive index of the sphere to the medium
            mu : complex float
                relative permeability of the sphere to the medium (typically 1)
            x : float
                size parameter of the sphere
                
            Attributes
            -------
            _an
            
            _bn
            
            _cn
            
            _dn

        """
        self._compute_n_array(x)
        # self._n_array will be an array from 1 to n_max
        print(self._n_array)
        
        # pre-compute terms that will be used numerous times in computing coefficients
        _jnx = spherical_jn(self._n_array , x)
        _jnmx = spherical_jn(self._n_array , m * x)
        _hnx = self._compute_s_hn(self._n_array, x)
        _xjnxp = self._compute_z_jn_prime(self._n_array, x)
        _mxjnmxp = self._compute_z_jn_prime(self._n_array, m*x)
        _xhnxp = self._compute_z_hn_prime(self._n_array, x)
        
        # a_n coefficients
        _a_numerator   = m ** 2 * _jnmx * _xjnxp - mu * _jnx * _mxjnmxp
        _a_denominator = m ** 2 * _jnmx * _xhnxp - mu * _hnx * _mxjnmxp
        
        self._an = _a_numerator / _a_denominator
        
        # b_n coefficients
        _b_numerator   = mu * _jnmx * _xjnxp - _jnx * _mxjnmxp
        _b_denominator = mu * _jnmx * _xhnxp - _hnx * _mxjnmxp
        
        self._bn = _b_numerator / _b_denominator
        
        # c_n coefficients
        _c_numerator   = mu * _jnx * _xhnxp - mu * _hnx * _xjnxp
        _c_denominator = mu * _jnmx * _xhnxp - _hnx * _mxjnmxp
        
        self._cn = _c_numerator / _c_denominator
        
        # d_n coefficients
        _d_numerator   = mu * m * _jnx * _xhnxp - mu * m * _hnx * _xjnxp
        _d_denominator = m ** 2 * _jnmx * _xhnxp - mu * _hnx * _mxjnmxp
        
        self._dn = _d_numerator / _d_denominator
        return [self._an,self._bn,self._cn,self._dn]
        
    def _compute_q_scattering(self, m, mu, x):
        """ computes the scattering efficiency from the mie coefficients
 
            Parameters
            ----------
            m : complex float
                relative refractive index of the sphere

            mu : float
                relative permeability of the sphere
     
            x : float
                size parameter of the sphere, defined as 2 * pi * r / lambda
                where r is the radius of the sphere and lambda is the wavelength of illumination
           
            Attributes
            -------
            q_scat
            
            Returns
            -------
            q_scat

        """
        return 'replace_w_q_scat'
        
    def _compute_q_extinction(self, m, mu, x):
        """ computes the extinction efficiency from the mie coefficients
           
            Parameters
            ----------

            m : complex float
                relative refractive index of the sphere

            mu : float
                relative permeability of the sphere
     
            x : float
                size parameter of the sphere, defined as 2 * pi * r / lambda
                where r is the radius of the sphere and lambda is the wavelength of illumination
           
            Attributes
            -------
            q_ext
            
            Returns
            -------
            q_ext

        """
        return 'replace_with_q_ext'

    def _compute_n_array(self, x):
        _n_max = int(x + 4*x**(1/3.)+2)
        self._n_array = np.copy( np.linspace(1, _n_max, _n_max, dtype=int) )
        
    
