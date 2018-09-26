#=========================================================================
# TestSinkFixedDelay.py
#=========================================================================

from pymtl        import *
from pclib.test   import TestRandomDelay
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.test.TestSimpleNetSink import TestSimpleNetSink
#-------------------------------------------------------------------------
# TestNetSink
#-------------------------------------------------------------------------
# This class will sink network messages from a val/rdy interface and
# compare them to a predefined list of network messages. Each network
# message has route information, unique sequence number and payload
# information
class TestSinkFixedDelay( Model ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( s, dtype, msgs, fixed_delay = 0 ):

    s.in_  = InValRdyBundle( dtype )
    s.done = OutPort       ( 1          )

    s.sink  = TestSimpleNetSink( dtype, msgs )

    s.connect( s.in_.msg,   s.sink.in_.msg  )
    s.connect( s.in_.rdy,   s.sink.in_.rdy   )
    s.connect( s.sink.done, s.done          )

    s.cnt = fixed_delay
    # TODO: set s.sink.in_.val, 
    @s.combinational
    def setValRdy():
      if s.cnt == 0:
        s.sink.in_.val.value = s.in_.val
        s.in_.rdy.value      = s.sink.in_.rdy
      else:
        s.sink.in_.val.value = 0
        s.in_.rdy.value       = 0

    @s.tick
    def decrCounter():
      if s.cnt > 0:
        s.cnt = s.cnt - 1
      else:
        s.cnt = 0

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------
  def line_trace( s ):
    return "{}".format( s.in_ )