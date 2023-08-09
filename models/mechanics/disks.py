from sympy import (Symbol, symbols, Matrix, sin, cos, asin, diff, sqrt, S,
                   diag, Eq, hessian, Function, flatten, Tuple, im, pi, latex,
                   dsolve, solve, fraction, factorial, Subs, Number, oo, Abs,
                   N, solveset)

from sympy.physics.mechanics import dynamicsymbols, ReferenceFrame, Point
from sympy.physics.vector import vpprint, vlatex
from ...dynamics import LagrangesDynamicSystem, HarmonicOscillator, mech_comp

from ..elements import MaterialPoint, Spring, GravitationalForce, Disk, RigidBody2D, Damper, PID, Excitation, Force, base_frame, base_origin
from ...continuous import ContinuousSystem, PlaneStressProblem

import base64
import random
import IPython as IP
import numpy as np
import inspect

from functools import cached_property, lru_cache


from .principles import ComposedSystem, NonlinearComposedSystem, base_frame, base_origin

class RollingDisk(ComposedSystem): 
    m1 = Symbol('m1', positive=True)
    R = Symbol('R', positive=True)
    Omega = Symbol('Omega', positive=True)
    ivar = Symbol('t')
    x = dynamicsymbols('x')
    qs = dynamicsymbols('x')

    def __init__(self,
                 m1=None,
                 R=None,
                 F=None,
                 x=None,
                 qs=None,
                 ivar=Symbol('t'),
                 **kwargs):

        if m1 is not None: self.m1 = m1
        if R is not None: self.R = R
        if x is not None: self.x = x

        if qs is None:
            self.qs = [self.x]
        else:
            self.qs = qs

        self._init_from_components(**kwargs)

    @cached_property
    def components(self):

        components = {}

        self.DiskLin = MaterialPoint(self.m1, self.x, qs=self.qs)
        self.DiskRot = MaterialPoint(self.m1 / 2 * self.R**2, self.x / self.R, qs=self.qs)


        components['_DiskLin'] = self.DiskLin
        components['_DiskRot'] = self.DiskRot

        return components


class DiskMountingBlock(ComposedSystem): 

    m = Symbol('m', positive=True)
    m1 = Symbol('m1', positive=True)
    R = Symbol('R', positive=True)
    Omega = Symbol('Omega', positive=True)
    ivar = Symbol('t')
    x = dynamicsymbols('x')
    qs = dynamicsymbols('x')

    def __init__(self,
                 m=None,
                 m1=None,
                 R=None,
                 x=None,
                 qs=None,
                 ivar=Symbol('t'),
                 **kwargs):


        if m is not None: self.m = m
        if m1 is not None: self.m1 = m1
        if R is not None: self.R = R
        if x is not None: self.x = x

        self._init_from_components(**kwargs)

    @cached_property
    def components(self):

        components = {}

        self.DiskLin = MaterialPoint(self.m, self.x, qs=[self.x])
        self.DiskRot = MaterialPoint(self.m / 2 * self.R**2, self.x / self.R, qs=[self.x])
        self.DiskInner = MaterialPoint(self.m1, self.x, qs = [self.x])

        components['_DiskLin'] = self.DiskLin
        components['_DiskRot'] = self.DiskRot
        components['_DiskInner'] = self.DiskInner
        
        return components

    def get_default_data(self):

        m0 = symbols('m_0', positive=True)

        default_data_dict = {
            self.m1: [
                0.5 * m0, 1 * m0, 2 * m0, 3 * m0, 4 * m0, 5 * m0, 6 * m0,
                7 * m0, 8 * m0, 9 * m0
            ],
        }

        return default_data_dict

    def get_numerical_data(self):

        m0 = symbols('m_0', positive=True)


        default_data_dict = {
            self.m1: [
                0.5 * m0, 1 * m0, 2 * m0, 3 * m0, 4 * m0, 5 * m0, 6 * m0,
                7 * m0, 8 * m0, 9 * m0
            ],
        }

        return default_data_dict







class TwoForcedNonLinearDisks(ComposedSystem):
    scheme_name = 'MDOF_Double_Disk.png'
    real_name = 'roller_tightener.png'
    
    m1=Symbol('m_1', positive=True)
    m2=Symbol('m_2', positive=True)
    kl=Symbol('k_l', positive=True)
    kc=Symbol('k_c', positive=True)
    kr=Symbol('k_r', positive=True)
    R=Symbol('R', positive=True)
    l=Symbol('l', positive=True)
    l_0=Symbol('l_0', positive=True)
    Omega=Symbol('Omega', positive=True)
    omg=Symbol('omega', positive=True)
    ivar=Symbol('t')
    xl=dynamicsymbols('x_l')
    xr=dynamicsymbols('x_r')
    x=dynamicsymbols('x')
    qs=dynamicsymbols('x_l, x_r')
    F_l=Symbol('F_l', positive=True)
    F_r=Symbol('F_r', positive=True)
    
    def __init__(self,
                 m1=None,
                 m2=None,
                 kl=None,
                 kc=None,
                 kr=None,
                 R=None,
                 ivar=Symbol('t'),
                 l=None,
                 l_0=None,
                 xl=None,
                 xr=None,
                 x=None,
                 F_l=None,
                 F_r=None,
                 Omega=None,
                 omg=None,
                 **kwargs):

        if m1 is not None: self.m1=m1
        if m2 is not None: self.m2=m2
        if kl is not None: self.kl = kl
        if kc is not None: self.kc = kc
        if kr is not None: self.kr = kr
        if R is not None: self.R = R
        if l is not None: self.l = l
        if l_0 is not None: self.l_0 = l_0
        if xl is not None: self.xl=xl
        if xr is not None: self.xr=xr
        if x is not None: self.x=x
        if F_l is not None: self.F_l=F_l
        if F_r is not None: self.F_r=F_r
        if omg is not None: self.omg=omg

        self.ivar=ivar
        self.qs=[self.xl, self.xr]
        
        self._init_from_components(**kwargs)

    @cached_property
    def components(self):

        components = {}

        self.left_disk = ForcedNonLinearDisc(m1=self.m1, kl=self.kl, R=self.R, d=self.l, l_0=self.l_0, F=self.F_l, x=self.xl, ivar=self.ivar)
        self.right_disk = ForcedNonLinearDisc(m1=self.m2, kl=self.kr, R=self.R, d=self.l, l_0=self.l_0, F=self.F_r, x=self.xr, ivar=self.ivar)
        self.spring_m = Spring(self.kc, pos1 =self.xl, pos2 = self.xr, qs=self.qs)
#         self.disk1_lin = MaterialPoint(self.m1, self.xl, qs=self.qs) #+ MaterialPoint(self.m1/2*self.R**2, self.xl/self.R, qs=[self.xl])
#         self.disk1_rot = MaterialPoint(self.m1/2*self.R**2, self.xl/self.R, qs=self.qs)
#         self.disk2_lin = MaterialPoint(self.m2, self.xr, qs=self.qs) #+ MaterialPoint(self.m2/2*self.R**2, self.xr/self.R, qs=[self.xr])
#         self.disk2_rot = MaterialPoint(self.m2/2*self.R**2, self.xr/self.R, qs=self.qs)
#         self.spring_l = Spring(self.kl, pos1=(sqrt(self.xl**2 + self.d**2) - self.l_0), qs=self.qs)
#         self.spring_r = Spring(self.kr, pos1=(sqrt(self.xr**2 + self.d**2) - self.l_0), qs=self.qs)
#         self.force_l = Force(self.F_l * cos(self.Omega * self.ivar), pos1=self.xl, qs=self.qs)
#         self.force_r = Force(self.F_r * cos(self.Omega * self.ivar), pos1=self.xr, qs=self.qs)


