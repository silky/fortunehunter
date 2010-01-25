from Room import Room
from Dungeon import Dungeon
from constants import (
                        THEME_NAME, DOOR_INDEX, DOOR_FLAGS,
                        SPEC_FLAGS, ENEM_INDEX, ITEM_FLAGS,
                        ITEM_INDEX
                      )

from sugar.activity.activity import Activity, ActivityToolbox
from sugar.datastore import datastore
from gettext import gettext as _

from sugar.activity.activity import ActivityToolbox
from sugar.graphics.toolbutton import ToolButton
from sugar.util import unique_id

import gtk
import os
import re

MAX_GRID_WIDTH = 15
MAX_GRID_HEIGHT = 15
MIN_GRID_WIDTH = 2
MIN_GRID_HEIGHT = 2

class BadInputException(Exception):pass

class FortuneMaker(Activity):
    def __init__(self, handle):
        Activity.__init__(self, handle)

        self.dungeon = None
        self.active_room = None

        # INITIALIZE GUI
        ################
        self.set_title('FortuneMaker')

        # Create Toolbox
        self.build_toolbars()
        self.enable_room_icons(False, False)

        self.show_dungeon_selection()

    def build_toolbars(self):
        self.dungeon_buttons = {}
        self.dungeon_bar = gtk.Toolbar()
        self.view_bar = gtk.Toolbar()

        # BUILD CUSTOM TOOLBAR
        self.dungeon_buttons['new'] = ToolButton('add')
        self.dungeon_buttons['new'].set_tooltip(_("New Dungeon"))
        self.dungeon_buttons['new'].connect("clicked", self.view_change_cb, 'new')
        self.dungeon_bar.insert(self.dungeon_buttons['new'], -1)

        self.dungeon_buttons['load'] = ToolButton('fileopen')
        self.dungeon_buttons['load'].set_tooltip(_("Open Dungeon"))
        self.dungeon_buttons['load'].connect("clicked", self.view_change_cb, 'load')
        self.dungeon_bar.insert(self.dungeon_buttons['load'], -1)

        self.dungeon_buttons['save'] = ToolButton('filesave')
        self.dungeon_buttons['save'].set_tooltip( _("Save dungeon file to journal") )
        self.dungeon_buttons['save'].connect("clicked", self.view_change_cb, 'export')
        self.dungeon_bar.insert(self.dungeon_buttons['save'], -1)
        self.dungeon_buttons['save'].set_sensitive( False )

        self.dungeon_buttons['layout'] = ToolButton('view-freeform')
        self.dungeon_buttons['layout'].set_tooltip(_("View Dungeon Layout"))
        self.dungeon_buttons['layout'].connect("clicked", self.view_change_cb, 'layout')
        self.view_bar.insert(self.dungeon_buttons['layout'], -1)
        self.dungeon_buttons['layout'].set_sensitive( False )

        self.dungeon_buttons['room'] = ToolButton('view-box')
        self.dungeon_buttons['room'].set_tooltip(_("View Room Layout"))
        self.dungeon_buttons['room'].connect("clicked", self.view_change_cb, 'room')
        self.view_bar.insert(self.dungeon_buttons['room'], -1)
        self.dungeon_buttons['room'].set_sensitive( False )

        self.toolbox = ActivityToolbox(self)

        # Remove Share Bar
        activity_toolbar = self.toolbox.get_activity_toolbar()
        activity_toolbar.remove(activity_toolbar.share)
        activity_toolbar.share = None

        #Add our custom items to the toolbar
        self.toolbox.add_toolbar(_("Dungeon"), self.dungeon_bar)
        self.toolbox.add_toolbar(_("View"), self.view_bar)

        self.set_toolbox(self.toolbox)
        self.toolbox.show()

    def enable_room_icons(self, dn=True, rm = True):
        self.dungeon_buttons['save'].set_sensitive( dn )
        self.dungeon_buttons['layout'].set_sensitive( dn )
        self.dungeon_buttons['room'].set_sensitive( rm )


    def view_change_cb(self, widget, view=None):
        if view == 'stats':
            self.view_dungeon_stats()
        elif view == 'layout':
            self.view_dungeon_grid()
        elif view == 'room':
            self.view_room()
        elif view == 'export':
            self.export_view()
        elif view == 'new':
            ##TODO CONFIRM
            self.set_create_dungeon_settings()
        elif view == 'load':
            self.show_dungeon_selection()

    def list_fh_files(self):
        ds_objects, num_objects = datastore.find({'FortuneMaker_VERSION':'1'})
        file_list = []
        for i in xrange(0, num_objects, 1):
            file_list.append( ds_objects[i] )
        return file_list

    def export_view(self):
        data = self.dungeon.export()

        textbuffer = gtk.Label()
        filename = self.dungeon.name

        self._write_textfile( filename, data)

        textbuffer.set_text( "File Saved to %s"%(filename) )

        self.set_gui_view( textbuffer, True )



    #### Method: _write_textfile, which creates a simple text file
    # with filetext as the data put in the file.
    # @Returns: a DSObject representing the file in the datastore.
    def _write_textfile(self, filename, filetext=''):
        ds_objects, num_objects = datastore.find({'title':filename,'FortuneMaker_VERSION':'1'})

        if num_objects == 0:
            # Create a datastore object
            file_dsobject = datastore.create()
            file_dsobject.metadata['FM_UID'] = unique_id()
        else:
            file_dsobject = ds_objects[0]

        # Write any metadata (here we specifically set the title of the file and
        # specify that this is a plain text file).
        file_dsobject.metadata['title'] = filename
        file_dsobject.metadata['mime_type'] = 'text/fm_map'
        file_dsobject.metadata['FortuneMaker_VERSION'] = '1'

        #Write the actual file to the data directory of this activity's root.
        file_path = os.path.join(self.get_activity_root(), 'instance', filename)
        f = open(file_path, 'w')
        try:
            f.write(filetext)
        finally:
            f.close()

        #Set the file_path in the datastore.
        file_dsobject.set_file_path(file_path)

        datastore.write(file_dsobject)
        return file_dsobject


    def set_gui_view(self,  view, buttons=False):
        if buttons:
            box = gtk.VBox()
            box.pack_start( self.get_button_bar(), False )
            box.pack_start(view)
            self.set_canvas( box )
        else:
            self.set_canvas( view )
        self.show_all()

    def get_button_bar(self):
        button_tabs = gtk.HBox()

        stats = gtk.Button( _("Dungeon Summary") )
        stats.set_alignment(0,.5)
        stats.connect( 'clicked', self.view_change_cb, 'stats')
        button_tabs.pack_start( stats, False )

        return button_tabs

    def show_dungeon_selection(self):
        window_container = gtk.VBox()

        button = gtk.Button( _("Create New Dungeon") )
        button.connect("clicked", self.set_create_dungeon_settings, None)
        window_container.pack_start( button, False )

        frame = gtk.Frame( _("Load Dungeon") )
        file_container = gtk.VBox()

        ##LOAD FILE LIST HERE
        file_list = self.list_fh_files()

        for dfile in file_list:
            row = gtk.HBox()
            label = gtk.Label(dfile.metadata['title'])
            row.pack_start( label, False )

            button = gtk.Button(_("Load"))
            button.connect( 'clicked', self.load_dungeon, dfile )
            row.pack_end(button, False)

            file_container.pack_start( row, False )

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport( file_container )

        frame.add( scroll )
        window_container.pack_start( frame )

        room_center = gtk.HBox()
        room_center.pack_start( gtk.Label() )
        room_center.pack_start( window_container )
        room_center.pack_start( gtk.Label() )

        self.set_gui_view( room_center )


    def set_create_dungeon_settings(self, trash=None, trash2=None):
        window_container = gtk.VBox()

        ## Dungeon Properties
        ###############
        frame = gtk.Frame(_("Dungeon Properties"))

        container =  gtk.VBox()

        # Name
        row = gtk.HBox()
        label = gtk.Label(_("Name:"))
        label.set_alignment( 0, 0.5)
        row.pack_start( label )
        name = gtk.Entry()
        row.pack_end( name )
        container.pack_start( row, False )

        # Theme
        row = gtk.HBox()
        label = gtk.Label(_("Theme:"))
        label.set_alignment( 0, 0.5)
        row.pack_start( label )
        theme = gtk.combo_box_new_text()
        for option in THEME_NAME:
            theme.append_text( option )
        theme.set_active( 0 )
        row.pack_end( theme )
        container.pack_start( row, False )

        # Next Dungeon
        row = gtk.HBox()
        label = gtk.Label(_("Next Dungeon:"))
        label.set_alignment( 0, .5)
        row.pack_start( label )

        next_dungeon = gtk.combo_box_new_text()

        file_list = self.list_fh_files()
        file_list_map = {}
        file_list_map["0"] = _("None")
        next_dungeon.append_text( file_list_map["0"] )
        next_dungeon.set_active(0)

        for dfile in file_list:
            file_list_map[dfile.metadata['FM_UID']] = dfile.metadata['title']
            next_dungeon.append_text( dfile.metadata['title'] )

        row.pack_start(next_dungeon)
        container.pack_start( row, False )

        frame.add( container )
        window_container.pack_start( frame, False )

        ## Dungeon Size
        ###############
        frame = gtk.Frame(_("Dungeon Size"))

        # Width
        widthADJ = gtk.Adjustment(MIN_GRID_WIDTH, MIN_GRID_WIDTH, MAX_GRID_WIDTH, 1.0, 5.0, 0.0)
        widthspin = gtk.SpinButton(widthADJ, 0, 0)
        container = gtk.VBox()
        row = gtk.HBox()
        label = gtk.Label(_("Width:") )
        label.set_alignment( 0, 0.5)
        row.pack_start( label)
        row.pack_end( widthspin )
        container.pack_start( row, False )

        # Height
        heightADJ = gtk.Adjustment(MIN_GRID_HEIGHT, MIN_GRID_HEIGHT, MAX_GRID_HEIGHT, 1.0, 5.0, 0.0)
        heightspin = gtk.SpinButton(heightADJ, 0, 0)
        row = gtk.HBox()
        label = gtk.Label(_("Height:") )
        label.set_alignment( 0, 0.5)
        row.pack_start( label )
        row.pack_end( heightspin )
        container.pack_start( row, False )

        frame.add( container )
        window_container.pack_start( frame, False )

        ## Make Dungeon Button
        make_dungeon = gtk.Button(_("Create Dungeon"))
        make_dungeon.connect("clicked", self.create_dungeon_cb, {'name':name,
                                'theme':theme,'width':widthspin, 'height':heightspin,
                                'next_dungeon':next_dungeon, 'd_list':file_list_map})

        window_container.pack_start( make_dungeon, False )

        room_center = gtk.HBox()
        room_center.pack_start( gtk.Label() )
        room_center.pack_start( window_container )
        room_center.pack_start( gtk.Label() )

        self.set_gui_view( room_center )

    def load_dungeon(self, widget, file_data):
        name = file_data.metadata['title']
        dgnFile=open(file_data.get_file_path(),'r')
        self.do_load( name, dgnFile)

    def do_load( self, name, dgnFile ):
        grab = 0
        room_str = []
        for line in dgnFile:
            if grab == 0:
                match = re.match('(\d+)x(\d+)',line)
                if match:
                    x = int(match.group(1))
                    y = int(match.group(2))
                    grab = 1
                else:
                    raise BadInputException()

            elif grab == 1:
                theme = int(line)
                grab = 2
            elif grab == 2:
                next = line
                grab = 3
            elif grab == 3:
                room_str.append(line)

        self.dungeon = Dungeon( name, theme, next, x, y, room_str)
        self.enable_room_icons(True, False)
        self.view_dungeon_stats()


    def create_dungeon_cb(self, widget, data):
        name = data['name'].get_text()
        theme = data['theme'].get_active()  #.get_active_text()
        next = find_key( data['d_list'], data['next_dungeon'].get_active_text())
        width = data['width'].get_value_as_int()
        height = data['height'].get_value_as_int()

        self.dungeon = Dungeon( name, theme, next, width, height )
        self.enable_room_icons(True, False)
        self.view_dungeon_stats()

    def view_dungeon_stats(self):
        dungeon_stats = gtk.HBox()
        dungeon_stats.pack_start(gtk.Label("Dungeon (%s) Statistics to be implemented"%self.dungeon.name))
        self.set_gui_view( dungeon_stats, True )

    def view_dungeon_grid(self):
        room_array = self.dungeon.get_room_array()
        box = gtk.VBox()
        for row_array in room_array:
            row = gtk.HBox()
            box.pack_start( row, False )
            for room in row_array:
                room_gui = room.render_room()
                room_gui.connect('clicked', self.set_active_room, room)
                row.pack_start( room_gui, False )

        scroll = gtk.ScrolledWindow()
        scroll.add_with_viewport( box )

        self.set_gui_view( scroll, True )

    def view_room(self):
        self.enable_room_icons(True, True)
        lbl_size = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        input_size =  gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)

        #TODO CHECK IF ACTIVE ROOM SET

        room_holder = gtk.VBox()

        ## Room Doors
        #############
        frame = gtk.Frame(_("Room Doors"))
        frame.set_label_align(0.5, 0.5)
        holder = gtk.VBox()

        doors = {}

        door_flags = [ _("None") ]
        door_flags.extend( DOOR_FLAGS.values() )

        for door_key in DOOR_INDEX:
            row = gtk.HBox()
            label = gtk.Label(DOOR_INDEX[door_key])
            label.set_alignment( 0, 0.5 )
            lbl_size.add_widget(label)
            row.pack_start( label, False )

            doors[door_key] = gtk.combo_box_new_text()
            input_size.add_widget( doors[door_key] )

            for value in door_flags:
                doors[door_key].append_text( value )

            door_flag = self.active_room.get_door( door_key )
            if door_flag != '0':
                doors[door_key].set_active( door_flags.index( DOOR_FLAGS[door_flag] ) )
            else:
                doors[door_key].set_active( 0 )

            row.pack_end( doors[door_key], False )
            holder.pack_start( row, False )

        frame.add( holder )
        room_holder.pack_start( frame, True )

        ##Room Flags
        ############
        frame = gtk.Frame(_("Room Properties"))
        frame.set_label_align(0.5, 0.5)
        holder = gtk.VBox()

        row = gtk.HBox()
        label = gtk.Label(_("Room Flag"))
        label.set_alignment( 0, 0.5 )
        lbl_size.add_widget(label)
        row.pack_start( label, False )

        flag_sel = gtk.combo_box_new_text()
        spec_flags = SPEC_FLAGS.values()
        input_size.add_widget( flag_sel )
        for flag in spec_flags:
            flag_sel.append_text( flag )

        flag = self.active_room.get_room_flag()
        flag_sel.set_active( spec_flags.index( SPEC_FLAGS[flag] ) )

        row.pack_end( flag_sel, False )
        holder.pack_start( row, True)

        frame.add( holder )
        room_holder.pack_start( frame, True )

        ## Room Enemies
        ###############
        frame = gtk.Frame(_("Room Enemies"))
        frame.set_label_align(0.5, 0.5)
        holder = gtk.VBox()

        enem = []

        for i in range(0,4):
            enem.append( gtk.combo_box_new_text() )

            row = gtk.HBox()
            label = gtk.Label("%s (%d)" % (_("Enemy"), i))
            label.set_alignment( 0, 0.5 )
            lbl_size.add_widget( label )

            row.pack_start(label, False)
            em_list = ENEM_INDEX.values()
            for em in em_list:
                enem[i].append_text( em )

            enem[i].set_active( em_list.index(ENEM_INDEX[self.active_room.get_enemy( i )] ) )
            input_size.add_widget( enem[i] )
            row.pack_end( enem[i], False )

            holder.pack_start( row, False )

        frame.add( holder )
        room_holder.pack_start( frame, True )

        ## Room Items
        #############
        frame = gtk.Frame(_("Room Item"))
        frame.set_label_align(0.5, 0.5)
        holder = gtk.VBox()

        item_arr = []

        item_list = ITEM_INDEX.values()
        item_flags = ITEM_FLAGS.values()

        for i in range(0,4):
            itemType = gtk.combo_box_new_text()
            itemFlag= gtk.combo_box_new_text()

            for item in item_list:
                itemType.append_text( item )

            #TODO: ADD DEFUALT Flag

            for item in item_flags:
                itemFlag.append_text( item )

            #TODO: ADD DEFUALT Flag

            item_arr.append( [itemType, itemFlag] )

            row = gtk.HBox()
            row.pack_start( itemType, False )
            row.pack_start( itemFlag, False )

            holder.pack_start( row, False )

        frame.add( holder )
        room_holder.pack_start( frame, True )

        ## Save Button
        ##############
        save = gtk.Button(_('Save'))
        save.connect('clicked', self.save_room, {'doors':doors,'flag':flag_sel,'enemy':enem,'items':item_arr})

        room_holder.pack_start( save, True )

        room_center = gtk.HBox()
        room_center.pack_start( gtk.Label() )
        room_center.pack_start( room_holder )
        room_center.pack_start( gtk.Label() )

        self.set_gui_view( room_center, True )

    def save_room(self, widgit, data):
        for key in data['doors']:
            value = find_key( DOOR_FLAGS, data['doors'][key].get_active_text())
            if value:
                self.active_room.add_door( key, value )
            else:
                self.active_room.remove_door( key )

        self.active_room.set_room_flag( find_key(SPEC_FLAGS, data['flag'].get_active_text() ) )

        i = 0
        for enemy_select in data['enemy']:
            en_id= find_key( ENEM_INDEX, enemy_select.get_active_text() )
            self.active_room.set_enemy( i, en_id )
            i = i + 1

        #TODO ITEMS

        self.dungeon.update_room( self.active_room )
        self.view_dungeon_grid()

    def set_active_room(self, widgit, room):
        self.active_room  = room
        self.view_room()

    def read_file(self, file_path):
        # If no title, not valid save, don't continue loading file
        if self.metadata.has_key( 'dungeon_title' ):
            name = self.metadata['dungeon_title']
            dgnFile=open(file_path,'r')
            self.do_load( name, dgnFile )

    def write_file(self, file_path):
        if self.dungeon:
            f = open( file_path, 'w' )
            f.write( self.dungeon.export() )
            f.close()
            self.metadata['dungeon_title'] = self.dungeon.name
        else:
            # Basically touch file to prevent it from keep error
            open( file_path, 'w' ).close()

if __name__ == "__main__":

    aroom = Room()

    aroom.add_door('N', 'u')
    aroom.add_door('E', 'p')

    aroom.set_enemy(1,'2')
    aroom.set_enemy(3,'4')

    aroom.set_room_flag('P')
    #ADD SET ITEM WHEN CODED

    print aroom.room_to_string()

def find_key(dic, val):
    """return the key of dictionary dic given the value"""
    try:
        return [k for k, v in dic.iteritems() if v == val][0]
    except:
        return False
