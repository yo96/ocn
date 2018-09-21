from TestHelper  import *
from pclib.ifcs  import NetMsg

# This constant specify how many packets will be sent in random tests.
NUM_RAND_PACKETS = 50

def one_pkt_one_self():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  0,   0x00,  0xc001 ),
    ]
  )

def a2b_1pkt():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  2,   0x01,  0xc001 ),
      ( 1,  0,   0x10,  0xcafe ),
      ( 2,  3,   0x23,  0xdead ),
      ( 3,  1,   0x32,  0xd00d ),
    ]
  )

def a2b_4pkt():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  2,   0x01,  0xc001 ),
      ( 0,  2,   0x01,  0xc001 ),
      ( 0,  2,   0x01,  0xc001 ),
      ( 0,  2,   0x01,  0xc001 ),
      ( 1,  0,   0x10,  0xcafe ),
      ( 1,  0,   0x10,  0xcafe ),
      ( 1,  0,   0x10,  0xcafe ),
      ( 1,  0,   0x10,  0xcafe ),
      ( 2,  3,   0x23,  0xdead ),
      ( 2,  3,   0x23,  0xdead ),
      ( 2,  3,   0x23,  0xdead ),
      ( 2,  3,   0x23,  0xdead ),
      ( 3,  1,   0x32,  0xd00d ),
      ( 3,  1,   0x32,  0xd00d ),
      ( 3,  1,   0x32,  0xd00d ),
      ( 3,  1,   0x32,  0xd00d ),
    ]
  )

def a2b_all():
  nports = 4
  ret = []
  for src in range(0,4):
    for dest in range(0,4):
      if src != dest:
        ret.append((src,dest,src*16+dest,0xc001))
  return mk_net_msgs( nports, ret )


def single_src_basic():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  0,   0x00,  0xce ),
      ( 0,  1,   0x01,  0xff ),
      ( 0,  2,   0x02,  0x80 ),
      ( 0,  3,   0x03,  0xc0 ),
    ]
  )

def single_src_4pkt():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  0,   0x00,  0xce ),
      ( 0,  0,   0x00,  0xce ),
      ( 0,  0,   0x01,  0xce ),
      ( 0,  0,   0x02,  0xce ),
      ( 0,  1,   0x03,  0xff ),
      ( 0,  1,   0x04,  0xff ),
      ( 0,  1,   0x05,  0xff ),
      ( 0,  1,   0x06,  0xff ),
      ( 0,  2,   0x07,  0x80 ),
      ( 0,  2,   0x08,  0x80 ),
      ( 0,  2,   0x09,  0x80 ),
      ( 0,  2,   0x0a,  0x80 ),
      ( 0,  3,   0x0b,  0xc0 ),
      ( 0,  3,   0x0c,  0xc0 ),
      ( 0,  3,   0x0d,  0xc0 ),
      ( 0,  3,   0x0e,  0xc0 ),
    ]
  )

def single_src_1pkt_all():
  nports = 4
  ret = []
  cnt = 0
  for src in range(0,4):
    for dest in range(0,4):
      ret.append((src,dest,cnt,0xdead))
      cnt = cnt + 1
  return mk_net_msgs( nports, ret )

def single_src_4pkt_all():
  nports = 4
  ret = []
  cnt = 0
  for src in range(0,4):
    for dest in range(0,4):
      for i in range(0,4):
        ret.append((src,dest,cnt,0xdead))
        cnt = cnt + 1
  return mk_net_msgs( nports, ret )

def single_neighbor_basic():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  1,   0x00,  0xce ),
      ( 1,  2,   0x01,  0xff ),
      ( 2,  3,   0x02,  0x80 ),
      ( 3,  0,   0x03,  0xc0 ),
    ]
  )

def both_neighbor_basic():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  3,   0x00,  0xce ),
      ( 0,  1,   0x01,  0xff ),
      ( 1,  0,   0x01,  0xff ),
      ( 1,  2,   0x01,  0xff ),
      ( 2,  1,   0x02,  0x80 ),
      ( 2,  3,   0x02,  0x80 ),
      ( 3,  2,   0x03,  0xc0 ),
      ( 3,  0,   0x03,  0xc0 ),
    ]
  )

def single_neighbor_4pkt():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  1,   0x00,  0xce ),
    	( 0,  1,   0x00,  0xce ),
    	( 0,  1,   0x00,  0xce ),
    	( 0,  1,   0x00,  0xce ),
      ( 1,  2,   0x01,  0xff ),
      ( 1,  2,   0x01,  0xff ),
      ( 1,  2,   0x01,  0xff ),
      ( 1,  2,   0x01,  0xff ),
      ( 2,  3,   0x02,  0x80 ),
      ( 2,  3,   0x02,  0x80 ),
      ( 2,  3,   0x02,  0x80 ),
      ( 2,  3,   0x02,  0x80 ),
      ( 3,  0,   0x03,  0xc0 ),
      ( 3,  0,   0x03,  0xc0 ),
      ( 3,  0,   0x03,  0xc0 ),
      ( 3,  0,   0x03,  0xc0 ),
    ]
  )

def both_neighbor_4pkt():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  3,   0x00,  0xce ),
	    ( 0,  3,   0x00,  0xce ),
	    ( 0,  3,   0x00,  0xce ),
	    ( 0,  3,   0x00,  0xce ),
	    ( 0,  3,   0x00,  0xce ),
      ( 0,  1,   0x01,  0xff ),
      ( 0,  1,   0x01,  0xff ),
      ( 0,  1,   0x01,  0xff ),
      ( 0,  1,   0x01,  0xff ),
      ( 0,  1,   0x01,  0xff ),
      ( 1,  0,   0x01,  0xff ),
      ( 1,  0,   0x01,  0xff ),
      ( 1,  0,   0x01,  0xff ),
      ( 1,  0,   0x01,  0xff ),
      ( 1,  0,   0x01,  0xff ),
      ( 1,  2,   0x01,  0xff ),
      ( 1,  2,   0x01,  0xff ),
      ( 1,  2,   0x01,  0xff ),
      ( 1,  2,   0x01,  0xff ),
      ( 1,  2,   0x01,  0xff ),
      ( 2,  1,   0x02,  0x80 ),
      ( 2,  1,   0x02,  0x80 ),
      ( 2,  1,   0x02,  0x80 ),
      ( 2,  1,   0x02,  0x80 ),
      ( 2,  1,   0x02,  0x80 ),
      ( 2,  3,   0x02,  0x80 ),
      ( 2,  3,   0x02,  0x80 ),
      ( 2,  3,   0x02,  0x80 ),
      ( 2,  3,   0x02,  0x80 ),
      ( 2,  3,   0x02,  0x80 ),
      ( 3,  2,   0x03,  0xc0 ),
      ( 3,  2,   0x03,  0xc0 ),
      ( 3,  2,   0x03,  0xc0 ),
      ( 3,  2,   0x03,  0xc0 ),
      ( 3,  2,   0x03,  0xc0 ),
      ( 3,  0,   0x03,  0xc0 ),
      ( 3,  0,   0x03,  0xc0 ),
      ( 3,  0,   0x03,  0xc0 ),
      ( 3,  0,   0x03,  0xc0 ),
      ( 3,  0,   0x03,  0xc0 ),
    ]
  )