#=========================================================================
# NetFL_test.py
#=========================================================================

from __future__     import print_function

import pytest
import random

random.seed(0xdeadbeef)

from pymtl          import *
from pclib.test     import TestSource, TestNetSink, mk_test_case_table
from pclib.ifcs     import NetMsg
from net.NetFL import NetFL
                    
from TestHelper     import *
from NetTest0       import *
from NetTest1       import *

from TrafficPatternTest import *
#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  # Constructor

  def __init__( s, NetModel, src_msgs, sink_msgs, src_delay, sink_delay,
                num_ports, opaque_nbits, payload_nbits,
                dump_vcd=False, test_verilog=False ):

    s.src_msgs   = src_msgs
    s.sink_msgs  = sink_msgs
    s.src_delay  = src_delay
    s.sink_delay = sink_delay
    s.num_ports  = num_ports

    msg_type = NetMsg( num_ports, 2**opaque_nbits, payload_nbits )

    s.src  = [ TestSource ( msg_type, s.src_msgs[x],  s.src_delay[x]  ) for x in xrange(num_ports) ]#
    s.net  = NetModel
    s.sink = [ TestNetSink( msg_type, s.sink_msgs[x], s.sink_delay[x] ) for x in xrange(num_ports) ]

    # Dump VCD

    if dump_vcd:
      s.net.vcd_file = dump_vcd
      if hasattr(s.net, 'inner'):
        s.net.inner.vcd_file = dump_vcd

    # Translation

    if test_verilog:
      s.net = TranslationTool( s.net )

    # Connect

    for i in xrange(num_ports):
      s.connect( s.net.in_[i], s.src[i].out  )
      s.connect( s.net.out[i], s.sink[i].in_ )

  # Done

  def done( s ):
    done_flag = 1
    for i in xrange(s.num_ports):
      done_flag &= s.src[i].done and s.sink[i].done
    return done_flag

  # Line-trace

  def line_trace( s ):
    in_ = '|'.join( [ x.out.to_str( "%02s:%1s>%1s" % (  x.out.msg[32:40],
                                                        x.out.msg[40:40+clog2(s.num_ports)],
                                                        x.out.msg[40+clog2(s.num_ports):40+clog2(s.num_ports)*2] ) )
                                        for x in s.src  ] )
    out = '|'.join( [ x.in_.to_str( "%02s:%1s>%1s" % (  x.in_.msg[32:40],
                                                        x.in_.msg[40:40+clog2(s.num_ports)],
                                                        x.in_.msg[40+clog2(s.num_ports):40+clog2(s.num_ports)*2] ) )
                                        for x in s.sink ] )
    return in_ + ' >>> ' + s.net.line_trace() + ' >>> ' + out

#-------------------------------------------------------------------------
# run_net_test
#-------------------------------------------------------------------------

def run_net_test( NetModel, src_delay, sink_delay, test_msgs,
                  dump_vcd = False, test_verilog = False,
                  num_ports = 4, opaque_nbits = 8, payload_nbits = 32 ):

  # src/sink msgs

  src_msgs  = test_msgs[0]
  sink_msgs = test_msgs[1]

  # Instantiate and elaborate the model

  model = TestHarness( NetModel, src_msgs, sink_msgs, src_delay, sink_delay,
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
  # TODO: Change back to 50000
  while not model.done() and sim.ncycles < 50000:
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
# Test case: one pkt
#-------------------------------------------------------------------------

def one_pkt_msgs():

  nports = 4

  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  2,   0x00,  0xab ),
    ]
  )

#-------------------------------------------------------------------------
# Test case: single destination
#-------------------------------------------------------------------------

