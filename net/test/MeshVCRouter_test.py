# Test for Mesh router with VC

from __future__ import print_function

import pytest 
import hypothesis 

from pymtl      import * 
from pclib.test import TestSource, TestSink, mk_test_case_table
from net.MeshNetMsg import MeshNetMsg, mk_mesh_msg
from net.MeshVCRouter import MeshVCRouterRTL
from TestSinkFixedDelay import TestSinkFixedDelay 

# TODO: Test Harness
class TestHarness( Model ):
  def __init__( s, RouterModel, mesh_wid, mesh_ht,
				        pos_x, pos_y, opaque_nbits, payload_nbits,
				        src_msgs, sink_msgs, src_delay, sink_delay,
				        dump_vcd = False, test_verilog = False ):
    # Constant
    s.src_msgs    = src_msgs
    s.sink_msgs   = sink_msgs
    s.src_delay   = src_delay
    s.sink_delay  = sink_delay
    s.opaque_nbits  = opaque_nbits
    s.payload_nbits = payload_nbits
    s.x_addr_nbits  = clog2( mesh_wid )
    s.y_addr_nbits  = clog2( mesh_ht  )
    s.num_routers   = mesh_wid * mesh_ht

    s.num_ports = 5

    msg_type = MeshNetMsg( mesh_wid, mesh_ht, opaque_nbits, payload_nbits )

  	# use src_delay as a list 
    s.src = [TestSource        ( msg_type, s.src_msgs[i],  s.src_delay ) 
    		 		 for i in range( s.num_ports )]
    s.sink= [TestSinkFixedDelay( msg_type, s.sink_msgs[i], s.sink_delay )
    		 		 for i in range( s.num_ports )]
    s.router = RouterModel

    # Dump vcd file
    if dump_vcd:
      s.router.vcd_file = dump_vcd
      if hasattr(s.router, 'inner'):
        s.router.inner.vcd_file = dump_vcd

    # Translation
    if test_verilog:
      s.router = TranslationTool( s.router )

    # Connect ports
    for i in range( s.num_ports ):
      s.connect( s.router.in_[i], s.src[i].out )
      s.connect( s.router.out[i], s.sink[i].in_)

    # Connect constants
    s.connect( s.router.pos_x, pos_x )
    s.connect( s.router.pos_y, pos_y )

  def done( s ):
    done_flag = 1
    for i in range( s.num_ports ):
      done_flag &= s.src[i].done and s.sink[i].done
    return done_flag

  # TODO:: modify line trace
  #  +--------+--------+-------+-------+--------+---------+
  #  | dest_x | dest_y | src_x | src_y | opaque | payload |
  #  +--------+--------+-------+-------+--------+---------+
  #

  def line_trace( s ):
    opaque_offset = s.payload_nbits
    src_y_offset  = opaque_offset + s.opaque_nbits
    src_x_offset  = src_y_offset  + s.y_addr_nbits
    dest_y_offset = src_x_offset  + s.x_addr_nbits
    dest_x_offset = dest_y_offset + s.y_addr_nbits
    last_bit      = dest_x_offset + s.x_addr_nbits 

    opaque_slice = slice( opaque_offset, src_y_offset  )
    src_y_slice  = slice( src_y_offset, src_x_offset   )     
    src_x_slice  = slice( src_x_offset, dest_y_offset  )   
    dest_y_slice = slice( dest_y_offset, dest_x_offset )   
    dest_x_slice = slice( dest_x_offset, last_bit      )     

    in_ = '|'.join( [ x.out.to_str( "%02s:(%1s,%1s)>(%1s,%1s)" % (
                                     x.out.msg[opaque_slice], 
                                     x.out.msg[src_x_slice],  x.out.msg[src_y_slice],
                                     x.out.msg[dest_x_slice], x.out.msg[dest_y_slice] ) )
                                        for x in s.src  ] )
    out = '|'.join( [ x.in_.to_str( "%02s:(%1s,%1s)>(%1s,%1s)" % (
                                     x.in_.msg[opaque_slice], 
                                     x.in_.msg[src_x_slice],  x.in_.msg[src_y_slice],
                                     x.in_.msg[dest_x_slice], x.in_.msg[src_y_slice] ) )                                        for x in s.sink ] )
    return in_ + ' > ' + s.router.line_trace() + ' > '+ out
    
