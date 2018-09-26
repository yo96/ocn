#=========================================================================
# RingNetRTL_test.py
#=========================================================================
from __future__     import print_function

import pytest
import random
import hypothesis
from hypothesis import strategies as st

random.seed(0xdeadbeef)

from pymtl          import *
from pclib.test     import TestSource, TestNetSink, mk_test_case_table
from pclib.ifcs     import NetMsg
from net.NetFL import NetFL
                    
from TrafficPatternTest import *

from net.RingNetRTL import RingNetRTL

#-------------------------------------------------------------------------
# Reuse tests from FL model
#-------------------------------------------------------------------------

from NetFL_test import test_case_table
from TestHelper import mk_net_msgs
from TestSinkFixedDelay import TestSinkFixedDelay

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  # Constructor

  def __init__( s, NetModel, src_msgs,  sink_msgs, src_delay, sink_delay,
                num_routers, num_ports, opaque_nbits, payload_nbits,
                dump_vcd=False, test_verilog=False ):

    s.src_msgs      = src_msgs
    s.sink_msgs     = sink_msgs
    s.src_delay     = src_delay
    s.sink_delay    = sink_delay
    s.num_ports     = num_ports
    s.num_routers   = num_routers
    
    s.opaque_nbits  = opaque_nbits
    s.payload_nbits = payload_nbits
    s.addr_nbits    = clog2(num_routers)
    

    msg_type = NetMsg( num_routers, 2**opaque_nbits, payload_nbits )

    s.src  = [ TestSource ( msg_type, s.src_msgs[x],  s.src_delay[x]  ) for x in xrange(num_routers) ]
    s.net  = NetModel
    s.sink = [ TestSinkFixedDelay( msg_type, s.sink_msgs[x], s.sink_delay[x] ) for x in xrange(num_routers) ]

    # Dump VCD
    if dump_vcd:
      s.net.vcd_file = dump_vcd
      if hasattr(s.net, 'inner'):
        s.net.inner.vcd_file = dump_vcd

    # Translation
    if test_verilog:
      s.net = TranslationTool( s.net )

    # Connect
    for i in xrange(num_routers):
      s.connect( s.net.in_[i], s.src[i].out  )
      s.connect( s.net.out[i], s.sink[i].in_ )

  # Done

  def done( s ):
    done_flag = 1
    for i in xrange(s.num_routers):
      done_flag &= s.src[i].done and s.sink[i].done
    return done_flag

  # Line-trace

  def line_trace( s ):
    in_ = '|'.join( [ x.out.to_str( "%02s:%1s>%1s" % (  x.out.msg[s.payload_nbits:s.payload_nbits+s.opaque_nbits],
                                                        x.out.msg[s.payload_nbits+s.opaque_nbits:s.payload_nbits+s.opaque_nbits+s.addr_nbits],
                                                        x.out.msg[s.payload_nbits+s.opaque_nbits+s.addr_nbits:s.payload_nbits+s.opaque_nbits+s.addr_nbits*2] ) )
                                        for x in s.src  ] )
    out = '|'.join( [ x.in_.to_str( "%02s:%1s>%1s" % (  x.in_.msg[s.payload_nbits:s.payload_nbits+s.opaque_nbits],
                                                        x.in_.msg[s.payload_nbits+s.opaque_nbits:s.payload_nbits+s.opaque_nbits+s.addr_nbits],
                                                        x.in_.msg[s.payload_nbits+s.opaque_nbits+s.addr_nbits:s.payload_nbits+s.opaque_nbits+s.addr_nbits*2] ) )
                                        for x in s.sink ] )
    return in_ + ' >>> ' + s.net.line_trace() + ' >>> ' + out

#-------------------------------------------------------------------------
# run_net_test
#-------------------------------------------------------------------------

def run_net_test( NetModel, src_delay, sink_delay, test_msgs,
                  num_routers = 4, num_ports = 5,
                  opaque_nbits = 8, payload_nbits = 32,
                  dump_vcd = False, test_verilog = False):

  # src/sink msgs

  src_msgs  = test_msgs[0]
  sink_msgs = test_msgs[1]

  # Instantiate and elaborate the model

  model = TestHarness( NetModel, src_msgs, sink_msgs, src_delay, sink_delay,
                       num_routers, num_ports, opaque_nbits, payload_nbits,
                       dump_vcd, test_verilog )

  model.vcd_file     = dump_vcd
  model.test_verilog = test_verilog
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print()

  sim.reset()
  # TODO: Change back to 50000
  while not model.done() and sim.ncycles < 10000:
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

  # Check for success

  if not model.done():
    raise AssertionError( "Simulation did not complete!" )

#-------------------------------------------------------------------------------
# End of Test Harness
#-------------------------------------------------------------------------------

