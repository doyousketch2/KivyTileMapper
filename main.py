#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##=========================================================
##  tilemapper.py                               28 Apr 2017
##
##  Generates a Kivy app from spritesheet
##
##  Eli Leigh Innis
##  Twitter :  @ Doyousketch2
##  Email :  Doyousketch2 @ yahoo.com
##
##  GNU GPLv3                 gnu.org/licenses/gpl-3.0.html
##=========================================================
##  required  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##  you'll need kivy:
##  (debian)
##        sudo pip3 install kivy
##  (linux)
##        sudo python3 -m pip install kivy
##  (mac)
##        sudo easy_install pip
##        python -m pip install kivy
##  (win)
##        py -m pip install kivy
##=========================================================
##  libs  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import  os
import  sys

from  kivy .app           import  App               ##  GUI
from  kivy .graphics       import *
from  kivy .lang            import  Builder
from  kivy .uix .image       import  Image
from  kivy .uix .screenmanager  import  ( ScreenManager,
                                      NoTransition, Screen )
from  kivy .graphics .texture  import  Texture
from  kivy .core .window     import  Window
from  kivy .clock           import  Clock

##=========================================================
##  config  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

WIDTH  = 800
HEIGHT  = 600

##=========================================================
##  script  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Window .size  = ( WIDTH, HEIGHT )

##  Kivy sux, need 'Builder' when using ScreenManager...
Builder .load_file('./tilemapper.kv')


