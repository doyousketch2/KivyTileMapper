#!/usr/bin/env python3
# -*-coding: utf-8 -*-
##=========================================================
##  tilemapper.py                               28 Apr 2017
##
##  Generates a portable pixmap for game design
##  from spritesheet and kivy .atlas file
##
##  Eli Leigh Innis
##  Twitter :  @ Doyousketch2
##  Email :  Doyousketch2 @ yahoo.com
##
##  GNU GPLv3                 gnu.org/licenses/gpl-3..html
##=========================================================
##  required  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##  you'll need kivy:
##  ( debian )
##        sudo pip3 install kivy
##  ( linux )
##        sudo python3 -m pip install kivy
##  ( mac )
##        sudo easy_install pip
##        python -m pip install kivy
##  ( win )
##        py -m pip install kivy
##=========================================================
##  libs  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import  os
import  sys

from  kivy .app         import  App                  ## GUI
from  kivy .graphics      import *
from  kivy .lang            import  Builder
from  kivy .uix .image        import  Image
from  kivy .uix .screenmanager  import  ( ScreenManager,
                                      NoTransition, Screen )
from  kivy .core .window      import  Window
from  kivy .clock           import  Clock

##=========================================================
##  config  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

WIDTH  = 800
HEIGHT  = 600

##=========================================================
##  script  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Window .size  = ( WIDTH,  HEIGHT )

##  Kivy sux, need 'Builder' when using ScreenManager...
Builder .load_file( './tilemapper.kv' )