# Test default configuration
@pytest.mark.parametrize( **test_case_table )
def test_Ring_default( test_params, dump_vcd, test_verilog ):
  run_net_test( RingNetRTL(), 
                test_params.src_delay, test_params.sink_delay, test_params.msgs,
                num_routers = 4, num_ports = 5, 
                opaque_nbits = 8, payload_nbits = 32,
                dump_vcd = False, test_verilog = False )

@pytest.mark.parametrize( **test_case_table )
def test_Ring_greedy( test_params, dump_vcd, test_verilog ):
  run_net_test( RingNetRTL(routing_algorithm='greedy'), 
                test_params.src_delay, test_params.sink_delay, test_params.msgs,
                num_routers = 4, num_ports = 5,
                opaque_nbits = 8, payload_nbits = 32,
                dump_vcd = dump_vcd, test_verilog = test_verilog)

# Hypothesis test
@hypothesis.strategies.composite
def net_test_msg(draw,nrouter):
  src        = draw(st.integers(0,nrouter-1))
  dest       = draw(st.integers(0,nrouter-1))
  opaque     = draw(st.integers(1,0xff      ))
  payload    = draw(st.integers(0,0xffffffff))
  return (src,dest,opaque,payload)

@hypothesis.given(
  #num_routers  = st.integers( 4,5    ),
  src_delay    = st.integers( 0,10   ),
  sink_delay   = st.integers( 0,10   ),
  test_msgs    = st.data() )
