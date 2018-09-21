#=========================================================================
# BusNetCtrlPRTL.py
#=========================================================================
# This model implements 4-port (configurable) simple bus network.

from pymtl     import *

from pclib.rtl     import RoundRobinArbiterEn

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK: Include components
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

class BusNetCtrlPRTL( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s ):

    # Parameters
    # Your design does not need to support other values

    num_ports = 4

    # Interface

    s.out_val  = OutPort[num_ports]( 1 )
    s.out_rdy  = InPort [num_ports]( 1 )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # LAB TASK:
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    # Control signals (ctrl -> dpath)
    s.bus_sel = OutPort(clog2(num_ports))
    s.inq_rdy = OutPort(num_ports)

    # Status signals (dpath -> ctrl)
    s.inq_val = InPort(num_ports)
    s.inq_dests = [InPort(clog2(num_ports)) for _ in range(num_ports)]

    # Wires
    s.enable = Wire(1)
    s.grants = Wire(num_ports)

    # Round Robin Arbiter
    s.arbiter = m = RoundRobinArbiterEn(num_ports)
    s.connect_pairs(
      m.en,     s.enable,
      m.reqs,   s.inq_val,
      m.grants, s.grants
    )

    @s.combinational
    def cloudA():
      if   s.grants[0]:
        s.bus_sel.value = 0
      elif s.grants[1]:
        s.bus_sel.value = 1
      elif s.grants[2]:
        s.bus_sel.value = 2
      elif s.grants[3]:
        s.bus_sel.value = 3

    @s.combinational
    def cloudB():
      s.out_val[0].value = 0
      s.out_val[1].value = 0
      s.out_val[2].value = 0
      s.out_val[3].value = 0
      if   (s.grants[0] and s.inq_dests[0] == 0) or \
           (s.grants[1] and s.inq_dests[1] == 0) or \
           (s.grants[2] and s.inq_dests[2] == 0) or \
           (s.grants[3] and s.inq_dests[3] == 0):
        s.out_val[0].value = 1
      elif (s.grants[0] and s.inq_dests[0] == 1) or \
           (s.grants[1] and s.inq_dests[1] == 1) or \
           (s.grants[2] and s.inq_dests[2] == 1) or \
           (s.grants[3] and s.inq_dests[3] == 1):
        s.out_val[1].value = 1
      elif (s.grants[0] and s.inq_dests[0] == 2) or \
           (s.grants[1] and s.inq_dests[1] == 2) or \
           (s.grants[2] and s.inq_dests[2] == 2) or \
           (s.grants[3] and s.inq_dests[3] == 2):
        s.out_val[2].value = 1
      elif (s.grants[0] and s.inq_dests[0] == 3) or \
           (s.grants[1] and s.inq_dests[1] == 3) or \
           (s.grants[2] and s.inq_dests[2] == 3) or \
           (s.grants[3] and s.inq_dests[3] == 3):
        s.out_val[3].value = 1

    @s.combinational
    def cloudC():
      s.enable.value = (s.out_rdy[0] and s.out_val[0]) or \
                       (s.out_rdy[1] and s.out_val[1]) or \
                       (s.out_rdy[2] and s.out_val[2]) or \
                       (s.out_rdy[3] and s.out_val[3])

    @s.combinational
    def cloudD():
      if s.enable:
        s.inq_rdy.value = s.grants
      else:
        s.inq_rdy.value = 0
