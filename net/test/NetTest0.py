from TestHelper  import *
from pclib.ifcs  import NetMsg

# This constant specify how many packets will be sent in random tests.
NUM_RAND_PACKETS = 50

def one_pkt_self():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  0,   0x00,  0xc001 ),
      ( 1,  1,   0x01,  0xcafe ),
      ( 2,  2,   0x02,  0xc001 ),
      ( 3,  3,   0x03,  0xcafe ),
    ]
  )

def single_dest_2router():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  2,   0x00,  0xc001 ),
      ( 0,  2,   0x01,  0xc001 ),
      #( 0,  2,   0x02,  0xc001 ),
      #( 0,  2,   0x03,  0xd00d ),
      ( 1,  2,   0x03,  0xff ),
      ( 1,  2,   0x04,  0xff ),
      #( 1,  2,   0x05,  0xff ),
      #( 1,  2,   0x06,  0xff ),
    ]
  )

def dead_lock():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  2,   0x00,  0xc001 ),
      ( 0,  2,   0x00,  0xc001 ),
      ( 0,  2,   0x00,  0xc001 ),
      ( 0,  2,   0x00,  0xc001 ),
      ( 0,  2,   0x00,  0xc001 ),
      ( 0,  2,   0x00,  0xc001 ),
      ( 0,  2,   0x00,  0xc001 ),
      ( 0,  2,   0x00,  0xc001 ),
      ( 0,  2,   0x00,  0xc001 ),
( 0,  2,   0x00,  0xc001 ),
( 0,  2,   0x00,  0xc001 ),
( 0,  2,   0x00,  0xc001 ),
( 0,  2,   0x00,  0xc001 ),
( 0,  2,   0x00,  0xc001 ),
( 0,  2,   0x00,  0xc001 ),
( 0,  2,   0x00,  0xc001 ),
( 0,  2,   0x00,  0xc001 ),
( 0,  2,   0x00,  0xc001 ),
( 0,  2,   0x00,  0xc001 ),

      ( 1,  3,   0x01,  0xc001 ),
      ( 1,  3,   0x01,  0xd00d ),
      ( 1,  3,   0x01,  0xd00d ),
      ( 1,  3,   0x01,  0xd00d ),
      ( 1,  3,   0x01,  0xd00d ),
      ( 1,  3,   0x01,  0xd00d ),
      ( 1,  3,   0x01,  0xd00d ),
      ( 1,  3,   0x01,  0xd00d ),
      ( 1,  3,   0x01,  0xd00d ),
( 1,  3,   0x01,  0xd00d ),
( 1,  3,   0x01,  0xd00d ),
( 1,  3,   0x01,  0xd00d ),
( 1,  3,   0x01,  0xd00d ),
( 1,  3,   0x01,  0xd00d ),
( 1,  3,   0x01,  0xd00d ),
( 1,  3,   0x01,  0xd00d ),
( 1,  3,   0x01,  0xd00d ),
( 1,  3,   0x01,  0xd00d ),
( 1,  3,   0x01,  0xd00d ),

      ( 2,  0,   0x02,  0xd00d ),
      ( 2,  0,   0x02,  0xd00d ),
      ( 2,  0,   0x02,  0xd00d ),
      ( 2,  0,   0x02,  0xd00d ),
      ( 2,  0,   0x02,  0xd00d ),
      ( 2,  0,   0x02,  0xd00d ),
      ( 2,  0,   0x02,  0xd00d ),
      ( 2,  0,   0x02,  0xd00d ),
      ( 2,  0,   0x02,  0xd00d ),
( 2,  0,   0x02,  0xd00d ),
( 2,  0,   0x02,  0xd00d ),
( 2,  0,   0x02,  0xd00d ),
( 2,  0,   0x02,  0xd00d ),
( 2,  0,   0x02,  0xd00d ),
( 2,  0,   0x02,  0xd00d ),
( 2,  0,   0x02,  0xd00d ),
( 2,  0,   0x02,  0xd00d ),
( 2,  0,   0x02,  0xd00d ),
( 2,  0,   0x02,  0xd00d ),

      ( 3,  1,   0x03,  0xd00d ),
      ( 3,  1,   0x03,  0xd00d ),
      ( 3,  1,   0x03,  0xd00d ),
      ( 3,  1,   0x03,  0xd00d ),
      ( 3,  1,   0x03,  0xd00d ),
      ( 3,  1,   0x03,  0xd00d ),
      ( 3,  1,   0x03,  0xd00d ),
      ( 3,  1,   0x03,  0xd00d ),
      ( 3,  1,   0x03,  0xd00d ),
