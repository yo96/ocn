from pclib.ifcs     import NetMsg
from random import randint

#-------------------------------------------------------------------------
# Helper functions
#-------------------------------------------------------------------------

def mk_msg( src, dest, opaque, payload,
            payload_nbits=32, opaque_nbits=8, num_ports=4 ):
  """Utility function to create a NetMsg object."""

  msg         = NetMsg( num_ports, 2**opaque_nbits, payload_nbits )
  msg.src     = src
  msg.dest    = dest
  msg.opaque  = opaque
  msg.payload = payload

  return msg

def mk_net_msgs( nports, msg_list ):
  """Utility function to create the msgs from a list of msg parameters."""

  src_msgs  = [ [] for x in xrange(nports) ]
  sink_msgs = [ [] for x in xrange(nports) ]

  for x in msg_list:
    src, dest, opaque, payload = x[0], x[1], x[2], x[3]

    msg = mk_msg( src, dest, opaque, payload, num_ports=nports )
    src_msgs [src ].append( msg )
    sink_msgs[dest].append( msg )

  return [ src_msgs, sink_msgs ]

def random_terminal(num):
  return [randint(0, 3) for _ in xrange(0, num)]

def random_payload(num):
  return [randint(0, 0xffffffff) for _ in xrange(0, num)]

def rand_src_fixed_dest(num,dest):
  srcs = random_terminal(num)
  pay  = random_payload(num)
  return [(srcs[idx],dest,idx,pay[idx]) for idx in range(0, num)]

def rand_dest_fixed_src(num,src):
  dests = random_terminal(num)
  pay  = random_payload(num)
  return [(src,dests[idx],idx,pay[idx]) for idx in range(0, num)]

def rand_src_rand_dest(num):
  srcs  = random_terminal(num)
  dests = random_terminal(num)
  pay   = random_payload(num)
  return [(srcs[idx],dests[idx],idx,pay[idx]) for idx in range(0, num)]


def mk_router_msgs( nrouters, msg_list ):
  """Utility function to create the msgs from a list of msg parameters."""

  src_msgs  = [ [] for x in xrange(nrouters) ]
  sink_msgs = [ [] for x in xrange(nrouters) ]

  for x in msg_list:
    tsrc, tsink, src, dest, opaque, payload = x[0], x[1], x[2], x[3], x[4], x[5]

    msg = mk_msg( src, dest, opaque, payload, num_ports=4 )
    src_msgs [tsrc].append( msg )
    sink_msgs[tsink].append( msg )

  return [ src_msgs, sink_msgs ]