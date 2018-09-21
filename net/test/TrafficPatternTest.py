from TestHelper  import *
from pclib.ifcs  import NetMsg
import random

# This constant specify how many packets will be sent in each test.
NUM_PACKETS = 50

def nearest_neighbour():
  nports = 4
  ret = []
  for i in range(0,NUM_PACKETS):
    src  = i % 4
    dest = (i+1) % 4
    ret.append((src,dest,i,0xbaad))
  return mk_net_msgs( nports, ret )

def hotspot():
  nports = 4
  ret = []
  for i in range(0,NUM_PACKETS):
    src  = i % 4
    if random.random() <= 0.25:
      ret.append((src,3,i,0xbaad))
  return mk_net_msgs( nports, ret )

def oversubscribed_hotspot():
  nports = 4
  ret = []
  for i in range(0,NUM_PACKETS):
    src  = i % 4
    ret.append((src,3,i,0xbaad))
  return mk_net_msgs( nports, ret )

def opposite():
  nports = 4
  ret = []
  for i in range(0,NUM_PACKETS):
    src  = i % 4
    dest = (i+2) % 4
    ret.append((src,dest,i,0xbaad))
  return mk_net_msgs( nports, ret )