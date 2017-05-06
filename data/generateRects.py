#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
data = ["        canvas:"]

##  first 2 rows come from .atlas

i  = 0
row  = 0
while row < 2:
  col  = 0
  while col < 20:

    if row == 0:  vert  = " + self.size[1] * .667 )"
    else:  vert  = " + self.size[1] * .333 )"

    data .append( "          Rectangle:" )
    data .append( "            texture:  app.tile[" + str(i) + "]" )
    data .append( "            size:  (self.size[0] / 23,  self.size[1] / 3.3)" )
    data .append( "            pos:  (self.pos[0] + self.size[0] / 20 * " + str(col) + ",  self.pos[1]" + vert )

    i += 1
    col += 1
  row += 1

##  3rd row  = previously used tiles

col  = 0
while col < 20:

  data .append( "          Rectangle:" )
  data .append( "            texture:  app.preTile[" + str(col) + "]" )
  data .append( "            size:  (self.size[0] / 23,  self.size[1] / 3.3)" )
  data .append( "            pos:  (self.pos[0] + self.size[0] / 20 * " + str(col) + ",  self.pos[1] )" )

  col += 1

output  = '\n' .join( data )

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print(output)