#         components['_disk_1_lin'] = self.disk1_lin
#         components['_disk_1_rot'] = self.disk1_rot
#         components['_disk_2_lin'] = self.disk2_lin
#         components['_disk_2_rot'] = self.disk2_rot
#         components['_spring_l'] = self.spring_l
#         components['_spring_r'] = self.spring_r
#         components['_force_l']=self.force_l
#         components['_force_r']=self.force_r
        components['_left_disk'] = self.left_disk
        components['_right_disk'] = self.right_disk
        components['_spring_m'] = self.spring_m

        
        return components

    def get_default_data(self):

        m0, k0, l0, F0 = symbols('m_0 k_0 l_0 F_0', positive=True)

        default_data_dict = {
            self.m1: [S.One *m0 * no for no in range(5, 15)],
            self.m2: [S.One *m0 * no for no in range(5, 15)],
            self.l: [self.l_0*S.Half*no for no in range(4,16)],
            self.kl: [S.One *k0 * no for no in range(50, 75)],
            self.kr: [S.One *k0 * no for no in range(50, 75)],
            self.kc: [S.One *k0 * no for no in range(25, 50)],
            self.F_l: [S.One *F0 * no for no in range(15, 30)],
            self.F_r: [S.One *F0 * no for no in range(5, 15)],
            self.xl: [self.x, S.Zero],
            self.xr: [self.x, S.Zero],
        }

        return default_data_dict

    def get_random_parameters(self):

        default_data_dict = self.get_default_data()

        parameters_dict = {
            key: random.choice(items_list)
            for key, items_list in default_data_dict.items()
        }


        if parameters_dict[self.xl] == S.Zero:
            parameters_dict[self.xr] = self.x


        return parameters_dict

    def symbols_description(self):
        self.sym_desc_dict = {
            self.m1: r'Disk Mass',
            self.m2: r'Disk Mass',
            self.kl: 'Left Spring Stiffness',
            self.kr: 'Right Spring Stiffness',
            self.kc: 'Central Spring Stiffness',
            self.l: r'Length',
            self.l_0: r'initial Spring Length',
        }
        return self.sym_desc_dict
    
    
    def static_force(self):
        data=self._given_data
        ans=self.dynamic_force()
        free_coeff=ans.subs({cos(self.Omega*self.ivar):0, sin(self.Omega*self.ivar):0}).subs(data)
        return (free_coeff)
    
    def dynamic_force(self):
        return self.spring_force().expand().doit().n(6)
    
    def spring_force(self):


        sol_dict=self.linearized().subs(self._given_data)._fodes_system.steady_solution.as_dict()
        

        
        F_km=self.spring_m.force().subs(self._given_data).subs(sol_dict).subs(self._given_data)
        
        return F_km
    
    def max_static_force(self):
        return abs(self.static_force())

    def max_dynamic_force(self):
        
        data=self._given_data
        ans=self.dynamic_force()
        amp_cos=ans.subs({cos(self.Omega*self.ivar):1, sin(self.Omega*self.ivar):0}).subs(data)
        

        
        return (Abs(amp_cos) + self.max_static_force())#.subs(data)

    def static_force_pin_diameter(self):
        kt = Symbol('k_t', positive=True)
        Re = Symbol('R_e', positive=True)
        return ((4 * self.max_static_force()) / (pi * kt * Re))**(1 / 2)

    def dynamic_force_pin_diameter(self):
        kt = Symbol('k_t', positive=True)
        Re = Symbol('R_e', positive=True)
        return ((4 * self.max_dynamic_force()) / (pi * kt * Re))**(1 / 2)

    
    def frequency_response_function(self,
                                    frequency=Symbol('Omega', positive=True),
                                    amplitude=Symbol('a')):

        omega = (self.linearized()).natural_frequencies()[0]
        
        
        eps = self.small_parameter()

        exciting_force = self.external_forces()[0]

        comps = exciting_force.atoms(sin, cos)
        exciting_amp = sum([exciting_force.coeff(comp) for comp in comps])
        inertia = self.inertia_matrix()[0]

        return amplitude * (-frequency**2 + omega**2) * inertia + S(
            3) / 4 * eps * amplitude**3 - exciting_amp
    
class TwoDisksWithThreeSprings(ComposedSystem):
    scheme_name = 'ddof_disks_3_springs_scheme.png'
    real_name = 'nonlin_trolley_real.PNG'

    d=Symbol('d', positive=True)
    m1=Symbol('m_1', positive=True)
    m2=Symbol('m_2', positive=True)
    kl=Symbol('k_l', positive=True)
    kc=Symbol('k_c', positive=True)
    kr=Symbol('k_r', positive=True)
    R=Symbol('R', positive=True)
    l_0=Symbol('l_0', positive=True)
    ivar=Symbol('t')
    xl=dynamicsymbols('x_l')
    xr=dynamicsymbols('x_r')
    x=dynamicsymbols('x')
    
    def __init__(self,
                 d=None,
                 m1=None,
                 m2=None,
                 kl=None,
                 kc=None,
                 kr=None,
                 R=None,
                 l_0=None,
                 ivar=Symbol('t'),
                 xl=None,
                 xr=None,
                 x=None,
                 **kwargs):

        if d is not None: self.d = d
        if m1 is not None: self.m1 = m1
        if kl is not None: self.kl = kl
        if R is not None: self.R = R
        if m2 is not None: self.m2 = m2
        if l_0 is not None: self.l_0 = l_0
        if x is not None: self.x = x
        if kc is not None: self.kc = kc
        if kr is not None: self.kr = kr
        if xl is not None: self.xl = xl
        if xr is not None: self.xr = xr

        self.ivar=ivar
        self.qs=[self.xl, self.xr]

        self._init_from_components(**kwargs)

    @cached_property
    def components(self):
        
        components={}

        
        self.Disk1 = RollingDisk(self.m1, R=self.R ,F=0, x=self.xl, qs=self.qs, ivar = self.ivar)
#        self.Disk1_lin = MaterialPoint(self.m1, self.xl, qs=[self.xl])
#        self.Disk1_rot = MaterialPoint(self.m1/2*self.R**2, self.xl/self.R, qs=[self.xl])
        self.spring_l = Spring(self.kl, self.xl, qs=[self.xl])
        self.Disk2 = RollingDisk(self.m2, R=self.R ,F=0, x=self.xr, qs=self.qs, ivar = self.ivar)
#        self.Disk2_lin = MaterialPoint(self.m2, self.xr, qs=[self.xr])
#        self.Disk2_rot = MaterialPoint(self.m2/2*self.R**2, self.xr/self.R, qs=[self.xr])
        self.spring_r = Spring(self.kr,self.xr, qs=[self.xr])
        self.spring_m = Spring(self.kc, pos1 = self.xl, pos2=self.xr, qs=self.qs)
        
        components['_Disk1'] = self.Disk1
