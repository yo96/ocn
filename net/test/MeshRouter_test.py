#=========================================================================
# MeshRouter_test.py
#=========================================================================

from __future__    import print_function

import pytest
import hypothesis
from hypothesis import strategies as st

from pymtl         import *
from pclib.test    import TestSource, TestNetSink, mk_test_case_table
from pclib.ifcs    import NetMsg

#from hypothesis import given, example

from net.MeshRouterRTL import MeshRouterRTL
from NetFL_test import mk_msg
from RouterTest1 import *
from TestHelper  import mk_router_msgs
#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, RouterModel, router_id, row_min, row_max, num_ports,
                src_msgs, sink_msgs, src_delay, sink_delay,
                num_routers, opaque_nbits, payload_nbits,
                dump_vcd=False, test_verilog=False ):

    s.src_msgs    = src_msgs
    s.sink_msgs   = sink_msgs
    s.src_delay   = src_delay
    s.sink_delay  = sink_delay
    s.num_ports   = num_ports
    s.num_routers = num_routers
    s.payload_nbits = payload_nbits
    s.opaque_nbits  = opaque_nbits
    s.addr_nbits    = clog2(num_routers)

    msg_type = NetMsg( num_routers, 2**opaque_nbits, payload_nbits )

    s.src    = [ TestSource  ( msg_type, s.src_msgs[x],  s.src_delay  )
                 for x in xrange( num_ports ) ]


    s.router = RouterModel

    s.sink   = [ TestNetSink ( msg_type, s.sink_msgs[x], s.sink_delay )
                 for x in xrange( num_ports ) ]

    for x in range( num_ports ):
      print ('src [{}]:{}'.format(x,s.src_msgs[x]))
      print ('sink[{}]:{}'.format(x,s.sink_msgs[x]))
    # Dump VCD

    if dump_vcd:
      s.router.vcd_file = dump_vcd
      if hasattr(s.router, 'inner'):
        s.router.inner.vcd_file = dump_vcd


    # Translation

    if test_verilog:
      s.router = TranslationTool( s.router )

    # Connect
    for i in range( num_ports ):
      s.connect( s.router.in_[i], s.src[i].out  )
      s.connect( s.router.out[i], s.sink[i].in_ )

    s.connect( s.router.router_id, router_id )
    s.connect( s.router.row_min,    row_min )
    s.connect( s.router.row_max,    row_max )

  def done( s ):
    done_flag = 1
    for i in xrange( s.num_ports ):
      done_flag &= s.src[i].done and s.sink[i].done
    return done_flag

  def line_trace( s ):
    
    in_ = '|'.join( [ x.out.to_str( "%02s:%1s>%1s" % ( x.out.msg[s.payload_nbits:s.payload_nbits+s.opaque_nbits],
                                                       x.out.msg[s.payload_nbits+s.opaque_nbits:s.payload_nbits+s.opaque_nbits+s.addr_nbits],
                                                       x.out.msg[s.payload_nbits+s.opaque_nbits+s.addr_nbits:s.payload_nbits+s.opaque_nbits+s.addr_nbits*2] ) )
                                        for x in s.src  ] )
    out = '|'.join( [ x.in_.to_str( "%02s:%1s>%1s" % ( x.in_.msg[s.payload_nbits:s.payload_nbits+s.opaque_nbits],
                                                       x.in_.msg[s.payload_nbits+s.opaque_nbits:s.payload_nbits+s.opaque_nbits+s.addr_nbits],
                                                       x.in_.msg[s.payload_nbits+s.opaque_nbits+s.addr_nbits:s.payload_nbits+s.opaque_nbits+s.addr_nbits*2] ) )
                                        for x in s.sink ] )
    return in_ + ' > ' + s.router.line_trace() + ' > '+ out

#-------------------------------------------------------------------------
# run_router_test
#-------------------------------------------------------------------------