def single_dest_msgs():

  nports = 4

  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  0,   0x00,  0xce ),
      ( 1,  0,   0x01,  0xff ),
      ( 2,  0,   0x02,  0x80 ),
      ( 3,  0,   0x03,  0xc0 ),
    ]
  )

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK: Add new test cases
#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                        "msgs                      src_delay         sink_delay" ),
  [ "one_pkt",              one_pkt_msgs(),           [0,0,0,0],        [0,0,0,0]   ],
  [ "single_dest",          single_dest_msgs(),       [0,0,0,0],        [0,0,0,0]   ],

  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to leverage the additional lists
  # of request/response messages defined above, but also to test
  # different source/sink random delays.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  [ "one_pkt_one_self",     one_pkt_one_self(),       [0,0,0,0],        [0,0,0,0]   ],
  [ "one_pkt_self",         one_pkt_self(),           [0,0,0,0],        [0,0,0,0]   ],
  [ "four_pkt_self",        four_pkt_self(),          [0,0,0,0],        [0,0,0,0]   ],
  [ "single_dest_2router",  single_dest_2router(),    [0,0,0,0],        [0,0,0,0]   ],  
  [ "var_pkt_self",         var_pkt_self(),           [0,0,0,0],        [0,0,0,0]   ],
  [ "dead_lock",            dead_lock(),              [0,0,0,0],        [100,100,100,100]   ],

  [ "a2b_1pkt",             a2b_1pkt(),               [0,0,0,0],        [0,0,0,0]   ],
  [ "a2b_4pkt",             a2b_4pkt(),               [0,0,0,0],        [0,0,0,0]   ],
  [ "a2b_all",              a2b_all(),                [0,0,0,0],        [0,0,0,0]   ],

  [ "a2b_b2a_1pkt",         a2b_b2a_1pkt(),           [0,0,0,0],        [0,0,0,0]   ],
  [ "a2b_b2a_4pkt",         a2b_b2a_4pkt(),           [0,0,0,0],        [0,0,0,0]   ],
  [ "a2b_b2a_all",          a2b_b2a_all(),            [0,0,0,0],        [0,0,0,0]   ],
  
  [ "single_src_basic",     single_src_basic(),       [0,0,0,0],        [0,0,0,0]   ],
  [ "single_src_4pkt",      single_src_4pkt(),        [0,0,0,0],        [0,0,0,0]   ],
  [ "single_src_1pkt_all",  single_src_1pkt_all(),    [0,0,0,0],        [0,0,0,0]   ],
  [ "single_src_4pkt_all",  single_src_4pkt_all(),    [0,0,0,0],        [0,0,0,0]   ],

  [ "single_dest_basic",    single_dest_basic(),      [0,0,0,0],        [0,0,0,0]   ],
  [ "single_dest_4pkt",     single_dest_4pkt(),       [0,0,0,0],        [0,0,0,0]   ],
  [ "single_dest_1pkt_all", single_dest_1pkt_all(),   [0,0,0,0],        [0,0,0,0]   ],
  [ "single_dest_4pkt_all", single_dest_4pkt_all(),   [0,0,0,0],        [0,0,0,0]   ],

  [ "single_neighbor_basic",single_neighbor_basic(),  [0,0,0,0],        [0,0,0,0]   ],
  [ "both_neighbor_basic",  both_neighbor_basic(),    [0,0,0,0],        [0,0,0,0]   ],
  [ "single_neighbor_4pkt", single_neighbor_4pkt(),   [0,0,0,0],        [0,0,0,0]   ],
  [ "both_neighbor_4pkt",   both_neighbor_4pkt(),     [0,0,0,0],        [0,0,0,0]   ],
  
  [ "crazy_pressure",       crazy_pressure(),         [0,0,0,0],        [0,0,0,0]   ],
  [ "sink0_pressure",       single_sink_pressure(0),  [0,0,0,0],        [20,0,0,0]  ],
  [ "sink1_pressure",       single_sink_pressure(1),  [0,0,0,0],        [0,20,0,0]  ],
  [ "sink2_pressure",       single_sink_pressure(2),  [0,0,0,0],        [0,0,20,0]  ],
  [ "sink3_pressure",       single_sink_pressure(3),  [0,0,0,0],        [0,0,0,20]  ],
  [ "0_to_0_pressure",      one_to_one_pressure(0,0), [0,0,0,0],        [20,0,0,0]  ],
  [ "0_to_1_pressure",      one_to_one_pressure(0,1), [0,0,0,0],        [0,20,0,0]  ],
  [ "0_to_2_pressure",      one_to_one_pressure(0,2), [0,0,0,0],        [0,0,20,0]  ],
  [ "0_to_3_pressure",      one_to_one_pressure(0,3), [0,0,0,0],        [0,0,0,20]  ],
  [ "1_to_0_pressure",      one_to_one_pressure(1,0), [0,0,0,0],        [20,0,0,0]  ],
  [ "1_to_1_pressure",      one_to_one_pressure(1,1), [0,0,0,0],        [0,20,0,0]  ],
  [ "1_to_2_pressure",      one_to_one_pressure(1,2), [0,0,0,0],        [0,0,20,0]  ],
  [ "1_to_3_pressure",      one_to_one_pressure(1,3), [0,0,0,0],        [0,0,0,20]  ],
  [ "2_to_0_pressure",      one_to_one_pressure(2,0), [0,0,0,0],        [20,0,0,0]  ],
  [ "2_to_1_pressure",      one_to_one_pressure(2,1), [0,0,0,0],        [0,20,0,0]  ],
  [ "2_to_2_pressure",      one_to_one_pressure(2,2), [0,0,0,0],        [0,0,20,0]  ],
  [ "2_to_3_pressure",      one_to_one_pressure(2,3), [0,0,0,0],        [0,0,0,20]  ],
  [ "3_to_0_pressure",      one_to_one_pressure(3,0), [0,0,0,0],        [20,0,0,0]  ],
  [ "3_to_1_pressure",      one_to_one_pressure(3,1), [0,0,0,0],        [0,20,0,0]  ],
  [ "3_to_2_pressure",      one_to_one_pressure(3,2), [0,0,0,0],        [0,0,20,0]  ],
  [ "3_to_3_pressure",      one_to_one_pressure(3,3), [0,0,0,0],        [0,0,0,20]  ],

  [ "rand_src_to_0",        rand_src_to_0(),          [0,0,0,0],        [0,0,0,0]   ],
  [ "rand_src_to_1",        rand_src_to_1(),          [0,0,0,0],        [0,0,0,0]   ],
  [ "rand_src_to_2",        rand_src_to_2(),          [0,0,0,0],        [0,0,0,0]   ],
  [ "rand_src_to_3",        rand_src_to_3(),          [0,0,0,0],        [0,0,0,0]   ],

  [ "rand_dest_from_0",     rand_dest_from_0(),       [0,0,0,0],        [0,0,0,0]   ],
  [ "rand_dest_from_1",     rand_dest_from_1(),       [0,0,0,0],        [0,0,0,0]   ],
  [ "rand_dest_from_2",     rand_dest_from_2(),       [0,0,0,0],        [0,0,0,0]   ],
  [ "rand_dest_from_3",     rand_dest_from_3(),       [0,0,0,0],        [0,0,0,0]   ],

  [ "rand_src_rand_dest",   rand_src_2_rand_dest(),   [0,0,0,0],        [0,0,0,0]   ],
  
  [ "nearest_neighbour",    nearest_neighbour(),      [0,0,0,0],        [0,0,0,0]   ],
  [ "hotspot",              hotspot(),                [1,2,3,4],        [0,0,0,0]   ],
  [ "oversubscribed_hotspot",oversubscribed_hotspot(),[0,0,0,0],        [0,0,0,0]   ],
  [ "opposite",             opposite(),               [0,0,0,0],        [0,0,0,0]   ],
