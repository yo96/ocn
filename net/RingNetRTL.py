from pymtl        import *
from pclib.ifcs   import InValRdyBundle, OutValRdyBundle, ValRdyBundle
from pclib.ifcs   import NetMsg
from pclib.rtl    import NormalQueue

from RingRouterRTL import RingRouterRTL
from RingRouterGreedyRTL import RingRouterGreedyRTL
class RingNetRTL( Model ):

  def __init__( s, 
                num_ports     = 3,
                num_routers   = 4,
                payload_nbits = 32,
                routing_algorithm = 'greedy' ):
    # Network parameters 
    opaque_nbits = 8
    addr_nbits   = clog2( num_routers )
    id_nbits     = addr_nbits
    msg_type     = NetMsg(num_routers, 2**opaque_nbits, payload_nbits)

    DIR_W = 0
    DIR_E = 1
    DIR_C = 2

    #wid = clog2( num_routers )
    #ht  = clog2( num_routers )

    # interface 
    s.in_ =  InValRdyBundle[num_routers]( msg_type )
    s.out = OutValRdyBundle[num_routers]( msg_type )

    # components 
    # TODO : calculate number of routers correctly
    #        calculate number of channels correctly
    if routing_algorithm == 'even-odd':
      s.routers            = RingRouterRTL[num_routers](payload_nbits = 32,
                                                        num_routers=num_routers,
                                                        num_ports=num_ports)
    else:
      s.routers            = RingRouterGreedyRTL[num_routers](payload_nbits = 32,
                                                              num_routers=num_routers,
                                                              num_ports=num_ports)
    s.channel_queues_E   = NormalQueue[num_routers](2, msg_type)
    s.channel_queues_W   = NormalQueue[num_routers](2, msg_type)
    s.router_ids         =     OutPort[num_routers]( id_nbits  )

    # connecting components 
    for idx in range( num_routers ):
        # set router ids, connect in/out for each router
        idx_next = (idx+1) % num_routers
        s.connect_pairs( 
          s.router_ids[idx],              idx,
          s.routers[idx].router_id,       idx,
          s.routers[idx].out[DIR_C],      s.out[idx],
          s.routers[idx].in_[DIR_C],      s.in_[idx]
        )

        # connect channels queues        
        s.connect_pairs(
          s.routers[idx].out[DIR_E],   s.channel_queues_E[idx].enq,
          s.channel_queues_E[idx].deq, s.routers[idx_next].in_[DIR_W],
          s.routers[idx].in_[DIR_E],   s.channel_queues_W[idx].deq,
          s.channel_queues_W[idx].enq, s.routers[idx_next].out[DIR_W]
        )


  def line_trace( s ):
    return "".join( [ x.line_trace() for x in s.routers] )