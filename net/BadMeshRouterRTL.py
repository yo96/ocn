#=========================================================================
# MeshRouterRTL.py
#=========================================================================

from pymtl      import *
from pclib.ifcs import NetMsg
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.rtl  import NormalQueue, Crossbar
from pclib.rtl  import RoundRobinArbiterEn

#from RouterDpathPRTL import RouterDpathPRTL
#from RouterCtrlPRTL  import RouterCtrlPRTL

class BadMeshRouterRTL( Model ):
  def __init__ ( s, 
                 payload_nbits = 32, 
                 num_routers   = 4,
                 num_ports     = 5,
                ):
    #-------------------------------------------------------------
    # Parameters & Constants
    #-------------------------------------------------------------
    opaque_nbits = 8
    msg_type   = NetMsg( num_routers, 2**opaque_nbits, payload_nbits)
    sel_nbits  = clog2 ( num_ports   )
    addr_nbits = clog2 ( num_routers )
    port_nbits = clog2 ( num_ports   ) # not useful anymore
    addr_offset= addr_nbits+opaque_nbits+payload_nbits
    # routing directions 1 for north, 2 for east, etc
    DIR_N = 1
    DIR_S = 3
    DIR_E = 2
    DIR_W = 0
    DIR_C = 4
    #-------------------------------------------------------------
    # Interface
    #-------------------------------------------------------------
    s.in_       = InValRdyBundle [num_ports]( msg_type )
    s.out       = OutValRdyBundle[num_ports]( msg_type )
    s.router_id = InPort( addr_nbits ) 
    #s.coord_x   = InPort( addr_nbits )
    #s.coord_y   = InPort( addr_nbits )
    s.row_min    = InPort( addr_nbits )
    s.row_max    = InPort( addr_nbits )
    #-------------------------------------------------------------
    # Components
    #-------------------------------------------------------------
    
    # Signals
    s.sels       = Wire[num_ports]( sel_nbits  )
    s.dest       = Wire[num_ports]( addr_nbits )
    s.arbitor_en = Wire( num_ports )
    s.has_grant  = Wire( num_ports )
    #s.deq_rdy    = Wire( num_ports )


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
        s.dest[i].value = s.input_buffer[i].deq.msg[(payload_nbits+10):(payload_nbits+12)]

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
    # y-dimension-order routing
    @s.combinational
    def setArbitorReq():
      for i in range( num_ports ):
        s.arbitors[i].reqs.value = 0
      for i in range( num_ports ):
        if s.router_id == s.dest[i]:
          s.arbitors[DIR_C].reqs[i].value = s.input_buffer[i].deq.val
        elif s.dest[i] < s.row_min:
          s.arbitors[DIR_N].reqs[i].value = s.input_buffer[i].deq.val
        elif s.dest[i] > s.row_max:
          s.arbitors[DIR_S].reqs[i].value = s.input_buffer[i].deq.val
        elif s.dest[i] < s.router_id:
          s.arbitors[DIR_W].reqs[i].value = s.input_buffer[i].deq.val
        else:
          s.arbitors[DIR_E].reqs[i].value = s.input_buffer[i].deq.val

    
  def line_trace( s ):
    in0_str = s.in_[0].to_str( "%02s:%1s>%1s" % ( s.in_[0].msg.opaque, s.in_[0].msg.src, s.in_[0].msg.dest ) )
    in1_str = s.in_[1].to_str( "%02s:%1s>%1s" % ( s.in_[1].msg.opaque, s.in_[1].msg.src, s.in_[1].msg.dest ) )
    in2_str = s.in_[2].to_str( "%02s:%1s>%1s" % ( s.in_[2].msg.opaque, s.in_[2].msg.src, s.in_[2].msg.dest ) )
    in3_str = s.in_[3].to_str( "%02s:%1s>%1s" % ( s.in_[3].msg.opaque, s.in_[3].msg.src, s.in_[3].msg.dest ) )
    in4_str = s.in_[4].to_str( "%02s:%1s>%1s" % ( s.in_[4].msg.opaque, s.in_[4].msg.src, s.in_[4].msg.dest ) )
    return "(id:{})(W:{},sel:{}|N:{},sel:{}|E:{},sel:{}|S:{},sel:{}|{},sel:{})".format( s.router_id,
                                                in0_str,s.sels[0], in1_str,s.sels[1], in2_str,s.sels[2], in3_str,s.sels[3], in4_str,s.sels[4])  