#        components['_left_disk_rot'] = self.Disk1_rot
        components['_Disk2'] = self.Disk2
#        components['_right_disk_rot'] = self.Disk2_rot
        components['_spring_m'] = self.spring_m
        components['_spring_r'] = self.spring_r
        components['_spring_l'] = self.spring_l
        
        return components

    def get_default_data(self):

        m0, k0, l0 = symbols('m_0 k_0 l_0', positive=True)

        default_data_dict = {
            self.m1: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.m2: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],

#             self.d: [1 * l0, 2 * l0, S.Half * l0, 4 * S.Half * l0,  S.Half**2 * l0],

            self.kl: [S.Half * k0, S.Half**2 * k0, 1 * k0, 4 * S.Half * k0, 2 * k0],
            self.kr: [S.Half * k0, S.Half**2 * k0, 1 * k0, 4 * S.Half * k0, 2 * k0],
            self.kc: [S.Half * k0, S.Half**2 * k0, 1 * k0, 4 * S.Half * k0, 2 * k0],
        }

        return default_data_dict

    def get_random_parameters(self):

        default_data_dict = self.get_default_data()

        parameters_dict = {
            key: random.choice(items_list)
            for key, items_list in default_data_dict.items()
        }



        return parameters_dict

    def symbols_description(self):
        self.sym_desc_dict = {
            self.m1: r'Disk Mass',
            self.m2: r'Disk Mass',
            self.kl: 'Left Spring Stiffness',
            self.kr: 'Right Spring Stiffness',
            self.kc: 'Central Spring Stiffness',
            self.l: r'Length',
            self.l_0: r'initial Spring Length',
        }
        return self.sym_desc_dict


class ForcedDisksWithSerialSprings(ComposedSystem):
    scheme_name = 'MDOF_Forced_Disks_With_Serial_Springs.PNG'
    real_name = 'three_carriages.PNG'

    r = Symbol('r', positive=True)  #!!! Important - it's dummy variable which is to remove when the LagrangesDynamicSystem inits will be improved
    R = Symbol('R', positive=True)
    m = Symbol('m', positive=True)
    m1 = Symbol('m_1', positive=True)
    m2 = Symbol('m_2', positive=True)
    m3 = Symbol('m_3', positive=True)
    k_ll = Symbol('k_ll', positive=True)
    k_lr = Symbol('k_lr', positive=True)
    k_12l = Symbol('k_12l', positive=True)
    k_12r = Symbol('k_12r', positive=True)
    k_23l = Symbol('k_23l', positive=True)
    k_23r = Symbol('k_23r', positive=True)
    k_rl = Symbol('k_rl', positive=True)
    k_rr = Symbol('k_rr', positive=True)
    F_0 = Symbol('F_0', positive=True)
    Omega = Symbol('Omega', positive=True)
    x_l = dynamicsymbols('x_l')
    x_c = dynamicsymbols('x_c')
    x_r = dynamicsymbols('x_r')
    x_1 = dynamicsymbols('x_1')
    x_2 = dynamicsymbols('x_2')
    x_3 = dynamicsymbols('x_3')
    qs = dynamicsymbols('x_l x_c x_r')
    ivar = Symbol('t')

    def __init__(self,
                 r=None,
                 R=None,
                 m=None,
                 m1=None,
                 m2=None,
                 m3=None,
                 k_ll=None,
                 k_lr=None,
                 k_12l=None,
                 k_12r=None,
                 k_23l=None,
                 k_23r=None,
                 k_rl=None,
                 k_rr=None,
                 F_0=None,
                 Omega=None,
                 x_l=None,
                 x_c=None,
                 x_r=None,
                 x_1=None,
                 x_2=None,
                 x_3=None,
                 ivar=Symbol('t'),
                 **kwargs):

        if r is not None: self.r = r
        if R is not None: self.R = R
        if m is not None: self.m = m
        if m1 is not None: self.m1 = m1
        if m2 is not None: self.m2 = m2
        if m3 is not None: self.m3 = m3
        if k_ll is not None: self.k_ll = k_ll
        if k_lr is not None: self.k_lr = k_lr
        if k_12l is not None: self.k_12l = k_12l
        if k_12r is not None: self.k_12r = k_12r
        if k_23r is not None: self.k_23r = k_23r
        if k_23l is not None: self.k_23l = k_23l
        if k_rl is not None: self.k_rl = k_rl
        if k_rr is not None: self.k_rr = k_rr
        if F_0 is not None: self.F_0 = F_0
        if Omega is not None: self.Omega = Omega
        if x_l is not None: self.x_l = x_l
        if x_c is not None: self.x_c = x_c
        if x_r is not None: self.x_r = x_r
        if x_1 is not None: self.x_1 = x_1
        if x_2 is not None: self.x_2 = x_2
        if x_3 is not None: self.x_3 = x_3

        self.ivar = ivar
        self.qs = [self.x_l, self.x_c, self.x_r]
        self._init_from_components(**kwargs)

    @property
    def components(self):
        components = {}

        self.Disk1 = MaterialPoint(self.m, self.x_l, qs=[self.x_l])
        self.Disk1Reduced = MaterialPoint(self.m/2*self.R**2, self.x_l/self.R, qs=[self.x_l])
        self.LeftSpring = Spring((self.k_ll*self.k_lr)/(self.k_ll+self.k_lr), pos1 = self.x_l, qs = [self.x_l])
        self.LeftForce = Force(-2*self.F_0 * cos(self.Omega * self.ivar), pos1 = self.x_l, qs = [self.x_l])
        self.Block1 = MaterialPoint(self.m1, self.x_l, qs=[self.x_l])
        
        
        self.Disk2 = MaterialPoint(self.m, self.x_c, qs=[self.x_c])
        self.Disk2Reduced = MaterialPoint(self.m/2*self.R**2, self.x_c/self.R, qs=[self.x_c]) 
        self.CentralLeftSpring = Spring((self.k_12l*self.k_12r)/(self.k_12l+self.k_12r), pos1 = self.x_l, pos2 = self.x_c, qs = [self.x_l, self.x_c])
        self.CentralRightSpring = Spring((self.k_23l*self.k_23r)/(self.k_23l+self.k_23r), pos1 = self.x_c, pos2 = self.x_r, qs = [self.x_c, self.x_r])
        self.Block2 = MaterialPoint(self.m2, self.x_c, qs=[self.x_c])
        
        self.Disk3 = MaterialPoint(self.m, self.x_r, qs=[self.x_r])
        self.Disk3Reduced = MaterialPoint(self.m/2*self.R**2, self.x_r/self.R, qs=[self.x_r]) 
        self.RightSpring = Spring((self.k_rl*self.k_rr)/(self.k_rl+self.k_rr), pos1 = self.x_r, qs = [self.x_r])
        self.RightForce = Force(-self.F_0 * cos(self.Omega * self.ivar), pos1 = self.x_r, qs = [self.x_r])
        self.Block3 = MaterialPoint(self.m3, self.x_r, qs=[self.x_r])
        

        components['_disk1'] = self.Disk1
        components['_disk1_reduced'] = self.Disk1Reduced
        components['_left_spring'] = self.LeftSpring
        components['left_force'] = self.LeftForce
        components['_disk2'] = self.Disk2
        components['_disk2_reduced'] = self.Disk2Reduced
        components['_central_left_spring'] = self.CentralLeftSpring
        components['_central_right_spring'] = self.CentralRightSpring
        components['_disk3'] = self.Disk3
        components['_disk3_reduced'] = self.Disk3Reduced
        components['_right_spring'] = self.RightSpring
        components['_right_force'] = self.RightForce
        components['_Block1'] = self.Block1
        components['_Block2'] = self.Block2
        components['_Block3'] = self.Block3
        

        
        return components                        

    def get_default_data(self):

        m0, k0, l0 = symbols('m_0 k_0 l_0', positive=True)

        default_data_dict = {
            self.m1: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.m2: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.m3: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.m: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.k_ll: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_lr: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_12l: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_12r: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_23l: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_23r: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_rl: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_rr: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.x_l: [self.x_1, 0],
            self.x_c: [self.x_1, self.x_2, 0],
            self.x_r: [self.x_2, 0],
        }

        return default_data_dict

    def get_random_parameters(self):

        default_data_dict = self.get_default_data()

        parameters_dict = {
            key: random.choice(items_list)
            for key, items_list in default_data_dict.items()
        }

        if parameters_dict[self.x_l] != self.x_1 or parameters_dict[
                self.x_c] != self.x_1:

            parameters_dict[self.x_l] = self.x_1

        if parameters_dict[self.x_c] != self.x_2 or parameters_dict[
                self.x_r] != self.x_2:

            parameters_dict[self.x_r] = self.x_2

        return parameters_dict

    def get_default_data(self):

        m0, l0 = symbols('m_0 l_0', positive=True)

        default_data_dict = {
            self.m1: [S.Half * m0, 1 * m0, 2 * m0, 1 * m0, S.Half * m0],
            self.m2: [1 * m0, 2 * m0, S.Half * m0, 1 * m0, 2 * m0],
            self.l_1: [1 * l0, 2 * l0, S.Half * l0, 2 * l0, S.Half * l0],
            self.l_2: [1 * l0, 2 * l0, S.Half * l0, 2 * l0, S.Half * l0],
            self.phi_1: [self.phi_u],
            self.phi_2: [self.phi_l],
        }

        return default_data_dict

