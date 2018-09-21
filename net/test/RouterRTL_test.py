#=========================================================================
# RouterRTL_test.py
#=========================================================================

from __future__    import print_function

import pytest

from pymtl         import *
from pclib.test    import TestSource, TestNetSink, mk_test_case_table
from pclib.ifcs    import NetMsg

from net.RouterRTL import RouterRTL
from NetFL_test import mk_msg
from RouterTest1 import *

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, RouterModel, router_id, src_msgs, sink_msgs, src_delay, sink_delay,
                num_ports, opaque_nbits, payload_nbits,
                dump_vcd=False, test_verilog=False ):

    s.src_msgs   = src_msgs
    s.sink_msgs  = sink_msgs
    s.src_delay  = src_delay
    s.sink_delay = sink_delay

    msg_type = NetMsg( num_ports, 2**opaque_nbits, payload_nbits )

    s.src    = [ TestSource  ( msg_type, s.src_msgs[x],  s.src_delay  )
                 for x in xrange( 3 ) ]

    s.router = RouterModel

    s.sink   = [ TestNetSink ( msg_type, s.sink_msgs[x], s.sink_delay )
                 for x in xrange( 3 ) ]

    # Dump VCD

    if dump_vcd:
      s.router.vcd_file = dump_vcd
      if hasattr(s.router, 'inner'):
        s.router.inner.vcd_file = dump_vcd


    # Translation

    if test_verilog:
      s.router = TranslationTool( s.router )

    # Connect

    s.connect( s.router.in0 , s.src[0].out  )
    s.connect( s.router.out0, s.sink[0].in_ )

    s.connect( s.router.in1 , s.src[1].out  )
    s.connect( s.router.out1, s.sink[1].in_ )

    s.connect( s.router.in2 , s.src[2].out  )
    s.connect( s.router.out2, s.sink[2].in_ )

    s.connect( s.router.router_id, router_id )

  def done( s ):
    done_flag = 1
    for i in xrange( 3 ):
      done_flag &= s.src[i].done and s.sink[i].done
    return done_flag

  def line_trace( s ):
    in_ = '|'.join( [ x.out.to_str( "%02s:%1s>%1s" % ( x.out.msg[32:40],
                                                       x.out.msg[40:42],
                                                       x.out.msg[42:44] ) )
                                        for x in s.src  ] )
    out = '|'.join( [ x.in_.to_str( "%02s:%1s>%1s" % ( x.in_.msg[32:40],
                                                       x.in_.msg[40:42],
                                                       x.in_.msg[42:44] ) )
                                        for x in s.sink ] )
    return in_ + ' > ' + s.router.line_trace() + ' > '+ out

#-------------------------------------------------------------------------
# run_router_test
#-------------------------------------------------------------------------

def run_router_test( RouterModel, router_id, src_delay, sink_delay, test_msgs,
                     dump_vcd = False, test_verilog = False,
                     num_ports = 4, opaque_nbits = 8, payload_nbits = 32 ):

  # src/sink msgs

  src_msgs  = test_msgs[0]
  sink_msgs = test_msgs[1]

  # Instantiate and elaborate the model

  model = TestHarness( RouterModel, router_id,
                       src_msgs, sink_msgs, src_delay, sink_delay,
                       num_ports, opaque_nbits, payload_nbits,
                       dump_vcd, test_verilog )

  model.vcd_file     = dump_vcd
  model.test_verilog = test_verilog
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print()

  sim.reset()
  while not model.done() and sim.ncycles < 1000:
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

  # Check for success

  if not model.done():
    raise AssertionError( "Simulation did not complete!" )

#-------------------------------------------------------------------------
# Test case: very basic messages
#-------------------------------------------------------------------------
# The testing approach for the router is basically the following.
# - tsrc: which _input port_ the router is getting a message from.
# - tsink: the _expected port_ the router should forward to.
# - src and dest are the _router ids_ for the _actual network_
#
# For example, say the router is number 2 (the parameter is at the bottom
# of this file), and we want to test if the router directly forward a
# message from inport #1 (input terminal) with src=dest=2 to output port
# #1 (output terminal).
# If your router fail to forward this message to the correct output port,
# the simulation will hang or fail, since the test sink connected
# to outport#1 expects to get a message but there is really no message
# for it, or some other test sink receives an unexpected message.