def run_router_test( RouterModel, router_id, row_min, row_max,
                     src_delay, sink_delay, test_msgs,
                     dump_vcd = False, test_verilog = False,
                     num_routers = 4, opaque_nbits = 8, payload_nbits = 32 ):

  # src/sink msgs

  src_msgs  = test_msgs[0]
  sink_msgs = test_msgs[1]

  # Instantiate and elaborate the model, num_ports = 5

  model = TestHarness( RouterModel, router_id, row_min, row_max, 5,
                       src_msgs, sink_msgs, src_delay, sink_delay,
                       num_routers, opaque_nbits, payload_nbits,
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
# End of Test Harness
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
# Helpers
#-------------------------------------------------------------------------
def y_dimension_order_routing(router_id, row_min, row_max,src, dest):
  row_wid = row_max-row_min+1
  # determine tsrc tsink based on y-dimension order routing
  tsrc  = 0
  tsink = 0
  if src == router_id:
    tsrc = 4
  elif (src % row_wid) < (router_id % row_wid):
    tsrc = 0
  elif (src % row_wid) > (router_id % row_wid):
    tsrc = 2
  elif router_id < row_min:
    tsrc = 1
  else:
    tsrc = 3
  # determin tsink
  if dest == router_id:
    tsink = 4
  elif dest < row_min:
    tsink = 1
  elif dest > row_max:
    tsink = 3
  elif dest < router_id:
    tsink = 0
  else:
    tsink = 2
  return (tsrc,tsink)

def gen_router_msgs(router_id, row_min, row_max,
                    src, dest, opaque, payload,
                    nrouter=4,num_ports=5,
                    payload_nbits=32,opaque_nbits=8  ):
  tsrc, tsink = y_dimension_order_routing(router_id, row_min, row_max,src, dest)
  return mk_router_msgs( num_ports,
#       tsrc   tsink   src    dest    opaque   payload
    [  ( tsrc, tsink,  src,   dest,   opaque,  payload )
      #( 0x4, 0x3,  0,   2,   0x01,  0xff ), # deliver directly to #2
      #( 0x2, 0x4,  1,   0,   0x02,  0xde ), # pass it through
      #( 0x2, 0x4,  3,   0,   0x03,  0xad ),
      #( 0x4, 0x4,  0,   0,   0x04,  0xdd ),
    ]
  )

def gen_src_sink_msgs( nrouters, num_ports, msg_list):
  src_msgs  = [ [] for x in xrange(num_ports) ]
  sink_msgs = [ [] for x in xrange(num_ports) ]

  for x in msg_list:
    tsrc, tsink, src, dest, opaque, payload = x[0], x[1], x[2], x[3], x[4], x[5]

    msg = mk_msg( src, dest, opaque, payload, num_ports=nrouters )
    src_msgs [tsrc].append( msg )
    sink_msgs[tsink].append( msg )

  return [ src_msgs, sink_msgs ] 
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

  nrouters  = 9
  num_ports = 5

  pre = (i-1) % nrouters
  nxt = (i+1) % nrouters

  return gen_src_sink_msgs( nrouters, num_ports,
#       tsrc tsink src  dest opaque payload
    [  ( 0x4, 0x2,  0,   1,   0x01,  0xff ),
      #( 0x4, 0x4,  0,   0,   0x01,  0xff ), 
      #( 0x2, 0x4,  1,   0,   0x02,  0xde ), 
      #( 0x2, 0x4,  3,   0,   0x03,  0xad ),
      #( 0x4, 0x4,  0,   0,   0x04,  0xdd ),
    ]
  )

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                       "msgs                routerid  src_delay sink_delay"),
  [ "vbasic_0",            very_basic_msgs(0), 0,        0,        0          ]

])

#-------------------------------------------------------------------------
# Run tests
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd, test_verilog ):
  nrouters = 9
  run_router_test( MeshRouterRTL(num_routers = nrouters), test_params.routerid, 0, 2,
                   test_params.src_delay, test_params.sink_delay,
                   test_params.msgs, dump_vcd, test_verilog,
                   num_routers = nrouters )

#-------------------------------------------------------------------------
# Hypothesis tests
#-------------------------------------------------------------------------