class FileScreen(Screen):

  def select(self, *args):
    self .selection  = args[1][0]
    try:
      app .selected  = self .selection
      self .label .text  = app .selected
    except:  pass


  def choice(self):

    app .path,  app .ext  = os .path .splitext( app .selected )

    if '/' in app .path:  ##  Unix, Linux, Android, Mac OSX, iOS
      app .filename  = app .path .split('/')[-1]
    else:  ##  the other OS
      app .filename  = app .path .split('\\')[-1]
    print(app .filename)

    with open('./data/' + app .filename + '.atlas') as JSONfile:  ##  .atlas is a JSON file

      JSONfile .readline()  ##  skip the first line, 'cuz it's just a curly bracket {

                                                          ##    "spritesheet.png": {
      spritesheet  = JSONfile .readline() .split('"')[1]  ##  spritesheet.png

                                            ##    "Name":  [ xpos, ypos,  w, h],\n
      line = JSONfile .readline() .strip()  ##  "Name":  [ xpos, ypos,  w, h],

      app .name .append(line .split('"')[1])  ##  Name

      values  = line .split('[')[1] .split(']')[0] .split(',')  ##  xpos, ypos,  w, h

      app .gridW  = int(values[2] .strip() )  ##  w     grid tile width
      app .gridH  = int(values[3] .strip() )  ##  h     "    "    height

      for line in JSONfile:
        if line .strip() .startswith('"'):  ##  skip closing brackets }

          app .name .append(line .split('"')[1])  ##  B2

    i = 0
    while i < len(app .tile):
      app .tile[i]  = Image(source = 'atlas://' + app .path + '/' + app .name[i] ) .texture
      i += 1

    self .manager .switch_to( TileScreen() )


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TileScreen(Screen):

  def refreshTiles(self):
    off  = app .offset
    self .ids .tileSet .canvas .clear()

    i  = 0
    while i < app .tileX * app .tileY:
      app .tile[i]  = Image(source = 'atlas://' + app .path + '/' + app .name[off] ) .texture

      col  = app .tileW * (i % 20)
      row  = app .tileH * (2 - int( i / 20))
      ##  subtract from 2 to reverse bottom-up order 0,1,2 to top-down 2,1,0

      tilePos  = (self .ids .tileSet .pos[0] + col,  self .ids .tileSet .pos[1] + row )
      outlinePos  = (self .ids .tileSet .pos[0] + col - self .ids .tileSet .size[0] / 200,
                     self .ids .tileSet .pos[1] + row - self .ids .tileSet .size[1] / 50)

      if i + app .offset >= len(app .name):
        currentName  = app .name[i + app .offset - len(app .name)]
      else:
        currentName  = app .name[i + app .offset]

      with self .ids .tileSet .canvas:
        if app .currentTile == currentName:
          Color(1, 0.1, 0.1,  1)  ##  red outline
          Rectangle(size = app .outlineSize,  pos = outlinePos)
          Color(1, 1, 1,  1)  ##  change color back to white, or tiles go wonky
        if i < app .tileX * 2:
          Rectangle(texture = app .tile[i],  size = app .tileSize,  pos = tilePos)
        else:
          Rectangle(texture = app .preTile[i],  size = app .tileSize,  pos = tilePos)

      off += 1
      if off == len(app .name):  off  = 0
      i += 1


  def refreshGrid(self):
    self .ids .grid .canvas .clear()

    i  = 0
    while i < app .gridX * app .gridY:
      col  = app .gridW * (i % app .gridX)
      row  = app .gridH * int(i / app .gridX)

      gridPos  = (app .gridPos[0] + col,  app .gridPos[1] + row )

      with self .ids .tileSet .canvas:
        Rectangle(texture = app .grid[i],  size = app .gridSize,  pos = gridPos)

      i += 1


  def layer(self, lay):
    app .layer  = lay * app .gridX * app .gridY
    TileScreen .sizes(self)
    TileScreen .refreshGrid(self)


  def hover(self, toggle):
    if toggle == 1:       ##  Kivy sux again...
      app .ident  = self  ##  <-- using this to cheat Clock callback.
      ##   Clock .schedule_interval(TileScreen .place,  0.05)
      ##  can't pass 'self' along as (TileScreen .place(self),  0.05)
      ##  so I set  app.ident = self   then reference that instead,
      ##  in 'place' function:     with app .ident .ids .grid .canvas:
      ##  instead of:              with self .ids .grid .canvas:
      app .hoverEvent  = Clock .schedule_interval(TileScreen .place,  0.05)
    else:  app .hoverEvent .cancel()


  def place(self):
    mX  = Window .mouse_pos[0]
    mY  = Window .mouse_pos[1]

    mY -= app .buttonHeight  ##  subtract lower buttons

    col  = int(mX / app .gridW)
    row  = int(mY / app .gridH)

    if col >= app .gridX - 1:  col  = app .gridX - 1
    elif col < 0:  col  = 0

    if row >= app .gridY - 1:  row  = app .gridY - 1
    elif row < 0:  row  = 0

    i  = col + row * app .gridX
    xx  = app .gridW * col
    yy  = app .gridH * row

    app .number[i]  = app .currentNum
    app .grid[i]  = Image(source = 'atlas://' + app .path + '/' + app .currentTile ) .texture

    with app .ident .ids .grid .canvas:
      Rectangle(texture = app .grid[i],  size = app .gridSize,  pos = (app .gridPos[0] + xx,  app .gridPos[1] + yy ) )


  def sizes(self):  ##  Note:  should be called on window resize

    app .leftScroll  = self .ids .scrollLeft .size[0]
    app .labelHeight  = self .ids .current .size[1]

    app .gridHeight  = self .ids .grid .size[1]
    app .buttonHeight  = self .ids .topRow .size[1] + self .ids .bottomRow .size[1]

    app .tileW  = self .ids .tileSet .size[0] / 20
    app .tileH  = self .ids .tileSet .size[1] / 3

    app .gridW  = self .ids .grid .size[0] / app .gridX
    app .gridH  = self .ids .grid .size[1] / app .gridY

    app .tileSize  = (app .tileW * 0.85,  app .tileH * 0.85)
    app .gridSize  = (app .gridW,  app .gridH)

    app .gridPos  = self .ids .grid .pos
    app .outlineSize  = (app .tileW,  app .tileH)


  def select(self):
    TileScreen .sizes(self)

    mX  = Window .mouse_pos[0]
    mY  = Window .mouse_pos[1]

    mX -= app .leftScroll  ##  subtract left scroll button

    mY -= app .labelHeight
    mY -= app .gridHeight
    mY -= app .buttonHeight

    col  = int(mX / app .tileW)
    row  = 2 - int(mY / app .tileH)
    ##  subract from 2 to reverse bottom-up order 0,1,2 to top-down 2,1,0

    i  = col + row * 20 + app .offset
    app .currentNum = i

    if row < 2:  app .currentTile  = app .name[i]
    else:  app .currentTile  = app .name[col]

    self .ids .current .text  = app .currentTile

    if Image(source = 'atlas://' + app .path + '/' + app .currentTile ) .texture not in app .preTile:

      i = app .tileX - 1
      while i > 0:
        app .preTile[i]  = app .preTile[i - 1]
        i -= 1

      app .preTile[0]  = Image(source = 'atlas://' + app .path + '/' + app .currentTile ) .texture

    TileScreen .refreshTiles(self)
    TileScreen .refreshGrid(self)


  def scroll(self, off):
    TileScreen .sizes(self)

    app .offset  += off
    if app .offset < 0:  app .offset += len(app .name)
    if app .offset >= len(app .name):  app .offset -= len(app .name)

    TileScreen .refreshTiles(self)
    TileScreen .refreshGrid(self)


  def zoom(self, factor):
    app .zoom += factor
    if app .zoom < 0.2:  app .zoom  = 0.2
    elif app .zoom > 3:  app .zoom  = 3


  def horiz(self, xx):
    app .gridX  += xx
    if app .gridX < 0:  app .gridX  = 0


  def vert(self, yy):
    app .gridY  -= yy
    if app .gridY < 0:  app .gridY  = 0


  def generate(self):
    data  = []

    if app .bpp < 3:
      data .append('P2')
      ext  = '.pgm'  ##  Portable GreyMap format
    else:
      data .append('P3')
      ext  = '.ppm'  ##  Portable PixMap format

    data .append('%s %s' % (app .gridX, app .gridY))  ##  width, height
    data .append(str(len(app .name) ))  ##  how many unique values
    data .append('##  %s' % app .selected)

    i  = 0
    while i < app .gridX * app .gridY:
      col = 0
      line = ''
      while col < app .gridX:
        if app .bpp < 3:
          line += str(app .number[i])
        else:  line += '0 ' + str(app .number[i]) + ' 0'
        col += 1
        if col < app .gridX:  line += ' '
        i += 1
      data .append(line)

    Output  = '\n' .join(data)  ##  stringify list

    print('Writing\n')
    with open('data/' + app .filename + ext, 'w') as fileOut:
      fileOut .write(Output)

    print('Written to data/' + app .filename + ext)
    sys .exit()


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class app(App):
  icon  = 'icon.png'
  title  = "Kivy Tilemapper   ::   by Doyousketch2"

  sm  = ScreenManager( transition = NoTransition() )

  selected  = 'icon.png'
  path  = 'data/icon'
  filename  = 'icon'
  ext  = '.png'

  layer  = 0
  offset  = 0
  padding  = 6

  tileW  = 30
  tileH  = 30
  gridW  = 20
  gridH  = 20

  tileX  = 20
  tileY  = 3
  gridX  = 30
  gridY  = 20

  bpp   = 1
  name  = []

  tileSize  = (tileW * 0.85,  tileH * 0.85)
  outlineSize  = (tileW,  tileH)
  outlinePos  = (0, 0)

  gridSize  = (gridW,  gridH)
  gridPos  = (0, 0)

  currentNum  = 0
  currentTile  = ''
  number  = [0] * gridX * gridY

  labelHeight  = 0
  gridHeight   = 0
  buttonHeight = 0

  hoverEvent  = ''
  ident  = ''

  ##  default textures to use so kivy doesn't crash.
  tile  = [Image(source = 'icon.png') .texture] * tileX * 3
  preTile  = [Image(source = 'icon.png') .texture] * tileX * 3
  grid  = [Image(source = 'blank.png' ) .texture] * gridX * gridY * bpp
  ##  will be regenerated once a spritesheet is selected.

  def build(self):
    self .sm .add_widget( FileScreen( name = 'FileScreen') )
    self .sm .add_widget( TileScreen( name = 'TileScreen') )
    return self .sm


##=========================================================
##  main  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
  app() .run()

##  I called it 'app' to remain consistant with .kv conventions.
##  Variables within the class have the same name in .py or .kv file.
##  examples:  app.selected  app.tileSize

##  You can't do this if you load .kv without Builder,
##  because it'll look for a lowercase version of
##  your main class without the word 'app' appended to the name.

##  normally, TileMapperApp would look for tilemapper.kv
##  but I was using Builder to use ScreenManager anyway...

##  Builder .load_file('./tilemapper.kv')
##  in this case, the .kv file could have been named anything.

##=========================================================
##  eof  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

