#=========================================================================
# BusNetDpathPRTL.py
#=========================================================================
# This model implements 4-port (configurable) simple bus network.

from pymtl         import *
from pclib.ifcs    import NetMsg, InValRdyBundle
from pclib.rtl     import NormalQueue
from pclib.rtl     import Bus

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK: Include components
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

class BusNetDpathPRTL( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, payload_nbits ):

    # Parameters
    # Your design does not need to support other values

    num_ports    = 4
    opaque_nbits = 8

    # Interface

    msg_type = NetMsg( num_ports, 2**opaque_nbits, payload_nbits )

    s.in_    = InValRdyBundle[num_ports]( msg_type )

    s.out_msg  = OutPort[num_ports]( msg_type )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # LAB TASK:
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    # Constants
    DEST_HIGH = payload_nbits + 12
    DEST_LOW = DEST_HIGH - clog2(num_ports)
    QUEUE_NUM_ENTRIES = 2

    # Control signals (ctrl -> dpath)
    s.bus_sel = InPort(clog2(num_ports))
    s.inq_rdy = InPort(num_ports)

    # Status signals (dpath -> ctrl)
    s.inq_val = OutPort(num_ports)
    s.inq_dests = [OutPort(clog2(num_ports)) for _ in range(num_ports)]

    # Queues
    s.queues = []
    for i in range(num_ports):
      queue = NormalQueue(QUEUE_NUM_ENTRIES, msg_type)
      # Enq val/rdy/msg
      s.connect(queue.enq, s.in_[i])
      # Deq val/rdy
      s.connect(queue.deq.val, s.inq_val[i])
      s.connect(queue.deq.rdy, s.inq_rdy[i])
      # Deq dest
      s.connect(queue.deq.msg[DEST_LOW:DEST_HIGH], s.inq_dests[i])
      # Append
      s.queues.append(queue)

    # Bus
    s.bus = Bus(num_ports, msg_type)
    s.connect(s.bus.sel, s.bus_sel)
    for i in range(num_ports):
      # Deq msg
      s.connect(s.bus.in_[i], s.queues[i].deq.msg)
      # Result
      s.connect(s.bus.out[i], s.out_msg[i])