#-------------------------------------------------------------------------------
# Test simulator
#------------------------------------------------------------------------------- 
def run_vc_router_test(
      RouterModel, mesh_wid, mesh_ht, 
      pos_x, pos_y, opaque_nbits, payload_nbits,
      test_msgs, src_delay, sink_delay,
      dump_vcd = False, test_verilog = False):
  # Constant
  max_cycles = 200

  # src/sink msgs
  src_msgs  = test_msgs[0]
  sink_msgs = test_msgs[1]

  # Instantiate and elaborate model
  model = TestHarness( RouterModel, mesh_wid, mesh_ht,
                       pos_x, pos_y, opaque_nbits, payload_nbits,
                       src_msgs, sink_msgs, src_delay, sink_delay,
                       dump_vcd, test_verilog )
  model.vcd_file = dump_vcd
  model.test_verilog = test_verilog
  model.elaborate()

  # Run simulation
  sim = SimulationTool( model )
  print()
  sim.reset()
  while not model.done() and sim.ncycles < max_cycles:
    sim.print_line_trace()
    sim.cycle()

  # A few extra cycles
  sim.cycle()
  sim.cycle()
  sim.cycle()

  # Check result
  if not model.done():
    raise AssertionError( "Simulation did not complete!" )

#-----------------------------------------------------------------------
# Helpers 
#-----------------------------------------------------------------------
def dimension_order_routing( dimension, pos_x, pos_y, 
                             src_x, src_y, dest_x, dest_y ):
  tsrc  = 0
  tsink = 0
  west  = 0
  north = 1
  east  = 2
  south = 3
  inout = 4
  # determine source port
  if src_x == pos_x and src_y == pos_y:
    tsrc = inout
  
  elif dimension == 'y':
    if src_x == pos_x:
      if src_y < pos_y:
        tsrc = north
      else:
        tsrc = south
    elif src_x < pos_x:
      tsrc = west
    else:
      tsrc = east
  
  elif dimension == 'x':
    if src_y == pos_y:
      if src_x < pos_x:
        tsrc = west 
      else: 
        tsrc = east
    elif src_y > pos_y:
      tsrc = south
    else:
      tsrc = north 
  else: 
    raise AssertionError( "Invalid dimension input for DOR! " )
  # determine dest port
  if dest_x == pos_x and dest_y == pos_y:
    tsink = inout
  elif dimension == 'y':
    if dest_y > pos_y:
      tsink = south
    elif dest_y < pos_y:
      tsink = north
    elif dest_x > pos_x:
      tsink = east
    else:
      tsink = west
  elif dimension == 'x':
    if dest_x > pos_x:
      tsink = east
    elif dest_x < pos_x:
      tsink = west
    elif dest_y > pos_y:
      tsink = south
    else:
      tsink = north 
  else:
    raise AssertionError( "Invalid dimension input for DOR! " )
  return (tsrc, tsink)


def mk_test_msgs( nports, mesh_wid, mesh_ht, msg_list ):

  src_msgs  = [ [] for _ in range( nports ) ]
  sink_msgs = [ [] for _ in range( nports ) ]
  
  for m in msg_list:
    tsrc, tsink, src_x, src_y, dest_x, dest_y, opaque, payload = \
    m[0], m[1],  m[2],  m[3],  m[4],   m[5],   m[6],   m[7]
    msg = mk_mesh_msg( src_x, src_y, dest_x, dest_y, opaque, payload,
                       mesh_wid, mesh_ht)
    src_msgs [ tsrc].append( msg )
    sink_msgs[tsink].append( msg )

  return [ src_msgs, sink_msgs ]

# Append source and sink ids to a list of net messages
def copmute_src_sink( pos_x, pos_y, dimension, msg_lst ):
  test_lst = []
  tsrc  = 0
  tsink = 0
  print( msg_lst )
  for m in msg_lst:
    tsrc, tsink = dimension_order_routing( dimension, pos_x, pos_y,
                                           m[0], m[1], m[2], m[3] )
    test_lst.append( (tsrc, tsink, m[0], m[1], m[2], m[3], m[4], m[5]) )
  return test_lst


# Very basic direct tests
def basic_msgs( pos_x, pos_y, mesh_wid, mesh_ht, dimension ):
  return mk_test_msgs( 5, mesh_wid, mesh_ht, 
         copmute_src_sink( pos_x,pos_y, dimension,
          [ (   0,      0,      1,      1,      0, 0xc001d00d)
          ]) )

          # src_x,  src_y, dest_x, dest_y, opaque, payload

#-------------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                 "msgs                     routing  mesh_wid mesh_ht pos_x pos_y src_delay sink_delay" ),
  [ "first_test",    basic_msgs(1,1,2,2,'y'), 'DOR_Y', 2,       2,      1,    1,    0,        0         ]

])


#-------------------------------------------------------------------------------
# Run tests
#-------------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd, test_verilog ):
  run_vc_router_test( MeshVCRouterRTL(
                        mesh_wid = test_params.mesh_wid, mesh_ht=test_params.mesh_ht,
                        routing_algo = test_params.routing
                      ),
                      test_params.mesh_wid, test_params.mesh_ht, 
                      test_params.pos_x, test_params.pos_y, 8, 32,
                      test_params.msgs, test_params.src_delay, test_params.sink_delay,
                      dump_vcd, test_verilog )