#from RouterRTL_test import *
from TestHelper  import *
from pclib.ifcs  import NetMsg

# This constant specify how many packets will be sent in random tests.
NUM_RAND_PACKETS = 50

def basic_dest( i ):
  nrouters = 4

  pre = i-1 if i>0 else nrouters-1
  nxt = i+1 if i<nrouters-1 else 0

  return mk_router_msgs( nrouters,
#       tsrc tsink src  dest opaque payload
    [ ( 0x0, 0x1,  pre,   i,   0x00,  0xfe ), # deliver to output
      ( 0x2, 0x1,  nxt,   i,   0x01,  0xde ), # deliver to output
    ]
  )

def pass_back( i ):
  nrouters = 4

  pre = i-1 if i>0 else nrouters-1
  nxt = i+1 if i<nrouters-1 else 0

  return mk_router_msgs( nrouters,
#       tsrc tsink src  dest opaque payload
    [ ( 0x2, 0x0,  nxt, pre,   0x00,  0xfe ), # pass back
    ]
  )

def to_self( i ):
  nrouters = 4
  ret = []
  for cnt in xrange(40):
    ret.append((0x1,0x1,i,i,cnt,0xbad))
  return mk_router_msgs( nrouters, ret )

def route_neighbor( i ):
  nrouters = 4

  pre = i-1 if i>0 else nrouters-1
  nxt = i+1 if i<nrouters-1 else 0

  return mk_router_msgs( nrouters,
#       tsrc tsink src  dest opaque payload
    [ ( 0x1, 0x0,    i, pre,   0x00,  0xfe ), # deliver to left neighbor
      ( 0x1, 0x2,    i, nxt,   0x01,  0xde ), # deliver to right neighbor
    ]
  )

def break_ties( i ):
  nrouters = 4
  
  dest = (i+2) % 4

  if i % 2 == 0:
    sink = 0x0
  else:
    sink = 0x2

  return mk_router_msgs( nrouters,
#       tsrc tsink src  dest opaque payload
    [ ( 0x1, sink,   i, dest,  0x04,  0x43 ), # deliver to opposite neighbor
    ]
  )

def back_pressure( i ):
  nrouters = 4
  nxt = i+1 if i<nrouters-1 else 0
  ret = []
  for cnt in xrange(40):
    ret.append((0x1,0x2,i,nxt,cnt,0xbad))
  return mk_router_msgs( nrouters, ret )