class FileScreen( Screen ):

  def select( self, *args ):
    self .selection  = args[1][0]
    try:
      app .selected  = self .selection
      self .label .text  = app .selected
    except:  pass


  def choice( self ):

    app .path,  app .ext  = os .path .splitext( app .selected )

    if '/' in app .path:   ## Unix, Linux, Android, Mac OSX, iOS
      app .filename  = app .path .split( '/' )[-1]
    else:   ## the other OS
      app .filename  = app .path .split( '\\' )[-1]
    print( app .filename )

    with open( './data/' + app .filename + '.atlas' ) as JSONfile:   ## .atlas is a JSON file

      JSONfile .readline()   ## skip the first line, 'cuz it's just a curly bracket  {

                                                             ## "spritesheet.png": {
      spritesheet  = JSONfile .readline() .split( '"' )[1]   ## spritesheet.png  -not used

                                               ## "Name":  [ xpos, ypos,  w, h],\n
      line = JSONfile .readline() .strip()   ## "Name":  [ xpos, ypos,  w, h],

      values  = line .split( '[' )[1] .split( ']' )[0] .split( ',' )   ## xpos, ypos,  w, h

      app .mapPxlW  = int( values[2] .strip())   ## w     Map Tile width
      app .mapPxlH  = int( values[3] .strip())   ## h     "    "    height

      i  = 0
      for line in JSONfile:
        if line .strip() .startswith( '"' ):   ## skip closing brackets }
          app .name .append( line .split( '"' )[1] )   ## Name
          i += 1

    i = app .tileX
    while i < len( app .Tile ):
      app .Tile[i]  = Image( source = 'atlas://' + app .path + '/' + app .name[i] ) .texture
      i += 1

    Window .size  = ( int( app .mapPxlW * app .mapX * app .zoom ),  int( app .mapPxlH * app .mapY * app .zoom * 1.5 ))
    self .manager .switch_to( TileScreen())


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TileScreen( Screen ):

  def refreshTiles( self ):   ## tiles from the spritesheet
    off  = app .offset

    if app .once == 0:
      self .ids .topRow .size[1]  = app .tilePxlH * 2
      self .ids .bottomRow .size[1]  = app .tilePxlH * 2
      app .origin  = self .ids .tileSet .pos
      app .mapOrigin  = self .ids .Map .pos
      app .mapSize  = ( app .mapPxlW,  app .mapPxlH )

      i  = 0
      while i < app .tileX -1:
        app .prevNums[i] = i
        i += 1

      app .once  = 1

    self .ids .tileSet .canvas .clear()

    app .tilePxlW  = self .ids .tileSet .size[0] / 20
    app .tilePxlH  = self .ids .tileSet .size[1] / 3

    app .outlineSize  = ( app .tilePxlW,  app .tilePxlH)
    app .tileSize  = ( app .tilePxlW * .9,  app .tilePxlH * .9 )

    i  = 0
    while i < app .tileX * app .tileY:

      col  = app .tilePxlW * ( i % 20 )
      row  = app .tilePxlH * int( i / 20 )

      tilePos  = ( app .origin[0] + col + app .tilePxlW * .04,  app .origin[1] + row )
      if app .currentNum >= app .tileX:
        outlinePos  = ( app .origin[0],  app .origin[1] - app .tilePxlH * .04 )
      else:
        outlinePos  = ( app .origin[0] + app .currentNum * app .tilePxlW,  app .origin[1] - app .tilePxlH * .04 )

      with self .ids .tileSet .canvas:
        if i == 0:
          Color( 1, .1, .1,  1 )   ## red outline
          Rectangle( size = app .outlineSize,  pos = outlinePos )
          Color( 1, 1, 1,  1 )   ## change back to white, or Tile colors go wonky
        Rectangle( texture = app .Tile[i],  size = app .tileSize,  pos = tilePos )

      off += 1
      if off == len( app .name ):  off  = 0
      i += 1


  def refreshMap( self ):   ## the Map you're drawing
    self .ids .Map .canvas .clear()

    i  = 0
    while i < app .mapX * app .mapY:
      col  = app .mapPxlW * ( i % app .mapX )
      row  = app .mapPxlH * int( i / app .mapX )

      mapOrigin  = ( ( app .mapOrigin[0] + col ),  ( app .mapOrigin[1] + row ))

      with self .ids .tileSet .canvas:
        Rectangle( texture = app .Map[i],  size = app .mapSize,  pos = mapOrigin )

      i += 1


  def select( self ):   ## click a Tile

    mX  = Window .mouse_pos[0]
    mY  = Window .mouse_pos[1]

    mX -= self .ids .scrollLeft .size[0]                         ## left scroll button
    mY -= self .ids .Map .size[1]                                    ## Map height
    mY -= self .ids .topRow .size[1] + self .ids .bottomRow .size[1]   ## button height

    col  = int( mX / app .tilePxlW )
    row  = int( mY / app .tilePxlH )

    app .currentNum  = col + row * 20

    if row < 1:
      app .currentText  = app .name[ app .prevNums[ col ] ]
      print('Offset:', app .offset, '  Num:', col, '  eq:',  app .offset + col)

    else:
      if app .currentNum + app .offset >= len( app .name ):
        app .currentText  = app .name[ app .currentNum + app .offset - len( app .name ) ]
      else:
        app .currentText  = app .name[ app .currentNum + app .offset ]

      print('Offset:', app .offset, '  Num:', app .currentNum, '  equals:',  app .offset + app .currentNum)
      if app .currentNum + app .offset not in app .prevNums:   ##  start at right, shuffle left
        print('sorting  ',  app .prevNums[0],  app .prevNums[1],  app .prevNums[2],  app .prevNums[3])
        i  = app .tileX -1
        while i >= 1:
          app .prevNums[i]  = app .prevNums[i -1]
          app .Tile[i]  = Image( source = 'atlas://' + app .path + '/' + app .name[ app .prevNums[i] ]) .texture
          i -= 1
        app .prevNums[0]  = app .currentNum + app .offset

        app .Tile[0]  = Image( source = 'atlas://' + app .path + '/' + app .name[ app .prevNums[0] ]) .texture

      if app .name[ app .prevNums[0] ] != app .currentText:
        print('resorting  ',  app .prevNums[0],  app .prevNums[1],  app .prevNums[2],  app .prevNums[3])
        i  = app .tileX -1
        found  = 0
        while i >= 1:
          if app .name[ app .prevNums[i] ] == app .currentText:
            found  = 1
          if found == 1:
            app .prevNums[i]  = app .prevNums[i -1]
            app .Tile[i]  = Image( source = 'atlas://' + app .path + '/' + app .name[ app .prevNums[i] ]) .texture
          i -= 1
        app .prevNums[0]  = app .currentNum + app .offset

        app .Tile[0]  = Image( source = 'atlas://' + app .path + '/' + app .name[ app .prevNums[0] ]) .texture

    self .ids .current .text  = app .currentText
    TileScreen .refreshTiles( self )
    TileScreen .refreshMap( self )


  def scroll( self, off ):   ## < left  tiles  right >
    app .offset += off
    if app .offset < 0:  app .offset += len( app .name )
    if app .offset >= len( app .name ):  app .offset -= len( app .name )

    print('Offset:', app .offset)

    i  = app .tileX
    o  = 0
    while i < app .tileX * app .tileY -1:
      if i + app .offset >= len( app .name ):  o = len( app .name )
      app .Tile[i]  = Image( source = 'atlas://' + app .path + '/' + app .name[ i - o + app .offset ]) .texture
      i += 1

    TileScreen .refreshTiles( self )
    TileScreen .refreshMap( self )


  def horiz( self, xx ):   ## < >
    app .mapX  += xx
    if app .mapX < 0:  app .mapX  = 0

    while len( app .Map ) <  app .mapX * app .mapY * app .bpp:
      app .Map .append( Image( source = 'blank.png' ) .texture )
      app .number .append( 0 )

    while len( app .Map ) >  app .mapX * app .mapY * app .bpp:
      del app .Map[-1]
      del app .number[-1]

    if xx > 0:
      Window .size  = ( int( Window .size[0] + app .mapPxlW ),  Window .size[1] )
    else:
      Window .size  = ( int( Window .size[0] -app .mapPxlW ),  Window .size[1] )

    TileScreen .refreshTiles( self )   ## Kivy is refreshing the tiles
    TileScreen .refreshMap( self )    ## before the window gets resized...


  def vert( self, yy ):   ## v ^
    app .mapY  += yy
    if app .mapY < 0:  app .mapY  = 0

    while len( app .Map ) <  app .mapX * app .mapY * app .bpp:
      app .Map .append( Image( source = 'blank.png' ) .texture )
      app .number .append( 0 )

    while len( app .Map ) >  app .mapX * app .mapY * app .bpp:
      del app .Map[-1]
      del app .number[-1]

    if yy > 0:
      Window .size  = ( Window .size[0],  int( Window .size[1] + app .mapPxlH * 1.4 ))
      app .origin  = ( self .ids .tileSet .pos[0], self .ids .tileSet .pos[1] + app .mapPxlH )
    else:
      Window .size  = ( Window .size[0],  int ( Window .size[1] -app .mapPxlH * 1.4 ))
      app .origin  = ( self .ids .tileSet .pos[0], self .ids .tileSet .pos[1] -app .mapPxlH )

    TileScreen .refreshTiles( self )   ## Kivy is refreshing the tiles
    TileScreen .refreshMap( self )    ## before the window gets resized...


  def layer( self, lay ):   ## enemy, screen, object
    app .layer  = lay * app .mapX * app .mapY
    TileScreen .refreshMap( self )


  def paint( self, toggle ):
    if toggle == 1:        ## Kivy sux again...
      app .ident  = self   ## <--using this to cheat Clock callback.
       ##  Clock .schedule_interval( TileScreen .place,  .05 )
       ## can't pass 'self' along as ( TileScreen .place( self ),  .05 )

       ## so I set  "app .ident = self"   then reference that in the 'place' function.
       ## instead of:        with self .ids .Map .canvas:
       ## I used:             with app .ident .ids .Map .canvas:
      app .painting  = Clock .schedule_interval( TileScreen .place,  .05 )
    else:  app .painting .cancel()


  def place( self ):
    mX  = Window .mouse_pos[0]
    mY  = Window .mouse_pos[1]

    mY -= app .ident .ids .topRow .size[1] + app .ident .ids .bottomRow .size[1]   ## lower buttons

    col  = int( mX / app .mapPxlW )
    row  = int( mY / app .mapPxlH )

    if col >= app .mapX -1:  col  = app .mapX -1
    elif col < 0:  col  = 0

    if row >= app .mapY -1:  row  = app .mapY -1
    elif row < 0:  row  = 0

    i  = col + row * app .mapX
    xx  = app .mapPxlW * col
    yy  = app .mapPxlH * row

    app .number[i]  = app .currentNum
    app .Map[i]  = Image( source = 'atlas://' + app .path + '/' + app .currentText ) .texture

    with app .ident .ids .Map .canvas:
      Rectangle( texture = app .Map[i],  size = app .mapSize,  pos = ( app .mapOrigin[0] + xx,  app .mapOrigin[1] + yy ))


  def generate( self ):
    data  = []

    if app .bpp < 3:
      data .append( 'P2' )
      ext  = '.pgm'   ## Portable GreyMap format
    else:
      data .append( 'P3' )
      ext  = '.ppm'   ## Portable PixMap format

    data .append( '%s %s' % ( app .mapX,  app .mapY ))   ## width, height
    data .append( str( len( app .name )) )   ## how many unique values
    data .append( '##  %s' % app .selected )

    i  = 0
    while i < app .mapX * app .mapY:
      col = 0
      line = ''
      while col < app .mapX:
        if app .bpp < 3:
          line += str( app .number[i] )
        else:  line += '0 ' + str( app .number[i] ) + ' 0'
        col += 1
        if col < app .mapX:  line += ' '
        i += 1
      data .append( line )

    Output  = '\n' .join( data )   ## stringify list

    print( 'Writing\n' )
    with open( 'data/' + app .filename + ext, 'w' ) as fileOut:
      fileOut .write( Output )

    print( 'Written to data/' + app .filename + ext )
    sys .exit()


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class app( App ):
  icon  = 'icon.png'
  title  = 'Kivy TileMapper   ::   by Doyousketch2'

  sm  = ScreenManager( transition = NoTransition() )

  selected  = 'icon.png'
  path  = 'data/icon'
  filename  = 'icon'
  ext  = '.png'

  once  = 0
  layer  = 0
  offset  = 0

  tilePxlW  = 30
  tilePxlH  = 30
  mapPxlW  = 20
  mapPxlH  = 20

  tileX  = 20
  tileY  = 3
  mapX  = 30
  mapY  = 20

  bpp   = 1
  zoom  = 1
  name  = []

  tileSize  = ( tilePxlW * .85,  tilePxlH * .85 )
  outlineSize  = ( tilePxlW,  tilePxlH )
  outlinePos  = ( 0, 0 )

  mapSize  = ( mapPxlW,  mapPxlH )
  mapOrigin  = ( 0, 0 )
  origin  = ( 0, 0 )

  currentNum  = 0
  currentText  = ''
  number  = [0] * mapX * mapY

  ident  = ''
  painting  = ''
  prevNums  = [0] * tileX

   ## default textures to use so kivy doesn't crash.
  Tile  = [Image( source = 'icon.png' ) .texture] * tileX * 3
  Map  = [Image( source = 'blank.png' ) .texture] * mapX * mapY * bpp
   ## will be regenerated once a spritesheet is selected.

  def build( self ):
    self .sm .add_widget( FileScreen( name = 'FileScreen' ))
    self .sm .add_widget( TileScreen( name = 'TileScreen' ))
    return self .sm


##=========================================================
##  main  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
  app() .run()

##  I called it 'app' to remain consistent with .kv conventions.
##  Variables within the class have the same name in .py or .kv file.
##  examples:  'app.selected'  'app.tileSize'

##  You can't do this if you load .kv without Builder,
##  because it'll look for a lowercase version of
##  your main class without the word 'app' appended to the name.

##  normally, "TileMapperApp"  would look for  "tilemapper.kv"
##  but I was using Builder to use ScreenManager anyway.
##  Builder .load_file( './tilemapper.kv' )

##  In this case, the .kv file could have been named anything...

##=========================================================
##  eof  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