#TODO
#DO SPRAWDZENIA - PRZENIESIONO Z MODUŁU mdof.py
class ForcedDisksWithParallelSprings(ComposedSystem):

    _default_subs_method='direct'
    scheme_name = 'MDOF_Forced_Disks_With_Parallel_Springs.PNG'
    real_name = 'three_rollers_real.png'

    def __init__(self,
                 R=Symbol('R', positive=True),
                 m=Symbol('m', positive=True),
                 m1=Symbol('m_1', positive=True),
                 m2=Symbol('m_2', positive=True),
                 m3=Symbol('m_3', positive=True),
                 k_l=Symbol('k_l', positive=True),
                 k_cl=Symbol('k_cl', positive=True),
                 k_12=Symbol('k_12', positive=True),
                 k_c12=Symbol('k_c12', positive=True),
                 k_23=Symbol('k_23', positive=True),
                 k_c23=Symbol('k_c23', positive=True),
                 k_r=Symbol('k_r', positive=True),
                 k_cr=Symbol('k_cr', positive=True),
                 F_0=Symbol('F_0', positive=True),
                 Omega=Symbol('Omega', positive=True),
                 x_l=dynamicsymbols('x_l'),
                 x_c=dynamicsymbols('x_c'),
                 x_r=dynamicsymbols('x_r'),
                 x_1=dynamicsymbols('x_1'),
                 x_2=dynamicsymbols('x_2'),
                 qs=dynamicsymbols('x_l x_c x_r'),
                 ivar=Symbol('t'),
                 **kwargs):

        self.m = m
        self.m1 = m1
        self.m2 = m2
        self.m3 = m3
        self.R = R
        self.k_l = k_l
        self.k_cl = k_cl
        self.k_12 = k_12
        self.k_c12 = k_c12
        self.k_23 = k_23
        self.k_c23 = k_c23
        self.k_r = k_r
        self.k_cr = k_cr
        self.x_l = x_l
        self.x_c = x_c
        self.x_r = x_r
        self.x_1 = x_1
        self.x_2 = x_2
        self.Omega = Omega

        self.Disk1 = MaterialPoint(m, x_l, qs=[x_l]) + MaterialPoint(
            m / 2, x_l, qs=[x_l]) + MaterialPoint(m1, x_l, qs=[x_l]) + Spring(
                k_l, pos1=x_l, qs=[x_l]) + Spring(k_l, pos1=x_l, qs=[
                    x_l
                ]) + Spring(k_cl, pos1=x_l, qs=[x_l]) + Force(2*F_0 * cos(Omega * ivar), pos1=x_l, qs=[x_l])

        self.Disk2 = MaterialPoint(m, x_c, qs=[x_c]) + MaterialPoint(
            m / 2, x_c, qs=[x_c]) + MaterialPoint(m2, x_c, qs=[
                x_c
            ]) + Spring(k_12, pos1=x_l, pos2=x_c, qs=[x_l, x_c]) + Spring(
                k_c12, pos1=x_l, pos2=x_c, qs=[x_l, x_c]) + Spring(
                    k_12, pos1=x_l, pos2=x_c, qs=[x_l, x_c]) + Spring(
                        k_23, pos1=x_c, pos2=x_r, qs=[x_c, x_r]) + Spring(
                            k_c23, pos1=x_c, pos2=x_r, qs=[x_c, x_r]) + Spring(
                                k_23, pos1=x_c, pos2=x_r, qs=[x_c, x_r])

        self.Disk3 = MaterialPoint(m, x_r, qs=[x_r]) + MaterialPoint(
            m / 2, x_r, qs=[x_r]) + MaterialPoint(m3, x_r, qs=[x_r]) + Spring(
                k_r, pos1=x_r, qs=[x_r]) + Spring(k_r, pos1=x_r, qs=[
                    x_r
                ]) + Spring(k_cr, pos1=x_r, qs=[x_r]) + Force(F_0 * cos(Omega * ivar), pos1=x_r, qs=[x_r])


        system = self.Disk1 + self.Disk2 + self.Disk3
        super().__init__(system(qs),**kwargs)

    def get_default_data(self):

        m0, k0, l0 = symbols('m_0 k_0 l_0', positive=True)

        default_data_dict = {
            self.m1: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.m2: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.m3: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.m: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],

            self.k_l: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_cl: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_12: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_c12: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_23: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_c23: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_r: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_cr: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],

            self.x_l: [self.x_1],
            self.x_c: [0],
            self.x_r: [self.x_2],
        }

        return default_data_dict
    