( 3,  1,   0x03,  0xd00d ),
( 3,  1,   0x03,  0xd00d ),
( 3,  1,   0x03,  0xd00d ),
( 3,  1,   0x03,  0xd00d ),
( 3,  1,   0x03,  0xd00d ),
( 3,  1,   0x03,  0xd00d ),
( 3,  1,   0x03,  0xd00d ),
( 3,  1,   0x03,  0xd00d ),
( 3,  1,   0x03,  0xd00d ),
( 3,  1,   0x03,  0xd00d ),

    ] )

def four_pkt_self():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  0,   0x00,  0xc001 ),
      ( 0,  0,   0x01,  0xc001 ),
      ( 0,  0,   0x02,  0xc001 ),
      ( 0,  0,   0x03,  0xd00d ),
      ( 1,  1,   0x10,  0xcafe ),
      ( 1,  1,   0x11,  0xcafe ),
      ( 1,  1,   0x12,  0xcafe ),
      ( 1,  1,   0x13,  0xd00d ),
      ( 2,  2,   0x20,  0xc001 ),
      ( 2,  2,   0x21,  0xc001 ),
      ( 2,  2,   0x22,  0xc001 ),
      ( 2,  2,   0x23,  0xd00d ),
      ( 3,  3,   0x30,  0xcafe ),
      ( 3,  3,   0x31,  0xcafe ),
      ( 3,  3,   0x32,  0xcafe ),
      ( 3,  3,   0x33,  0xd00d ),
    ]
  )

def var_pkt_self():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  0,   0x00,  0xc001 ),
      ( 1,  1,   0x10,  0xcafe ),
      ( 2,  2,   0x20,  0xc001 ),
      ( 3,  3,   0x30,  0xcafe ),
      ( 1,  1,   0x11,  0xcafe ),
      ( 2,  2,   0x21,  0xc001 ),
      ( 3,  3,   0x31,  0xcafe ),
      ( 2,  2,   0x22,  0xc001 ),
      ( 3,  3,   0x32,  0xcafe ),
      ( 3,  3,   0x33,  0xcafe ),
    ]
  )

def a2b_b2a_1pkt():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  1,   0x01,  0xc001 ),
      ( 1,  0,   0x10,  0xcafe ),
      ( 2,  3,   0x23,  0xdead ),
      ( 3,  2,   0x32,  0xd00d ),
    ]
  )

def a2b_b2a_4pkt():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  1,   0x01,  0xc001 ),
      ( 0,  1,   0x01,  0xc001 ),
      ( 0,  1,   0x01,  0xc001 ),
      ( 0,  1,   0x01,  0xc001 ),
      ( 1,  0,   0x10,  0xcafe ),
      ( 1,  0,   0x10,  0xcafe ),
      ( 1,  0,   0x10,  0xcafe ),
      ( 1,  0,   0x10,  0xcafe ),
      ( 2,  3,   0x23,  0xdead ),
      ( 2,  3,   0x23,  0xdead ),
      ( 2,  3,   0x23,  0xdead ),
      ( 2,  3,   0x23,  0xdead ),
      ( 3,  2,   0x32,  0xd00d ),
      ( 3,  2,   0x32,  0xd00d ),
      ( 3,  2,   0x32,  0xd00d ),
      ( 3,  2,   0x32,  0xd00d ),
    ]
  )

def a2b_b2a_all():
  nports = 4
  ret = []
  for src0 in range(0,4):
    for dest0 in range(0,4):
      if src0 != dest0:
        for i in range (0,4):
          if (i!=src0 and i!=dest0):
            src1 = i
        for i in range (0,4):
          if (i!=src0 and i!=dest0 and i!=src1):
            dest1 = i
        ret.extend(
          [(src0,dest0,src0*16+dest0,0xc001),(dest0,src0,dest0*16+src0,0xc001),
           (src1,dest1,src1*16+dest1,0xd00d),(dest1,src1,dest1*16+src1,0xd00d)])
  return mk_net_msgs( nports, ret )

