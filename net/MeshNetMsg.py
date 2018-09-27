from pymtl import *

#-------------------------------------------------------------------------
# NetMsg
#-------------------------------------------------------------------------
# BitStruct designed to create network messages.
#
#  +--------+--------+-------+-------+--------+---------+
#  | dest_x | dest_y | src_x | src_y | opaque | payload |
#  +--------+--------+-------+-------+--------+---------+
#
#

class MeshNetMsg( BitStructDefinition ):

  def __init__( s, width = 2, height = 2, opaque_nbits = 8, payload_nbits = 32 ):

    # Specify the size of each field
    x_addr_nbits = clog2( width  )
    y_addr_nbits = clog2( height )

    # Specify fields
    s.dest_x    = BitField( x_addr_nbits )
    s.dest_y    = BitField( y_addr_nbits )
    s.src_x     = BitField( x_addr_nbits )
    s.src_y     = BitField( y_addr_nbits )

    # TODO: encode VC id in the opaque field?
    s.opaque  = BitField( opaque_nbits  )
    s.payload = BitField( payload_nbits )

    s.width   = width
    s.height  = height
    s.opaque_nbits  = opaque_nbits
    s.payload_nbits = payload_nbits

  # TODO: Should this be a class method?
  def __str__( s ):
    return "{}:{}:{}:{}".format( s.dest, s.src, s.opaque, s.payload )

#------------------------------------------------------------------------
# Helper function to make a mesh net message
#------------------------------------------------------------------------

def mk_mesh_msg( src_x, src_y, dest_x, dest_y, opaque, payload,
                 mesh_wid = 2, mesh_ht = 2, 
                 opaque_nbits = 8, payload_nbits = 32 ):
  msg = MeshNetMsg( mesh_wid, mesh_ht, opaque_nbits, payload_nbits)
  msg.src_x   = src_x    
  msg.src_y   = src_y    
  msg.dest_x  = dest_x    
  msg.dest_y  = dest_y  
  msg.opaque  = opaque    
  msg.payload = payload  

  return msg