#TODO
#DO SPRAWDZENIA - PRZENIESIONO Z MODUŁU mdof.py
class ForcedDisksWithParallelSprings2(ComposedSystem):

    _default_subs_method='direct'
    scheme_name = 'MDOF_Forced_Disks_With_Parallel_Springs.PNG'
    real_name = 'three_rollers_real.png'

    def __init__(self,
                 R=Symbol('R', positive=True),
                 m=Symbol('m', positive=True),
                 m1=Symbol('m_1', positive=True),
                 m2=Symbol('m_2', positive=True),
                 m3=Symbol('m_3', positive=True),
                 k_l=Symbol('k_l', positive=True),
                 k_cl=Symbol('k_cl', positive=True),
                 k_12=Symbol('k_12', positive=True),
                 k_c12=Symbol('k_c12', positive=True),
                 k_23=Symbol('k_23', positive=True),
                 k_c23=Symbol('k_c23', positive=True),
                 k_r=Symbol('k_r', positive=True),
                 k_cr=Symbol('k_cr', positive=True),
                 F_0=Symbol('F_0', positive=True),
                 Omega=Symbol('Omega', positive=True),
                 x_l=dynamicsymbols('x_l'),
                 x_c=dynamicsymbols('x_c'),
                 x_r=dynamicsymbols('x_r'),
                 x_1=dynamicsymbols('x_1'),
                 x_2=dynamicsymbols('x_2'),
                 qs=dynamicsymbols('x_l x_c x_r'),
                 ivar=Symbol('t'),
                 **kwargs):

        self.m = m
        self.m1 = m1
        self.m2 = m2
        self.m3 = m3
        self.R = R
        self.k_l = k_l
        self.k_cl = k_cl
        self.k_12 = k_12
        self.k_c12 = k_c12
        self.k_23 = k_23
        self.k_c23 = k_c23
        self.k_r = k_r
        self.k_cr = k_cr
        self.x_l = x_l
        self.x_c = x_c
        self.x_r = x_r
        self.x_1 = x_1
        self.x_2 = x_2
        self.Omega = Omega

        self.Disk1 = MaterialPoint(m, x_l, qs=[x_l]) + MaterialPoint(
            m / 2, x_l, qs=[x_l]) + MaterialPoint(m1, x_l, qs=[x_l]) + Spring(
                k_l, pos1=x_l, qs=[x_l]) + Spring(k_l, pos1=x_l, qs=[
                    x_l
                ]) + Spring(k_cl, pos1=x_l, qs=[x_l]) + Force(2*F_0 * cos(Omega * ivar), pos1=x_l, qs=[x_l])

        self.Disk2 = MaterialPoint(m, x_c, qs=[x_c]) + MaterialPoint(
            m / 2, x_c, qs=[x_c]) + MaterialPoint(m2, x_c, qs=[
                x_c
            ]) + Spring(k_12, pos1=x_l, pos2=x_c, qs=[x_l, x_c]) + Spring(
                k_c12, pos1=x_l, pos2=x_c, qs=[x_l, x_c]) + Spring(
                    k_12, pos1=x_l, pos2=x_c, qs=[x_l, x_c]) + Spring(
                        k_23, pos1=x_c, pos2=x_r, qs=[x_c, x_r]) + Spring(
                            k_c23, pos1=x_c, pos2=x_r, qs=[x_c, x_r]) + Spring(
                                k_23, pos1=x_c, pos2=x_r, qs=[x_c, x_r])

        self.Disk3 = MaterialPoint(m, x_r, qs=[x_r]) + MaterialPoint(
            m / 2, x_r, qs=[x_r]) + MaterialPoint(m3, x_r, qs=[x_r]) + Spring(
                k_r, pos1=x_r, qs=[x_r]) + Spring(k_r, pos1=x_r, qs=[
                    x_r
                ]) + Spring(k_cr, pos1=x_r, qs=[x_r]) + Force(F_0 * cos(Omega * ivar), pos1=x_r, qs=[x_r])


        system = self.Disk1 + self.Disk2 + self.Disk3
        super().__init__(system(qs),**kwargs)

    def get_default_data(self):

        m0, k0, l0 = symbols('m_0 k_0 l_0', positive=True)

        default_data_dict = {
            self.m1: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.m2: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.m3: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.m: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],

            self.k_l: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_cl: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_12: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_c12: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_23: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_c23: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_r: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_cr: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],

            self.x_l: [self.x_1],
            self.x_c: [0],
            self.x_r: [self.x_2],
        }

        return default_data_dict
    
#DONE Kuba & Michal
class MDoFForcedSimpleDisksWithSerialSprings(ComposedSystem):
    scheme_name = 'three_simple_disks_serial.png'
    real_name = 'three_carriages.PNG'

    R=Symbol('R', positive=True)
    m=Symbol('m', positive=True)
    k_ll=Symbol('k_ll', positive=True)
    k_lr=Symbol('k_lr', positive=True)
    k_12l=Symbol('k_12l', positive=True)
    k_12r=Symbol('k_12r', positive=True)
    k_23l=Symbol('k_23l', positive=True)
    k_23r=Symbol('k_23r', positive=True)
    k_rl=Symbol('k_rl', positive=True)
    k_rr=Symbol('k_rr', positive=True)
    F_0=Symbol('F_0', positive=True)
    Omega=Symbol('Omega', positive=True)
    x_l=dynamicsymbols('x_l')
    x_c=dynamicsymbols('x_c')
    x_r=dynamicsymbols('x_r')
    x_1=dynamicsymbols('x_1')
    x_2=dynamicsymbols('x_2')
    x_3=dynamicsymbols('x_3')    
    
    def __init__(self,
                 R=None,
                 m=None,
                 k_ll=None,
                 k_lr=None,
                 k_12l=None,
                 k_12r=None,
                 k_23l=None,
                 k_23r=None,
                 k_rl=None,
                 k_rr=None,
                 F_0=None,
                 Omega=None,
                 x_l=None,
                 x_c=None,
                 x_r=None,
                 x_1=None,
                 x_2=None,
                 x_3=None,
                 ivar=Symbol('t'),
                 **kwargs):

        if m is not None: self.m = m
        if R is not None: self.R = R
        if k_ll is not None: self.k_ll = k_ll
        if k_lr is not None: self.k_lr = k_lr
        if k_12l is not None: self.k_12l = k_12l
        if k_12r is not None: self.k_12r = k_12r
        if k_23l is not None: self.k_23l = k_23l
        if k_23r is not None: self.k_23r = k_23r
        if k_rl is not None: self.k_rl = k_rl
        if k_rr is not None: self.k_rr = k_rr
        if x_l is not None: self.x_l = x_l
        if x_c is not None: self.x_c = x_c
        if x_r is not None: self.x_r = x_r
        if x_1 is not None: self.x_1 = x_1
        if x_2 is not None: self.x_2 = x_2
        if x_3 is not None: self.x_3 = x_3
        if Omega is not None: self.Omega = Omega
                 #qs=dynamicsymbols('x_l x_c x_r')            
        self.ivar=ivar

        self._init_from_components(**kwargs)
        
    @cached_property
    def components(self):
        components = {}
        
        
        self.Disk1 = MaterialPoint(self.m, self.x_l, qs=[self.x_l])
        self.Disk1Reduced = MaterialPoint(self.m/2*self.R**2, self.x_l/self.R, qs=[self.x_l])
        self.LeftSpring = Spring((self.k_ll*self.k_lr)/(self.k_ll+self.k_lr), pos1 = self.x_l, qs = [self.x_l])
        self.LeftForce = Force(-2*self.F_0 * cos(self.Omega * self.ivar), pos1 = self.x_l, qs = [self.x_l]) 
        
        self.Disk2 = MaterialPoint(self.m, self.x_c, qs=[self.x_c])
        self.Disk2Reduced = MaterialPoint(self.m/2*self.R**2, self.x_c/self.R, qs=[self.x_c]) 
        self.CentralLeftSpring = Spring((self.k_12l*self.k_12r)/(self.k_12l+self.k_12r), pos1 = self.x_l, pos2 = self.x_c, qs = [self.x_l, self.x_c])
        self.CentralRightSpring = Spring((self.k_23l*self.k_23r)/(self.k_23l+self.k_23r), pos1 = self.x_c, pos2 = self.x_r, qs = [self.x_c, self.x_r])
        
        self.Disk3 = MaterialPoint(self.m, self.x_r, qs=[self.x_r])
        self.Disk3Reduced = MaterialPoint(self.m/2*self.R**2, self.x_r/self.R, qs=[self.x_r]) 
        self.RightSpring = Spring((self.k_rl*self.k_rr)/(self.k_rl+self.k_rr), pos1 = self.x_r, qs = [self.x_r])
        self.RightForce = Force(-self.F_0 * cos(self.Omega * self.ivar), pos1 = self.x_r, qs = [self.x_r])
        

        components['_disk1'] = self.Disk1
        components['_disk1_reduced'] = self.Disk1Reduced
        components['_left_spring'] = self.LeftSpring
        components['left_force'] = self.LeftForce
        components['_disk2'] = self.Disk2
        components['_disk2_reduced'] = self.Disk2Reduced
        components['_central_left_spring'] = self.CentralLeftSpring
        components['_central_right_spring'] = self.CentralRightSpring
        components['_disk3'] = self.Disk3
        components['_disk3_reduced'] = self.Disk3Reduced
        components['_right_spring'] = self.RightSpring
        components['_right_force'] = self.RightForce

        
        return components                        
        
    def get_default_data(self):

        m0, k0, l0 = symbols('m_0 k_0 l_0', positive=True)

        default_data_dict = {

            self.m: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            
            self.k_ll: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_lr: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_12l: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_12r: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_23l: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_23r: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_rl: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_rr: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],

            self.x_l: [self.x_1, 0],
            self.x_c: [self.x_1, self.x_2, 0],
            self.x_r: [self.x_2, 0],
            }

        return default_data_dict

    def get_random_parameters(self):

        default_data_dict = self.get_default_data()

        parameters_dict = {
            key: random.choice(items_list)
            for key, items_list in default_data_dict.items()
        }

        if parameters_dict[self.x_l] != self.x_1 or parameters_dict[self.x_c] != self.x_1:

            parameters_dict[self.x_l] = self.x_1

        if parameters_dict[self.x_c] != self.x_2 or parameters_dict[self.x_r] != self.x_2:

            parameters_dict[self.x_r] = self.x_2

        return parameters_dict
    

        
 

