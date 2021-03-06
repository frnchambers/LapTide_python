# I think a useful tool might be one that can work out some mode properties given a (m, l) or (m, k), for instance: whether it is odd/even, type of mode (g, r, Kelvin, Yanai), the asymptotic approximation with q, location of the equatorial waveguide with q. I suggest writing a header that can work this out and implements the approximations - you could call this something like mode-admin.
import numpy as np
import warnings

import os
cwd = os.getcwd()

class InputWarning(UserWarning):
    pass

def custom_formatwarning(msg, *args, **kwargs):
    # ignore everything except the message
    name = args[0].__name__
    loc = args[1]
    line = args[2]
    warningloc = "{}:{}: {}: ".format(loc.replace(cwd, "")[1:], line, name)
    return warningloc + str(msg) + '\n'
warnings.formatwarning = custom_formatwarning
warnings.simplefilter('always', InputWarning)


class Mode_admin:
    def __init__(self, m, k):
        """
        Need to work in the spin of the q's I am testing, since that sets prograde/
        retrograde movement, which will set the mode for -2<k<2
        """
        self.m = m
        self.k = k
        self.l = self.get_l()
        self.validate_values()
        self.is_even = self.check_is_even()

    def get_l(self):
        """
        Sets self.l and returns it according to the following:
        l = k + np.abs(m)
        """
        self.l = self.k + np.abs(self.m)
        return self.l

    def check_is_even(self):
        """
        Check if m+l is even (True) or odd (False)
        """
        if (self.m + self.l) % 2 == 0:
            return True
        return False

    def get_wavemode(self, direction=None):
        """
        Returns the wavemode for the given parameters. #TODO; expand this to include different m?
        """
        if self.k <= -2:
            self.mode = "r mode"
        elif self.k >= 2:
            self.mode = "g mode"
        else:
            if not direction:  # this should now never happen anymore
                try:
                    direction = self.set_direction()
                except:
                    self.mode = "Mode depends on Prograde/Retrograde spin"
                    return self.mode
            if direction.lower() in ["prograde", "pro"]:
                if self.k == 1:
                    self.mode = "yanai mode"
                elif self.k == 0:
                    self.mode = "kelvin mode"
                else:
                    self.validate_values()
                    exit()
            elif direction.lower() in ["retrograde", "retro"]:
                if self.k == -1:
                    self.mode = "yanai mode"
                elif self.k >= 0:
                    self.mode = "g mode"
        return self.mode

    def validate_values(self):
        if abs(self.m) > abs(self.l):
            warnings.warn("Legendre polynomials undefined for m>l, input: ({}, {}). Eigenvalues might not exist.".format(abs(self.m), abs(self.l)), InputWarning)

    def set_qlist(self, qlist):
        """
        Stores the qlist into the wavemode, helpful for some function calls to
        put all data in one class
        """
        self.qlist = qlist

    def set_curvilinear(self, ecc, chi, dlngrav):
        """
        Stores the eccentricity and dlngrav, helpful for some later function
        cals to have all data stored in one class
        """
        self.ecc = ecc
        self.chi = chi
        self.dlngrav = dlngrav

    def get_direction(self):
        """
        Should only be called *AFTER* qlist has been set!
        """
        if np.average(self.qlist)*self.m < 0:
            self.direction = "pro"
        else:
            self.direction = "retro"
        return self.direction


class Curvi_admin:
    def __init__(self, m, k, qarr):
        """
        Updated version which will be used for the curvilinear equations.
        m and k should be integers, qarr should be a list or array (it converts
        to an array if it is given a list)
        
        The idea is that it will check what kind of wave it is, then calculate
        the asymptotic values for all q in qarr, and then pass those into a
        rootfinding routine (which can look positive and negative directions!)
        and that updates back the correct eigenvalues into lamarr
        """
        self.m = m
        self.k = k
        self.l = self.get_l()
        self.validate_values()
        if not type(qarr) == np.ndarray:
            self.qarr = np.asarray(qarr)
        else:
            self.qarr = qarr
        self.lamarr = np.ones(len(qarr))
        self.asymptotes = self.get_wavemode()  # TODO, update this to asymptote calculation
    
    def get_l(self):
        """
        Sets self.l and returns it according to the following:
        l = k + np.abs(m)
        """
        self.l = self.k + np.abs(self.m)
        return self.l

    def is_even(self):
        """
        Check if m+k is even (True) or odd (False)
        """
        if (self.m + self.k) % 2 == 0:
            return True
        return False

    def get_wavemode(self):
        """
        Returns the wavemode for the given parameters. #TODO; expand this to include all wavemodes
        """
        if self.k < -2:
            self.mode = "r mode"
        elif self.k > 2:
            self.mode = "g mode"
        else:
            self.mode = "Mode depends on Prograde/Retrograde spin"
        return self.mode

    def validate_values(self):
        if self.m > self.l:
            warnings.warn("Legendre polynomials undefined for m>l, input: ({}, {}). Eigenvalues might not exist.".format(self.m, self.l), InputWarning)
    
    
