from constants import (
    DOOR_ORDER, DOOR_INDEX, DOOR_FLAGS, SPEC_FLAGS,
    ENEM_INDEX, ITEM_INDEX, ITEM_FLAGS
    )

import gtk

class Room:
    def __init__(self, x = -1, y = -1):
        self._x = x
        self._y = y
        self.doors = {}
        self.enemy = []
        self.item = []

        for index in DOOR_INDEX:
            self.doors[index] = ['0', '0']

        self.special = '0'

        for index in range(0,4):
            self.enemy.append( '0' )

        for index in range(0,4):
            self.item.append( ['0', '0'] )

    def add_door(self, door, flag):
        if door in DOOR_INDEX and flag in DOOR_FLAGS:
            self.doors[door] = [door, flag]
        else:
            print "INVALID DOOR AND/OR FLAG"

    def remove_door(self, door):
        if door in DOOR_INDEX:
            self.doors[door] = ['0', '0']
        else:
            print "INVALID DOOR"

    def get_door( self, door):
        if door in DOOR_INDEX:
            return self.doors[door][1]

    def set_room_flag(self, flag):
        if flag in SPEC_FLAGS:
            self.special = flag
        else:
            print "INVALID FLAG"

    def get_room_flag( self ):
        return self.special

    def set_enemy( self, pos, enemy ):
        if pos >= 0 and pos <=3 and enemy in ENEM_INDEX:
            self.enemy[pos] = enemy
        else:
            print "INVALID ENEMY POS OR ID"

    def get_enemy(self, pos):
        if pos >=0 and pos <=3:
            return self.enemy[pos]

    def set_item(self, pos, id, flag):
        if pos >= 0 and pos <=3 and id in ITEM_INDEX and flag in ITEM_FLAGS:
            self.item[ pos ] = [id, flag]
        else:
            print "INVALID POS OR ID OR FLAG"

    def room_to_string(self):
        str = ""
        for index in DOOR_ORDER:
            str += self.doors[index][0] + self.doors[index][1]

        str += self.special

        for enemy in self.enemy:
            str += enemy

        for item in self.item:
            str += item[0] + item[1]

        return str

    def render_room(self):
        but = gtk.Button("(%d, %d)" %(self._x, self._y))
        but.set_size_request(100, 100)
        return but
