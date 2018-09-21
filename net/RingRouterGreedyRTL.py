#=========================================================================
# RingRouterRTL.py
#=========================================================================

from pymtl      import *
from pclib.ifcs import NetMsg
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.rtl  import NormalQueue, Crossbar
from pclib.rtl  import RoundRobinArbiterEn

#from RouterDpathPRTL import RouterDpathPRTL
#from RouterCtrlPRTL  import RouterCtrlPRTL

class RingRouterGreedyRTL( Model ):
  def __init__ ( s, 
                 payload_nbits = 32, 
                 num_routers   = 4,
                 num_ports     = 3,
                 channel_queue_entries = 2,
                 routing_algorithm = 'deterministic'
                ):
    #-------------------------------------------------------------
    # Parameters & Constants
    #-------------------------------------------------------------
    opaque_nbits = 8
    msg_type   = NetMsg( num_routers, 2**opaque_nbits, payload_nbits)
    sel_nbits  = clog2 ( num_ports   )
    addr_nbits = clog2 ( num_routers )

    addr_offset= addr_nbits+opaque_nbits+payload_nbits
    # routing directions 1 for north, 2 for east, etc
    DIR_W = 0
    DIR_E = 1
    DIR_C = 2
    #-------------------------------------------------------------
    # Interface
    #-------------------------------------------------------------
    s.in_       = InValRdyBundle [num_ports]( msg_type )
    s.out       = OutValRdyBundle[num_ports]( msg_type )
    s.router_id = InPort( addr_nbits ) 
    #s.coord_x   = InPort( addr_nbits )
    #s.coord_y   = InPort( addr_nbits )
    #s.row_min   = InPort( addr_nbits )
    #s.row_max   = InPort( addr_nbits )
    #-------------------------------------------------------------
    # Components
    #-------------------------------------------------------------
    
    # Signals
    s.sels       = Wire[num_ports]( sel_nbits  )
    s.dest       = Wire[num_ports]( addr_nbits )
    s.arbitor_en = Wire( num_ports  )
    s.has_grant  = Wire( num_ports  )
    s.id_odd     = Wire( 1 )
    s.dist_west  = Wire[num_ports]( addr_nbits+1 )
    s.dist_east  = Wire[num_ports]( addr_nbits+1 )

    # Sinal indicating if the id is an even number
    s.connect ( s.id_odd, s.router_id[addr_nbits-1] )

    # Crossbar -- no output buffers
    s.crossbar = m = Crossbar(num_ports, msg_type)
    for i in range( num_ports ):
      s.connect( m.out[i], s.out[i].msg )
      s.connect_wire( dest=m.sel[i], src=s.sels[i])

    # Input buffers
    s.input_buffer = NormalQueue[num_ports](2, msg_type)
    for i in range( num_ports ):
      s.connect_pairs(
        s.input_buffer[i].enq,     s.in_[i],
        s.input_buffer[i].deq.msg, s.crossbar.in_[i]
      )

    # Arbitors
    s.arbitors = RoundRobinArbiterEn[num_ports](num_ports)
    for i in range( num_ports ):
      s.connect_pairs( 
        s.arbitors[i].en, s.arbitor_en[i] 
      )

    #--------------------------------------------------------------
    # Control Logic
    #--------------------------------------------------------------
    @s.combinational
    def getDestAddr():
      for i in range( num_ports ):
        s.dest[i].value = s.input_buffer[i].deq.msg[addr_offset:addr_offset+addr_nbits]

    @s.combinational
    def calculateDistance():
      for i in range( num_ports ):
        if s.dest[i] > s.router_id:
          s.dist_east[i].value = s.dest[i] - s.router_id
          s.dist_west[i].value = (num_routers-1) - s.dest[i] + s.router_id + 1
        else:
          s.dist_east[i].value = (num_routers-1) - s.router_id + s.dest[i] + 1
          s.dist_west[i].value = s.router_id - s.dest[i]

    @s.combinational
    def setCrossbarSel():
      for i in range( num_ports ):
        for j in range( num_ports ):
          if s.arbitors[i].grants[j]:
            s.sels[i].value = j

    @s.combinational
    def setOutVal():
      for i in range( num_ports ):
        s.out[i].val.value = 0
        if s.arbitors[i].grants > 0 :
          s.out[i].val.value = 1


    @s.combinational
    def setDeqRdy():
      for i in range( num_ports ):
        s.has_grant[i].value = 0        
        for j in range( num_ports ):
          if s.arbitors[j].grants[i]:
            s.has_grant[i].value = s.out[j].rdy

      for i in range( num_ports ):
        s.input_buffer[i].deq.rdy.value = s.has_grant[i] 

    @s.combinational
    def setArbitorEnable():
      for i in range( num_ports ):
        s.arbitor_en[i].value = s.out[i].val & s.out[i].rdy 
    
    # Routing Algorithm goes HERE!!!
    # deterministic routing
    @s.combinational
    def setArbitorReq():
      for i in range( num_ports ):
        s.arbitors[i].reqs.value = 0
      for i in range( num_ports ):
        if s.router_id == s.dest[i]:
          s.arbitors[DIR_C].reqs[i].value = s.input_buffer[i].deq.val
        elif s.dist_west[i] < s.dist_east[i]:
          s.arbitors[DIR_W].reqs[i].value = s.input_buffer[i].deq.val
        elif s.dist_west[i] > s.dist_east[i]:
          s.arbitors[DIR_E].reqs[i].value = s.input_buffer[i].deq.val
        else: # break ties
          s.arbitors[DIR_W].reqs[i].value = s.input_buffer[i].deq.val

  # Sublime SFTP test Test 2
  def line_trace( s ):
    in0_str = s.in_[0].to_str( "%02s:%1s>%1s" % ( s.in_[0].msg.opaque, s.in_[0].msg.src, s.in_[0].msg.dest ) )
    in1_str = s.in_[1].to_str( "%02s:%1s>%1s" % ( s.in_[1].msg.opaque, s.in_[1].msg.src, s.in_[1].msg.dest ) )
    in2_str = s.in_[2].to_str( "%02s:%1s>%1s" % ( s.in_[2].msg.opaque, s.in_[2].msg.src, s.in_[2].msg.dest ) )
    return "( {},w:{},e:{})({}|{}|{} )".format( s.router_id, s.dist_west[2], s.dist_east[2],
                                                in0_str, in1_str, in2_str )  