"""
@hypothesis.given( 
  src =st.integers(0,3),
  dest=st.integers(0,3),
  src_delay =st.integers(0,50),
  sink_delay=st.integers(0,50)
  )
def test_hypothesis_0_4( src, dest, src_delay, sink_delay, 
                         dump_vcd,test_verilog ):
  router_id = 0
  row_min   = 0
  row_max   = 1
  opaque    = 0x01
  payload   = 0xdead
  msg       = gen_router_msgs(router_id, row_min, row_max,
                              src, dest, opaque, payload,
                              nrouter=4, num_ports=5,
                              payload_nbits=32,opaque_nbits=8 )
  run_router_test( MeshRouterRTL(), 0, 0, 1,
                   src_delay, sink_delay,
                   msg, dump_vcd, test_verilog )

@hypothesis.given( 
  src =st.integers(0,3),
  dest=st.integers(0,3),
  src_delay =st.integers(0,50),
  sink_delay=st.integers(0,50)
  )
def test_hypothesis_1_4( src, dest, src_delay, sink_delay, 
                         dump_vcd,test_verilog ):
  router_id = 1
  row_min   = 0
  row_max   = 1
  opaque    = 0x01
  payload   = 0xdead
  msg       = gen_router_msgs(router_id, row_min, row_max,
                              src, dest, opaque, payload,
                              nrouter=4, num_ports=5,
                              payload_nbits=32,opaque_nbits=8 )
  run_router_test( MeshRouterRTL(), router_id, row_min, row_max,
                   src_delay, sink_delay,
                   msg, dump_vcd, test_verilog )

@hypothesis.given( 
  src =st.integers(0,3),
  dest=st.integers(0,3),
  src_delay =st.integers(0,50),
  sink_delay=st.integers(0,50)
  )
def test_hypothesis_0_9( src, dest, src_delay, sink_delay, 
                         dump_vcd,test_verilog ):
  router_id = 0
  row_min   = 0
  row_max   = 2
  opaque    = 0x01
  payload   = 0xdead
  msg       = gen_router_msgs(router_id, row_min, row_max,
                              src, dest, opaque, payload,
                              nrouter=9, num_ports=5,
                              payload_nbits=32,opaque_nbits=8 )
  run_router_test( MeshRouterRTL(num_routers=9), 
                   router_id, row_min, row_max,
                   src_delay, sink_delay,
                   msg, dump_vcd, test_verilog,
                   num_routers=9 )

@hypothesis.given(
  nrouter_log2 = st.integers(2,32),
  router_id    = st.integers(0,1024),
  src          = st.integers(0,3),
  dest         = st.integers(0,3),
  src_delay    = st.integers(0,50),
  sink_delay   = st.integers(0,50)
  )
def test_hypothesis_n( nrouter_log2,router_id,
                       src, dest, src_delay, sink_delay, 
                       dump_vcd,test_verilog ):
  hypothesis.assume(router_id<nrouter_log2**2)  
  nrouter   = nrouter_log2 ** 2
  row_min   = router_id/nrouter_log2
  row_max   = row_min + nrouter_log2-1
  opaque    = 0x01
  payload   = 0xdead
  msg       = gen_router_msgs(router_id, row_min, row_max,
                              src, dest, opaque, payload,
                              nrouter=nrouter, num_ports=5,
                              payload_nbits=32,opaque_nbits=8 )
  run_router_test( MeshRouterRTL(num_routers=nrouter), 
                   router_id, row_min, row_max,
                   src_delay, sink_delay,
                   msg, dump_vcd, test_verilog,
                   num_routers=nrouter )
"""
@hypothesis.strategies.composite
def router_test_msg(draw,mesh_wid,mesh_ht,router_id):
  nrouter    = mesh_wid * mesh_ht
  row_min    = (router_id/mesh_wid)*mesh_wid
  row_max    = row_min + mesh_wid-1
  src        = draw(st.integers(0,nrouter-1))
  dest       = draw(st.integers(0,nrouter-1))
  tsrc,tsink = y_dimension_order_routing(router_id, row_min, row_max,src,dest)
  opaque     = draw(st.integers(1,0xff      ))
  payload    = draw(st.integers(0,0xffffffff))
  return (tsrc,tsink,src,dest,opaque,payload)

# Test a square mesh
@hypothesis.given(
  nrouter_log2 = st.integers( 2,32   ),
  router_id    = st.integers( 0,1024 ),
  src_delay    = st.integers( 0,50   ),
  sink_delay   = st.integers( 0,50   ),
  test_msgs    = st.data()
  )
def test_hypothesis_square( nrouter_log2,router_id,
                            src_delay, sink_delay, test_msgs, 
                            dump_vcd,test_verilog ):
  # Assume router id always smaller than number of routers
  hypothesis.assume( router_id<nrouter_log2 ** 2 ) 
  nrouter   = nrouter_log2 ** 2
  row_min   = (router_id/nrouter_log2)*nrouter_log2
  row_max   = row_min + nrouter_log2-1
  # Generate a RANDOM list of RANDOM test msgs!
  msgs = test_msgs.draw( st.lists( 
    router_test_msg(nrouter_log2,nrouter_log2,router_id),
                    min_size=1, max_size=100 ) )

  run_router_test( MeshRouterRTL(num_routers=nrouter), 
                   router_id, row_min, row_max,
                   src_delay, sink_delay,
                   gen_src_sink_msgs(nrouters=nrouter,num_ports=5,msg_list=msgs), 
                   dump_vcd, test_verilog,
                   num_routers=nrouter )

# Test a arbitray mesh
@hypothesis.given(
  mesh_wid     = st.integers( 1,32   ),
  mesh_ht      = st.integers( 2,32   ),
  router_id    = st.integers( 0,1024 ),
  src_delay    = st.integers( 0,50   ),
  sink_delay   = st.integers( 0,50   ),
  test_msgs    = st.data()
  )
def test_hypothesis_arbitrary( mesh_wid,mesh_ht,router_id,
                               src_delay, sink_delay, test_msgs, 
                               dump_vcd,test_verilog ):
  nrouter   = mesh_wid * mesh_ht
  # Assume router id always smaller than number of routers
  hypothesis.assume( router_id < nrouter ) 
  row_min   = (router_id/mesh_wid)*mesh_wid
  row_max   = row_min + mesh_wid - 1
  # Generate a RANDOM list of RANDOM test msgs!
  msgs = test_msgs.draw( st.lists( 
                          router_test_msg(mesh_wid,mesh_ht,router_id),
                          min_size=1, max_size=100 ) )

  run_router_test( MeshRouterRTL(num_routers=nrouter), 
                   router_id, row_min, row_max,
                   src_delay, sink_delay,
                   gen_src_sink_msgs(nrouters=nrouter,num_ports=5,msg_list=msgs), 
                   dump_vcd, test_verilog,
                   num_routers=nrouter )