def single_dest_basic():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  3,   0x00,  0xce ),
      ( 1,  3,   0x01,  0xff ),
      ( 2,  3,   0x02,  0x80 ),
      ( 3,  3,   0x03,  0xc0 ),
    ]
  )

def single_dest_4pkt():
  nports = 4
  return mk_net_msgs( nports,
#       src dest opaque payload
    [ ( 0,  2,   0x00,  0xce ),
      ( 0,  2,   0x00,  0xce ),
      ( 0,  2,   0x01,  0xce ),
      ( 0,  2,   0x02,  0xce ),
      ( 1,  2,   0x03,  0xff ),
      ( 1,  2,   0x04,  0xff ),
      ( 1,  2,   0x05,  0xff ),
      ( 1,  2,   0x06,  0xff ),
      ( 2,  2,   0x07,  0x80 ),
      ( 2,  2,   0x08,  0x80 ),
      ( 2,  2,   0x09,  0x80 ),
      ( 2,  2,   0x0a,  0x80 ),
      ( 3,  2,   0x0b,  0xc0 ),
      ( 3,  2,   0x0c,  0xc0 ),
      ( 3,  2,   0x0d,  0xc0 ),
      ( 3,  2,   0x0e,  0xc0 ),
    ]
  )

def single_dest_1pkt_all():
  nports = 4
  ret = []
  cnt = 0
  for dest in range(0,4):
    for src in range(0,4):
      ret.append((src,dest,cnt,0xdead))
      cnt = cnt + 1
  return mk_net_msgs( nports, ret )

def single_dest_4pkt_all():
  nports = 4
  ret = []
  cnt = 0
  for dest in range(0,4):
    for src in range(0,4):
      for i in range(0,4):
        ret.append((src,dest,cnt,0xdead))
        cnt = cnt + 1
  return mk_net_msgs( nports, ret )

def crazy_pressure():
  nports = 4
  ret = []
  for cnt in range(0,20):
    for src in range(0,4):
      for dest in range(0,4):
        ret.append((src,dest,cnt,0xc001))
  return mk_net_msgs( nports, ret )

def single_sink_pressure(dest):
  nports = 4
  ret = []
  for cnt in range(0,20):
    for src in range(0,4):
        ret.append((src,dest,cnt,0xc001))
  return mk_net_msgs( nports, ret )

def one_to_one_pressure(src,dest):
  nports = 4
  ret = []
  for cnt in range(0,20):
        ret.append((src,dest,cnt,0xc001))
  return mk_net_msgs( nports, ret )


#------------------------------------------------------------------------------
#-----------------------Random src to fixed dest-------------------------------
#------------------------------------------------------------------------------
def rand_src_to_0():
  nports = 4
  return mk_net_msgs( nports, rand_src_fixed_dest(NUM_RAND_PACKETS,0))

def rand_src_to_1():
  nports = 4
  return mk_net_msgs( nports, rand_src_fixed_dest(NUM_RAND_PACKETS,1))

def rand_src_to_2():
  nports = 4
  return mk_net_msgs( nports, rand_src_fixed_dest(NUM_RAND_PACKETS,2))

def rand_src_to_3():
  nports = 4
  return mk_net_msgs( nports, rand_src_fixed_dest(NUM_RAND_PACKETS,3))
#------------------------------------------------------------------------------
#-----------------------Fixed src to random dest-------------------------------
#------------------------------------------------------------------------------
def rand_dest_from_0():
  nports = 4
  return mk_net_msgs( nports, rand_dest_fixed_src(NUM_RAND_PACKETS,0))

def rand_dest_from_1():
  nports = 4
  return mk_net_msgs( nports, rand_dest_fixed_src(NUM_RAND_PACKETS,1))

def rand_dest_from_2():
  nports = 4
  return mk_net_msgs( nports, rand_dest_fixed_src(NUM_RAND_PACKETS,2))

def rand_dest_from_3():
  nports = 4
  return mk_net_msgs( nports, rand_dest_fixed_src(NUM_RAND_PACKETS,3))
#------------------------------------------------------------------------------
#-----------------------random src to random dest------------------------------
#------------------------------------------------------------------------------
def rand_src_2_rand_dest():
  nports = 4
  return mk_net_msgs(nports, rand_src_rand_dest(NUM_RAND_PACKETS))
