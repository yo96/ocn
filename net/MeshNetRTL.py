from pymtl        import *
from pclib.ifcs   import InValRdyBundle, OutValRdyBundle, ValRdyBundle
from pclib.ifcs   import NetMsg
from pclib.rtl    import NormalQueue

from MeshRouterRTL import MeshRouterRTL

class MeshNetRTL( Model ):

  def __init__( s, 
                num_ports     = 5,
                num_routers   = 4,
                mesh_wid      = 2,
                mesh_ht       = 2, 
                payload_nbits = 32 ):
    # Network parameters 
    opaque_nbits = 8
    num_routers  = mesh_wid * mesh_ht
    addr_nbits   = clog2( num_routers )
    id_nbits     = addr_nbits
    msg_type     = NetMsg(num_routers, 2**opaque_nbits, payload_nbits)

    DIR_N = 1
    DIR_S = 3
    DIR_E = 2
    DIR_W = 0
    DIR_C = 4

    #wid = clog2( num_routers )
    #ht  = clog2( num_routers )
    wid  = mesh_wid
    ht   = mesh_ht

    # interface 
    s.in_ =  InValRdyBundle[num_routers]( msg_type )
    s.out = OutValRdyBundle[num_routers]( msg_type )

    # components 
    # TODO : calculate number of routers correctly
    #        calculate number of channels correctly
    s.routers              = MeshRouterRTL[num_routers](payload_nbits = 32,
                                                        num_routers=num_routers,
                                                        num_ports=num_ports)
    s.channel_queues_x_2   = NormalQueue[(wid-1)*ht](2, msg_type)
    s.channel_queues_x_0   = NormalQueue[(wid-1)*ht](2, msg_type)
    s.channel_queues_y_2   = NormalQueue[(ht-1)*wid](2, msg_type)
    s.channel_queues_y_0   = NormalQueue[(ht-1)*wid](2, msg_type)
    s.router_ids           =     OutPort[num_routers]( id_nbits  )

    # connecting components 
    for i in range( ht ):
      for j in range( wid ):
        idx = i*wid + j
        # set router ids, connect in/out for each router
        s.connect_pairs( 
          s.router_ids[idx],              idx,
          s.routers[idx].router_id,       idx,
          s.routers[idx].row_min,         i*wid,
          s.routers[idx].row_max,         i*wid+wid-1,
          s.routers[idx].out[DIR_C],      s.out[idx],
          s.routers[idx].in_[DIR_C],      s.in_[idx]
        )
        # connect channels in x direction
        if( j<wid-1 ):
          s.connect_pairs(
            s.routers[idx].out[DIR_E],   s.channel_queues_x_2[i*(wid-1)+j].enq,
            s.channel_queues_x_2[i*(wid-1)+j].deq, s.routers[idx+1].in_[DIR_W],
            s.routers[idx].in_[DIR_E],   s.channel_queues_x_0[i*(wid-1)+j].deq,
            s.channel_queues_x_0[i*(wid-1)+j].enq, s.routers[idx+1].out[DIR_W]
          )
        #connect channels in y direction
        if( i<ht-1 ):
          s.connect_pairs(
            s.routers[idx].out[DIR_S],   s.channel_queues_y_2[i*wid+j].enq,
            s.channel_queues_y_2[i*wid+j].deq, s.routers[idx+wid].in_[DIR_N],
            s.routers[idx].in_[DIR_S],   s.channel_queues_y_0[i*wid+j].deq,
            s.channel_queues_y_0[i*wid+j].enq, s.routers[idx+wid].out[DIR_N]
          )        


  def line_trace( s ):
    return "".join( [ x.line_trace() for x in s.routers] )