#DONE - Kuba & Sabina
class MDoFForcedSimpleDisksWithParallelSprings(ComposedSystem):

    _default_subs_method='direct'
    scheme_name = 'three_simple_disks.png'
    real_name = 'three_rollers_real.png'
    
    R=Symbol('R', positive=True)
    m=Symbol('m', positive=True)
    m1=Symbol('m_1', positive=True)
    m2=Symbol('m_2', positive=True)
    m3=Symbol('m_3', positive=True)
    k_l=Symbol('k_l', positive=True)
    k_cl=Symbol('k_cl', positive=True)
    k_12=Symbol('k_12', positive=True)
    k_c12=Symbol('k_c12', positive=True)
    k_23=Symbol('k_23', positive=True)
    k_c23=Symbol('k_c23', positive=True)
    k_r=Symbol('k_r', positive=True)     
    k_cr=Symbol('k_cr', positive=True)
    F=Symbol('F', positive=True)
    Omega=Symbol('Omega', positive=True)
    x_l=dynamicsymbols('x_l')
    x_c=dynamicsymbols('x_c')
    x_r=dynamicsymbols('x_r')
    x_1=dynamicsymbols('x_1')
    x_2=dynamicsymbols('x_2') 


    def __init__(self,
                 R=None,
                 m=None,
                 m1=None,
                 m2=None,
                 m3=None,
                 k_l=None,
                 k_cl=None,
                 k_12=None,
                 k_c12=None,
                 k_23=None,
                 k_c23=None,
                 k_r=None,
                 k_cr=None,
                 F=None,
                 Omega=None,
                 x_l=None,
                 x_c=None,
                 x_r=None,
                 x_1=None,
                 x_2=None,
                 ivar=Symbol('t'),
                 **kwargs):

        if m is not None: self.m = m
        if m1 is not None: self.m1 = m1
        if m2 is not None: self.m2 = m2
        if m3 is not None: self.m3 = m3
        if R is not None: self.R = R
        if k_l is not None: self.k_l = k_l
        if k_cl is not None: self.k_cl = k_cl
        if k_12 is not None: self.k_12 = k_12
        if k_c12 is not None: self.k_c12 = k_c12
        if k_23 is not None: self.k_23 = k_23
        if k_c23 is not None: self.k_c23 = k_c23
        if k_r is not None: self.k_r = k_r
        if k_cr is not None: self.k_cr = k_cr
        if x_l is not None: self.x_l = x_l
        if x_c is not None: self.x_c = x_c
        if x_r is not None: self.x_r = x_r
        if x_1 is not None: self.x_1 = x_1
        if x_2 is not None: self.x_2 = x_2
        if Omega is not None: self.Omega = Omega
            
        self._init_from_components(**kwargs)
        
    @cached_property
    def components(self):
        components = {}
        


        self.Disk1 = MaterialPoint(self.m, self.x_l, qs=[self.x_l]) 
        self.Disk1Reduced = MaterialPoint(self.m/2*self.R**2, self.x_l/self.R, qs=[self.x_l])
        self.LeftSpring = Spring(self.k_l, pos1=self.x_l, qs=[self.x_l]) + Spring(self.k_l, pos1=self.x_l, qs=[self.x_l]) + Spring(self.k_cl, pos1=self.x_l, qs=[self.x_l]) 
        self.LeftForce = Force(-2*self.F * cos(self.Omega * self.ivar), pos1 = self.x_l, qs = [self.x_l])   # -2 cyz 2
        
        self.Disk2 = MaterialPoint(self.m, self.x_c, qs=[self.x_c]) 
        self.Disk2Reduced = MaterialPoint(self.m/2*self.R**2, self.x_c/self.R, qs=[self.x_c])
        self.CentralLeftSpring = Spring(self.k_12, pos1=self.x_l, pos2=self.x_c, qs=[self.x_l,self.x_r]) + Spring(self.k_c12, pos1=self.x_l, pos2=self.x_c, qs=[self.x_l,self.x_c]) + Spring(self.k_12, pos1=self.x_l, pos2=self.x_c, qs=[self.x_l,self.x_r]) 
        self.CentralRightSpring = Spring(self.k_23, pos1=self.x_c, pos2=self.x_r, qs=[self.x_c,self.x_r]) + Spring(self.k_c23, pos1=self.x_c, pos2=self.x_r, qs=[self.x_c,self.x_r]) + Spring(self.k_23, pos1=self.x_c, pos2=self.x_r, qs=[self.x_c,self.x_r])

        self.Disk3 = MaterialPoint(self.m, self.x_r, qs=[self.x_r]) 
        self.Disk3Reduced = MaterialPoint(self.m/2*self.R**2, self.x_r/self.R, qs=[self.x_r])
        self.RightSpring = Spring(self.k_r, pos1=self.x_r, qs=[self.x_r]) + Spring(self.k_cr, pos1=self.x_r, qs=[self.x_r]) + Spring(self.k_r, pos1=self.x_r, qs=[self.x_r])
        self.RightForce = Force(-2*self.F * cos(self.Omega * self.ivar), pos1=self.x_r, qs=[self.x_r])


        components['_disk1'] = self.Disk1
        components['_disk1_reduced'] = self.Disk1Reduced
        components['_left_spring'] = self.LeftSpring
        components['left_force'] = self.LeftForce
        components['_disk2'] = self.Disk2
        components['_disk2_reduced'] = self.Disk2Reduced
        components['_central_left_spring'] = self.CentralLeftSpring
        components['_central_right_spring'] = self.CentralRightSpring
        components['_disk3'] = self.Disk3
        components['_disk3_reduced'] = self.Disk3Reduced
        components['_right_spring'] = self.RightSpring
        components['_right_force'] = self.RightForce

        
        return components                

    def get_default_data(self):

        m0, k0, l0, = symbols('m_0 k_0 l_0', positive=True)

        default_data_dict = {

            self.m: [1 * m0, 2 * m0, 4 * m0, 3 * m0, 5 * m0, 6 * m0, 7 * m0, 8 * m0, 9 * m0],

            self.k_l: [1 * k0, 2 * k0, 3 * k0, 4 * k0, 5 * k0, 6 * k0, 7 * k0, 8 * k0, 9 * k0],
            self.k_cl: [1 * k0, 2 * k0, 3 * k0, 4 * k0, 5 * k0, 6 * k0, 7 * k0, 8 * k0, 9 * k0],
            self.k_12: [1 * k0, 2 * k0, 3 * k0, 4 * k0, 5 * k0, 6 * k0, 7 * k0, 8 * k0, 9 * k0],
            self.k_c12: [1 * k0, 2 * k0, 3 * k0, 4 * k0, 5 * k0, 6 * k0, 7 * k0, 8 * k0, 9 * k0],
            self.k_23: [1 * k0, 2 * k0, 3 * k0, 4 * k0, 5 * k0, 6 * k0, 7 * k0, 8 * k0, 9 * k0],
            self.k_c23: [1 * k0, 2 * k0, 3 * k0, 4 * k0, 5 * k0, 6 * k0, 7 * k0, 8 * k0, 9 * k0],
            self.k_r: [1 * k0, 2 * k0, 3 * k0, 4 * k0, 5 * k0, 6 * k0, 7 * k0, 8 * k0, 9 * k0],
            self.k_cr: [1 * k0, 2 * k0, 3 * k0, 4 * k0, 5 * k0, 6 * k0, 7 * k0, 8 * k0, 9 * k0],

            self.x_l: [self.x_1, 0],
            self.x_c: [self.x_1, self.x_2],
            self.x_r: [self.x_2, 0],
        }

        return default_data_dict


    def get_random_parameters(self):

        default_data_dict = self.get_default_data()

        parameters_dict = {
            key: random.choice(items_list)
            for key, items_list in default_data_dict.items()
        }

        if parameters_dict[self.x_l] != self.x_1 or parameters_dict[
                self.x_c] != self.x_1:

            parameters_dict[self.x_l] = self.x_1

        if parameters_dict[self.x_c] != self.x_2 or parameters_dict[
                self.x_r] != self.x_2:

            parameters_dict[self.x_r] = self.x_2

        return parameters_dict