# Delay test
  [ "one_pkt_src_delay",    one_pkt_msgs(),           [0,3,0,0],        [0,0,0,0]   ],
  [ "one_pkt_sink_delay",   one_pkt_msgs(),           [0,0,0,0],        [5,0,0,0]   ],
  [ "one_pkt_long_delay",   one_pkt_msgs(),           [100,0,0,0],      [0,0,99,0]  ],
  [ "4_pkt_self_dealy",     four_pkt_self(),          [2,3,3,3],        [7,9,11,13] ],
  [ "var_pkt_self_delay",   var_pkt_self(),           [5,7,9,11],       [0,0,10,0]  ],
  [ "a2b_all_dalay",        a2b_all(),                [1,2,3,4],        [4,3,2,1]   ],
  [ "a2b_b2a_all_delay",    a2b_b2a_all(),            [16,8,4,2],       [1,2,4,8]   ],
  [ "single_src_4pkt_delay",single_src_4pkt_all(),    [99,1,2,3],       [1,4,8,12]  ],
  [ "both_neighbor_delay",  both_neighbor_4pkt(),     [0,1,2,3],        [1,3,5,7]   ],
  [ "ran_src_ran_des_delay",rand_src_2_rand_dest(),   [5,6,7,1],        [89,4,4,3]  ],
  [ "nearest_nbr_delay",    nearest_neighbour(),      [1,3,5,7],        [8,10,12,4] ],
  [ "hotspot_delay",        hotspot(),                [5,6,7,8],        [2,2,2,2]   ],
  [ "over_hotspot_delay",   oversubscribed_hotspot(), [5,3,1,1],        [11,1,0,9]  ],
  [ "opposite_delay",       opposite(),               [2,3,3,3],        [3,3,3,3]   ],
  [ "crazy_delay",          crazy_pressure(),         [0,0,0,0],        [99,98,97,9]],
])

#-------------------------------------------------------------------------
# Run tests
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd, test_verilog ):
  run_net_test( NetFL(), test_params.src_delay, test_params.sink_delay,
                test_params.msgs, dump_vcd, test_verilog )
