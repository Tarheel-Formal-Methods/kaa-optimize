import sympy as sp
import numpy as np

from kaa.bundle import Bundle
from kaa.model import Model

class SIR(Model):

  def __init__(self, delta=0.1, init_box= ((0.79,0.8), (0.19,0.2), (0.00099, 0.001)) ):
      s, i, r = sp.Symbol('s'), sp.Symbol('i'), sp.Symbol('r')

      ds = s - (0.34*s*i)*delta;
      di = i + (0.34*s*i - 0.05*i)*delta;
      dr = r + (0.05*i)*delta;

      dyns = (ds, di, dr)
      vars = (s, i, r) #In predetermined order
      sys_dim = len(vars)

      num_direct = 5
      num_temps = 3

      L = np.zeros((num_direct, sys_dim))
      T = np.zeros((num_temps, sys_dim))

      #Directions matrix
      L[0][0] = 1  #[1 0 0 ]^T
      L[1][1] = 1  #[0 1 0 ]^T
      L[2][2] = 1  #[0 0 1 ]^T``
      L[3][0] = 1; L[3][1] = 0.5;
      L[4][0] = 0.5; L[4][2] = 0.5;

      #Template matrix
      T[0][0] = 0
      T[0][1] = 1
      T[0][2] = 2
      T[1][0] = 1; T[1][1] = 2; T[1][2] = 3;
      T[2][0] = 2; T[2][1] = 3; T[2][2] = 4;

      offu = np.zeros(num_direct)
      offl = np.zeros(num_direct)

      offu[3] = 1; offl[3] = 0;
      offu[4] = 1; offl[4] = 0;

      super().__init__(dyns, vars, T, L, init_box, offl, offu, name="SIR")

class SIR_UnitBox(Model):

  def __init__(self, delta=0.1, init_box= ((0.79,0.8), (0.19,0.2), (0.00099, 0.001))):

      s, i, r = sp.Symbol('s'), sp.Symbol('i'), sp.Symbol('r')

      ds = s - (0.34*s*i)*delta;
      di = i + (0.34*s*i - 0.05*i)*delta;
      dr = r + 0.05*i*delta;

      dyns = (ds, di, dr)
      vars = (s, i, r) #In predetermined order
      sys_dim = len(vars)

      num_direct = 3
      num_temps = 1

      L = np.zeros((num_direct, sys_dim))
      T = np.zeros((num_temps, sys_dim))

      #Directions matrix
      L[0][0] = 1  #[1 0 0 ]^T
      L[1][1] = 1  #[0 1 0 ]^T
      L[2][2] = 1  #[0 0 1 ]^T
      #L[3][0] = 1; L[3][1] = 0.5;
      #L[4][0] = 0.5; L[4][2] = 0.5;
      #Template matrix
      T[0][0] = 0
      T[0][1] = 1
      T[0][2] = 2
     #T[1][0] = 1; T[1][1] = 2; T[1][2] = 3;
     #T[2][0] = 2; T[2][1] = 3; T[2][2] = 4;

      offu = np.zeros(num_direct)
      offl = np.zeros(num_direct)

      super().__init__(dyns, vars, T, L, init_box, offl, offu, name="SIR")