#DO ZROBIENIA - PRZENIESIONO Z MODUŁU mdof.py
#  //wydane Michał Szewczyk
class MDoFForcedDisksWithParallelSprings(ComposedSystem):

    _default_subs_method='direct'
    scheme_name = 'MDOF_Forced_Disks_With_Parallel_Springs.PNG'
    real_name = 'three_rollers_real.png'

    def __init__(self,
                 R=Symbol('R', positive=True),
                 m=Symbol('m', positive=True),
                 m1=Symbol('m_1', positive=True),
                 m2=Symbol('m_2', positive=True),
                 m3=Symbol('m_3', positive=True),
                 k_l=Symbol('k_l', positive=True),
                 k_cl=Symbol('k_cl', positive=True),
                 k_12=Symbol('k_12', positive=True),
                 k_c12=Symbol('k_c12', positive=True),
                 k_23=Symbol('k_23', positive=True),
                 k_c23=Symbol('k_c23', positive=True),
                 k_r=Symbol('k_r', positive=True),
                 k_cr=Symbol('k_cr', positive=True),
                 F_0=Symbol('F_0', positive=True),
                 Omega=Symbol('Omega', positive=True),
                 x_l=dynamicsymbols('x_l'),
                 x_c=dynamicsymbols('x_c'),
                 x_r=dynamicsymbols('x_r'),
                 x_1=dynamicsymbols('x_1'),
                 x_2=dynamicsymbols('x_2'),
                 qs=dynamicsymbols('x_l x_c x_r'),
                 ivar=Symbol('t'),
                 **kwargs):

        self.m = m
        self.m1 = m1
        self.m2 = m2
        self.m3 = m3
        self.R = R
        self.k_l = k_l
        self.k_cl = k_cl
        self.k_12 = k_12
        self.k_c12 = k_c12
        self.k_23 = k_23
        self.k_c23 = k_c23
        self.k_r = k_r
        self.k_cr = k_cr
        self.x_l = x_l
        self.x_c = x_c
        self.x_r = x_r
        self.x_1 = x_1
        self.x_2 = x_2
        self.Omega = Omega

        self.Disk1 = MaterialPoint(m, x_l, qs=[x_l]) + MaterialPoint(
            m / 2, x_l, qs=[x_l]) + MaterialPoint(m1, x_l, qs=[x_l]) + Spring(
                k_l, pos1=x_l, qs=[x_l]) + Spring(k_l, pos1=x_l, qs=[
                    x_l
                ]) + Spring(k_cl, pos1=x_l, qs=[x_l]) + Force(2*F_0 * cos(Omega * ivar), pos1=x_l, qs=[x_l])

        self.Disk2 = MaterialPoint(m, x_c, qs=[x_c]) + MaterialPoint(
            m / 2, x_c, qs=[x_c]) + MaterialPoint(m2, x_c, qs=[
                x_c
            ]) + Spring(k_12, pos1=x_l, pos2=x_c, qs=[x_l, x_c]) + Spring(
                k_c12, pos1=x_l, pos2=x_c, qs=[x_l, x_c]) + Spring(
                    k_12, pos1=x_l, pos2=x_c, qs=[x_l, x_c]) + Spring(
                        k_23, pos1=x_c, pos2=x_r, qs=[x_c, x_r]) + Spring(
                            k_c23, pos1=x_c, pos2=x_r, qs=[x_c, x_r]) + Spring(
                                k_23, pos1=x_c, pos2=x_r, qs=[x_c, x_r])

        self.Disk3 = MaterialPoint(m, x_r, qs=[x_r]) + MaterialPoint(
            m / 2, x_r, qs=[x_r]) + MaterialPoint(m3, x_r, qs=[x_r]) + Spring(
                k_r, pos1=x_r, qs=[x_r]) + Spring(k_r, pos1=x_r, qs=[
                    x_r
                ]) + Spring(k_cr, pos1=x_r, qs=[x_r]) + Force(F_0 * cos(Omega * ivar), pos1=x_r, qs=[x_r])


        system = self.Disk1 + self.Disk2 + self.Disk3
        super().__init__(system(qs),**kwargs)

    def get_default_data(self):

        m0, k0, l0 = symbols('m_0 k_0 l_0', positive=True)

        default_data_dict = {
            self.m1: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.m2: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.m3: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.m: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],

            self.k_l: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_cl: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_12: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_c12: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_23: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_c23: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_r: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
            self.k_cr: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],

            self.x_l: [self.x_1, 0],
            self.x_c: [self.x_1, self.x_2],
            self.x_r: [self.x_2, 0],
        }

        return default_data_dict
    