def very_basic_msgs( i ):

  nrouters = 4

  pre = (i-1) % nrouters
  nxt = (i+1) % nrouters

  return mk_router_msgs( nrouters,
#       tsrc tsink src  dest opaque payload
    [ ( 0x1, 0x1,  i,   i,   0x00,  0xfe ), # deliver directly to #2
      ( 0x0, 0x2,  pre, nxt, 0x01,  0xde ), # pass it through
    ]
  )

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                       "msgs                routerid  src_delay sink_delay"),
  [ "vbasic_0",            very_basic_msgs(0), 0,        0,        0          ],
  [ "vbasic_1",            very_basic_msgs(1), 1,        0,        0          ],
  [ "vbasic_2",            very_basic_msgs(2), 2,        0,        0          ],
  [ "vbasic_3",            very_basic_msgs(3), 3,        0,        0          ],

  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to leverage the additional lists
  # of request/response messages defined above, but also to test
  # different source/sink random delays.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  [ "basic_dest_0",        basic_dest(0),      0,        0,        0          ],
  [ "basic_dest_1",        basic_dest(1),      1,        0,        0          ],
  [ "basic_dest_2",        basic_dest(2),      2,        0,        0          ],
  [ "basic_dest_3",        basic_dest(3),      3,        0,        0          ],

  [ "pass_back_0",         pass_back(0),       0,        0,        0          ],
  [ "pass_back_1",         pass_back(1),       1,        0,        0          ],
  [ "pass_back_2",         pass_back(2),       2,        0,        0          ],
  [ "pass_back_3",         pass_back(3),       3,        0,        0          ],

  [ "to_self0",            to_self(0),         0,        0,        0          ],
  [ "to_self1",            to_self(1),         1,        0,        0          ],
  [ "to_self2",            to_self(2),         2,        0,        0          ],
  [ "to_self3",            to_self(3),         3,        0,        0          ],

  [ "route_neighbor0",     route_neighbor(0),  0,        0,        0          ],
  [ "route_neighbor1",     route_neighbor(1),  1,        0,        0          ],
  [ "route_neighbor2",     route_neighbor(2),  2,        0,        0          ],
  [ "route_neighbor3",     route_neighbor(3),  3,        0,        0          ],

  [ "break_ties0",         break_ties(0),      0,        0,        0          ],
  [ "break_ties1",         break_ties(1),      1,        0,        0          ],
  [ "break_ties2",         break_ties(2),      2,        0,        0          ],
  [ "break_ties3",         break_ties(3),      3,        0,        0          ],



  [ "back_pressure0",      back_pressure(0),   0,        0,        45         ],
  [ "back_pressure1",      back_pressure(1),   1,        0,        45         ],
  [ "back_pressure2",      back_pressure(2),   2,        0,        45         ],
  [ "back_pressure3",      back_pressure(3),   3,        0,        45         ],

  [ "dest_0_src_delay",    basic_dest(0),      0,        6,        0          ],
  [ "dest_1_src_delay",    basic_dest(1),      1,        6,        0          ],
  [ "dest_2_src_delay",    basic_dest(2),      2,        6,        0          ],
  [ "dest_3_src_delay",    basic_dest(3),      3,        6,        0          ],
  [ "dest_0_sink_delay",   basic_dest(0),      0,        0,        3          ],
  [ "dest_1_sink_delay",   basic_dest(1),      1,        0,        1          ],
  [ "dest_2_sink_delay",   basic_dest(2),      2,        0,        1          ],
  [ "dest_3_sink_delay",   basic_dest(3),      3,        0,        1          ],

  [ "basic_dest_0_delay",  basic_dest(0),      0,        5,        5          ],
  [ "basic_dest_1_delay",  basic_dest(1),      1,        5,        5          ],
  [ "basic_dest_2_delay",  basic_dest(2),      2,        5,        5          ],
  [ "basic_dest_3_delay",  basic_dest(3),      3,        5,        5          ],

  [ "back_0_src_delay",    pass_back(0),       0,        6,        0          ],
  [ "back_1_src_delay",    pass_back(1),       1,        6,        0          ],
  [ "back_2_src_delay",    pass_back(2),       2,        6,        0          ],
  [ "back_3_src_delay",    pass_back(3),       3,        6,        0          ],
  [ "back_0_sink_delay",   pass_back(0),       0,        0,        6          ],
  [ "back_1_sink_delay",   pass_back(1),       1,        0,        6          ],
  [ "back_2_sink_delay",   pass_back(2),       2,        0,        6          ],
  [ "back_3_sink_delay",   pass_back(3),       3,        0,        6          ],
  [ "pass_back_0_delay",   pass_back(0),       0,        7,        6          ],
  [ "pass_back_1_delay",   pass_back(1),       1,        7,        6          ],
  [ "pass_back_2_delay",   pass_back(2),       2,        7,        6          ],
  [ "pass_back_3_delay",   pass_back(3),       3,        7,        6          ],

  [ "to_self0_src_delay",  to_self(0),         0,        6,        0          ],
  [ "to_self1_src_delay",  to_self(1),         1,        6,        0          ],
  [ "to_self2_src_delay",  to_self(2),         2,        6,        0          ],
  [ "to_self3_src_delay",  to_self(3),         3,        6,        0          ],

  [ "route_neighbor0_src_src_delay",     route_neighbor(0),  0,        4,        0          ],
  [ "route_neighbor1_src_src_delay",     route_neighbor(1),  1,        3,        0          ],
  [ "route_neighbor2_src_src_delay",     route_neighbor(2),  2,        6,        0          ],
  [ "route_neighbor3_src_src_delay",     route_neighbor(3),  3,        7,        0          ],

  [ "route_neighbor0_src_sink_delay",     route_neighbor(0),  0,        0,        6          ],
  [ "route_neighbor1_src_sink_delay",     route_neighbor(1),  1,        0,        4          ],
  [ "route_neighbor2_src_sink_delay",     route_neighbor(2),  2,        0,        2          ],
  [ "route_neighbor3_src_sink_delay",     route_neighbor(3),  3,        0,        7          ],

  [ "break_ties0_src_sink_delays",         break_ties(0),      0,        6,        8          ],
  [ "break_ties1_src_sink_delays",         break_ties(1),      1,        4,        5          ],
  [ "break_ties2_src_sink_delays",         break_ties(2),      2,        5,        7          ],
  [ "break_ties3_src_sink_delays",         break_ties(3),      3,        8,        2          ],


])

#-------------------------------------------------------------------------
# Run tests
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd, test_verilog ):
  run_router_test( RouterRTL(), test_params.routerid,
                   test_params.src_delay, test_params.sink_delay,
                   test_params.msgs, dump_vcd, test_verilog )
