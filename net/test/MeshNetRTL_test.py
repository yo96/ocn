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

from net.MeshNetRTL import MeshNetRTL
from net.BadMeshNetRTL import BadMeshNetRTL # Demo purpose
#-------------------------------------------------------------------------
# Reuse tests from FL model
#-------------------------------------------------------------------------

from NetFL_test import test_case_table
from TestHelper import mk_net_msgs

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
    s.sink = [ TestNetSink( msg_type, s.sink_msgs[x], s.sink_delay[x] ) for x in xrange(num_routers) ]

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

#-------------------------------------------------------------------------------
# End of Test Harness
#-------------------------------------------------------------------------------

# Test default configuration
@pytest.mark.parametrize( **test_case_table )
def test_Mesh_default( test_params, dump_vcd, test_verilog ):
  run_net_test( MeshNetRTL(), 
                test_params.src_delay, test_params.sink_delay, test_params.msgs,
                num_routers = 4, num_ports = 5, 
                opaque_nbits = 8, payload_nbits = 32,
                dump_vcd = False, test_verilog = False )

# Hypothesis test
@hypothesis.strategies.composite
def net_test_msg(draw,mesh_wid,mesh_ht):
  nrouter    = mesh_wid * mesh_ht
  src        = draw(st.integers(0,nrouter-1))
  dest       = draw(st.integers(0,nrouter-1))
  opaque     = draw(st.integers(1,0xff      ))
  payload    = draw(st.integers(0,0xffffffff))
  return (src,dest,opaque,payload)

@hypothesis.given(
  mesh_wid     = st.integers( 1,32   ),
  mesh_ht      = st.integers( 1,32   ),
  src_delay    = st.integers( 0,50   ),
  sink_delay   = st.integers( 0,50   ),
  test_msgs    = st.data() )
#@hypothesis.settings(timeout=30)
def test_mesh_hypothesis(mesh_wid, mesh_ht, src_delay, sink_delay,
                         test_msgs):
  hypothesis.assume(mesh_wid*mesh_ht>1)
  hypothesis.event( "Number of routers: %d\n" % (mesh_ht*mesh_wid) )
  nrouters = mesh_wid * mesh_ht
  msgs     = test_msgs.draw(
              st.lists( net_test_msg(mesh_wid,mesh_ht),
                        min_size=1, max_size=256 ) )
  src_delay_lst = [src_delay for _ in range(nrouters)]
  sink_delay_lst= [sink_delay for _ in range(nrouters)]

  run_net_test( MeshNetRTL( num_routers = nrouters, 
                               mesh_wid = mesh_wid, mesh_ht = mesh_ht ), 
                src_delay_lst, sink_delay_lst, 
                mk_net_msgs(nrouters,msgs),
                num_routers = nrouters, num_ports = 5, 
                opaque_nbits = 8, payload_nbits = 32,
                dump_vcd = False, test_verilog = False )