#   def get_default_data(self):

#         m0, k0, l0 = symbols('m_0 k_0 l_0', positive=True)

#         default_data_dict = {
#             self.m1: [S.Half * m0, 1 * m0, 2 * m0, 1 * m0, S.Half * m0],
#             self.m2: [1 * m0, 2 * m0, S.Half * m0, 1 * m0, 2 * m0],
#             self.m3: [1 * m0, 2 * m0, S.Half * m0, 1 * m0, 2 * m0],
#             self.k_l: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
#             self.k_cl: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
#             self.k_12: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
#             self.k_c12: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
#             self.k_23: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
#             self.k_c23: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
#             self.k_r: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],
#             self.k_cr: [1 * k0, 2 * k0, S.Half * k0, 2 * k0, S.Half * k0],

#             self.x_l: [self.x_1, 0],
#             self.x_c: [self.x_1, self.x_2, 0],
#             self.x_r: [self.x_2, 0],
#         }

#         return default_data_dict
#
#    def get_random_parameters(self):
#
#        default_data_dict = self.get_default_data()
#
#        parameters_dict = {
#            key: random.choice(items_list)
#            for key, items_list in default_data_dict.items()
#        }
#
#        if parameters_dict[self.x_l] != self.x_1 or parameters_dict[
#                self.x_c] != self.x_1:
#
#            parameters_dict[self.x_l] = self.x_1
#
#        if parameters_dict[self.x_c] != self.x_2 or parameters_dict[
#                self.x_r] != self.x_2:
#
#            parameters_dict[self.x_r] = self.x_2
#
#        return parameters_dict
#    

#DO ZROBIENIA - PRZENIESIONO Z MODUŁU mdof.py
#  //wydane Maja
class MDoFForcedDisksWithSerialSprings(ComposedSystem):
    scheme_name = 'MDOF_Forced_Disks_With_Serial_Springs.PNG'
    real_name = 'three_carriages.PNG'

    def __init__(self,
                 r=Symbol('r', positive=True), #!!! Important - it's dummy variable which is to remove when the LagrangesDynamicSystem inits will be improved
                 R=Symbol('R', positive=True),
                 m=Symbol('m', positive=True),
                 m1=Symbol('m_1', positive=True),
                 m2=Symbol('m_2', positive=True),
                 m3=Symbol('m_3', positive=True),
                 k_ll=Symbol('k_ll', positive=True),
                 k_lr=Symbol('k_lr', positive=True),
                 k_12l=Symbol('k_12l', positive=True),
                 k_12r=Symbol('k_12r', positive=True),
                 k_23l=Symbol('k_23l', positive=True),
                 k_23r=Symbol('k_23r', positive=True),
                 k_rl=Symbol('k_rl', positive=True),
                 k_rr=Symbol('k_rr', positive=True),
                 F_0=Symbol('F_0', positive=True),
                 Omega=Symbol('Omega', positive=True),
                 x_l=dynamicsymbols('x_l'),
                 x_c=dynamicsymbols('x_c'),
                 x_r=dynamicsymbols('x_r'),
                 x_1=dynamicsymbols('x_1'),
                 x_2=dynamicsymbols('x_2'),
                 x_3=dynamicsymbols('x_3'),
                 qs=dynamicsymbols('x_l x_c x_r'),
                 ivar=Symbol('t'),
                 **kwargs):

        self.m = m
        self.m1 = m1
        self.m2 = m2
        self.m3 = m3
        self.R = R
        self.k_ll = k_ll
        self.k_lr = k_lr
        self.k_12l = k_12l
        self.k_12r = k_12r
        self.k_23l = k_23l
        self.k_23r = k_23r
        self.k_rl = k_rl
        self.k_rr = k_rr
        self.x_l = x_l
        self.x_c = x_c
        self.x_r = x_r
        self.x_1 = x_1
        self.x_2 = x_2
        self.x_3 = x_3
        self.Omega = Omega

        self.Disk1 =  MaterialPoint(m, x_l, qs = [x_l]) + MaterialPoint(m/2, x_l, qs = [x_l]) + MaterialPoint(m1, x_l, qs = [x_l]) + Spring((k_ll*k_lr)/(k_ll+k_lr), pos1 = x_l, qs = [x_l]) + Force(-2*F_0 * cos(Omega * ivar), pos1 = x_l, qs = [x_l])
        self.Disk2 =  MaterialPoint(m, x_c, qs = [x_c]) + MaterialPoint(m/2, x_c, qs = [x_c]) + MaterialPoint(m2, x_c, qs = [x_c]) + Spring((k_12l*k_12r)/(k_12l+k_12r), pos1 = x_l, pos2 = x_c, qs = [x_l, x_c]) + Spring((k_23l*k_23r)/(k_23l+k_23r), pos1 = x_c, pos2 = x_r, qs = [x_c, x_r])
        self.Disk3 =  MaterialPoint(m, x_r, qs = [x_r]) + MaterialPoint(m/2, x_r, qs = [x_r]) + MaterialPoint(m3, x_r, qs = [x_r]) + Spring((k_rl*k_rr)/(k_rl+k_rr), pos1 = x_r, qs = [x_r]) + Force(-F_0 * cos(Omega * ivar), pos1 = x_r, qs = [x_r])


        
        
        system = self.Disk1 + self.Disk2 + self.Disk3
        super().__init__(system(qs),**kwargs)

    def get_default_data(self):

        m0, k0, l0 = symbols('m_0 k_0 l_0', positive=True)

        default_data_dict = {
            self.m1: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.m2: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.m3: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            self.m: [S.Half * m0, 1 * m0, 2 * m0, 4 * m0, S.Half**2 * m0],
            
            self.k_ll: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_lr: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_12l: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_12r: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_23l: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_23r: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_rl: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],
            self.k_rr: [1 * k0, 2 * k0, S.Half * k0, 4 * k0, S.Half**2 * k0],

            self.x_l: [self.x_1, 0],
            self.x_c: [self.x_1, self.x_2, 0],
            self.x_r: [self.x_2, 0],
            }

        return default_data_dict

    def get_random_parameters(self):

        default_data_dict = self.get_default_data()

        parameters_dict = {
            key: random.choice(items_list)
            for key, items_list in default_data_dict.items()
        }

        if parameters_dict[self.x_l] != self.x_1 or parameters_dict[self.x_c] != self.x_1:

            parameters_dict[self.x_l] = self.x_1

        if parameters_dict[self.x_c] != self.x_2 or parameters_dict[self.x_r] != self.x_2:

            parameters_dict[self.x_r] = self.x_2

        return parameters_dict
    