#@hypothesis.settings(timeout=180)
#phases=[hypothesis.Phase.generate, hypothesis.Phase.shrink]
@hypothesis.settings(timeout=180,max_examples=500)
def test_ring_hypothesis(src_delay, sink_delay,
                         test_msgs):
  nrouters = 6
  msgs     = test_msgs.draw(
              st.lists( net_test_msg(nrouters),
                        min_size=20, max_size=2000 ) )

  src_delay_lst = [src_delay for _ in range(nrouters)]
  sink_delay_lst= [sink_delay for _ in range(nrouters)]
  hypothesis.event( "#routers: %d, #packets: %d\n" % (nrouters,len(msgs)) )

  run_net_test( RingNetRTL( num_routers = nrouters, routing_algorithm = 'even-odd' ), 
                src_delay_lst, sink_delay_lst, 
                mk_net_msgs(nrouters,msgs),
                num_routers = nrouters, num_ports = 3, 
                opaque_nbits = 8, payload_nbits = 32,
                dump_vcd = False, test_verilog = False )

  """
Falsifying example: test_ring_hypothesis(src_delay=0, sink_delay=1, test_msgs=data(...))
Draw 1: 
[(0, 1, 8, 117901063), 
 (0, 0, 2, 16843009),
 (1, 1, 2, 251724033),
 (1, 4, 7, 65798),
 (0, 1, 3, 100663553),
 (4, 1, 2, 50397441),
 (1, 4, 8, 117506305),
 (1, 5, 2, 117900546),
 (1, 2, 2, 16842757),
 (1, 2, 2, 16843520),
 (2, 5, 2, 16843271),
 (2, 0, 2, 16909569),
 (4, 3, 2, 17104897),
 (1, 5, 2, 16975363),
 (2, 5, 2, 16843527),
 (2, 3, 2, 16843010),
 (2, 5, 2, 16844036),
 (2, 0, 2, 16843782),
 (0, 3, 2, 16974849),
 (1, 3, 2, 17040899),
 (3, 4, 2, 83952385),
 (0, 4, 2, 257),
 (0, 5, 11, 33554689),
 (5, 2, 2, 83953409),
 (0, 4, 5, 16843009),
 (1, 0, 3, 16843009),
 (1, 0, 6, 16843009),
 (0, 4, 7, 100860161),
 (4, 1, 8, 67436801),
 (5, 3, 2, 67568897),
 (5, 3, 2, 17039617),
 (5, 5, 2, 16908545),
 (4, 5, 2, 16843009),
 (1, 1, 4, 65793),
 (4, 2, 6, 16843009),
 (4, 5, 7, 100860161),
 (2, 4, 2, 84082945),
 (5, 0, 2, 16974081),
 (1, 3, 2, 117573376),
 (2, 2, 2, 17236997),
 (2, 2, 2, 50397441),
 (5, 4, 5, 50397441),
 (2, 1, 3, 65793),
 (4, 4, 2, 65793),
 (4, 5, 4, 16843009),
 (5, 2, 8, 33882372),
 (3, 4, 2, 84017409),
 (0, 3, 6, 16843009),
 (4, 5, 2, 16843009),
 (0, 1, 2, 16843009),
 (0, 3, 10, 16843009),
 (1, 1, 2, 16843009),
 (1, 2, 2, 16843009),
 (1, 0, 2, 16843009),
 (2, 3, 2, 16843009),
 (4, 0, 2, 16843009),
 (1, 4, 2, 16843009),
 (1, 3, 2, 16843009),
 (1, 3, 2, 16843009),
 (5, 0, 2, 16843009),
 (0, 3, 2, 17170689),
 (2, 0, 2, 65793),
 (2, 1, 2, 16843009),
 (4, 3, 2, 16843009),
 (5, 2, 2, 16843009),
 (3, 0, 2, 16843009),
 (2, 2, 2, 16843009),
 (3, 3, 2, 16843009),
 (5, 5, 2, 16843009),
 (3, 0, 2, 16843009),
 (3, 1, 2, 16843009),
 (5, 3, 2, 16843014),
 (2, 0, 2, 16843009),
 (3, 0, 2, 16843009),
 (5, 3, 2, 16843009),
 (5, 2, 2, 16908545),
 (1, 4, 2, 17760513),
 (1, 3, 2, 16843009),
 (1, 3, 2, 16843009),
 (4, 4, 2, 16843009),
 (0, 1, 2, 16843009),
 (5, 5, 2, 16843009),
 (5, 0, 2, 16843009),
 (5, 0, 2, 16843009),
 (0, 3, 2, 17236225),
 (2, 3, 2, 16843009),
 (1, 3, 2, 16843009),
 (2, 3, 2, 16843009),
 (5, 0, 2, 16843009),
 (5, 3, 2, 16843009),
 (1, 2, 2, 16843009),
 (5, 0, 2, 16843009),
 (3, 1, 2, 16843009),
 (3, 1, 2, 16843009),
 (2, 4, 2, 16843018),
 (3, 1, 2, 16843009),
 (2, 4, 2, 16843009),
 (3, 4, 2, 16843009),
 (4, 3, 2, 16843265),
 (5, 1, 2, 16843009),
 (0, 5, 2, 16843009),
 (3, 5, 2, 16843009),
 (1, 2, 2, 16843009),
 (4, 3, 2, 16843009),
 (2, 0, 2, 16843009),
 (4, 0, 2, 17305345),
 (0, 1, 2, 16843009),
 (4, 1, 2, 16843009),
 (1, 1, 2, 16843009),
 (4, 1, 2, 16843009),
 (4, 0, 2, 16843009),
 (4, 1, 2, 16843009),
 (2, 2, 2, 16843009),
 (2, 5, 2, 16843009),
 (5, 5, 2, 16843009),
 (2, 2, 2, 16843009),
 (2, 3, 2, 16843009),
 (5, 3, 2, 16974081),
 (3, 1, 2, 17432833),
 (2, 2, 2, 16843009),
 (3, 2, 2, 16843009),
 (4, 5, 2, 16843009),
 (2, 0, 2, 16843009),
 (1, 5, 2, 16843009),
 (3, 2, 2, 16843009),
 (3, 0, 2, 17039617),
 (3, 5, 2, 16843009),
 (2, 4, 2, 16843009),
 (2, 0, 2, 16843009),
 (1, 0, 2, 16843009),
 (3, 5, 2, 16843009),
 (5, 3, 2, 16843009),
 (5, 3, 2, 16843009),
 (5, 2, 2, 16843009),
 (4, 2, 4, 16843009),
 (3, 3, 2, 16843009),
 (1, 4, 2, 16843009),
 (1, 3, 2, 16843009),
 (0, 1, 2, 16843009),
 (3, 2, 2, 16843009),
 (4, 1, 2, 16843009),
 (5, 5, 2, 16843009),
 (5, 4, 2, 16843009),
 (3, 5, 2, 16843009),
 (2, 2, 2, 16843009),
 (5, 2, 2, 16843009),
 (0, 0, 2, 16843009),
 (0, 4, 2, 16843009),
 (0, 2, 2, 16843009),
 (1, 3, 2, 16843009),
 (2, 0, 2, 16843008),
 (1, 4, 2, 16843009),
 (1, 4, 2, 16843009),
 (1, 5, 2, 16843009),
 (0, 2, 2, 16843017),
 (3, 4, 2, 16843009),
 (4, 1, 2, 16843009),
 (4, 4, 2, 16843009),
 (0, 5, 2, 16843013),
 (5, 3, 2, 16843009),
 (4, 0, 2, 16843009),
 (2, 4, 2, 16843009),
 (2, 5, 2, 16777473),
 (2, 0, 2, 50397441),
 (3, 3, 2, 16843009),
 (2, 2, 7, 16843009),
 (5, 5, 2, 16843009),
 (0, 4, 2, 17301762),
 (3, 4, 2, 16843009),
 (1, 1, 2, 16843009),
 (5, 3, 4, 16843009), 
 (2, 3, 2, 16843009), 
 (0, 4, 2, 16843009), 
 (4, 3, 2, 16974081), 
 (5, 4, 2, 65793), 
 (0, 3, 2, 16843009), 
 (0, 1, 2, 16843009), 
 (0, 4, 2, 16843009)]
  """