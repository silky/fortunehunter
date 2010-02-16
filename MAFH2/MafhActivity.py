from GameEngine import GameEngine
from MafhGameMenu import GameMenuHolder

from constants import MENU_PATH, FMC_PATH, TOUR_PATH

from Comic import Comic
from Profile import Profile
from MafhGameManager import MafhGameManager

ge = GameEngine()

def start_game():
    ge.add_object('manager', MafhGameManager() )

def menu_screen():
    ge.add_object('menu', GameMenuHolder( menu_called, MENU_PATH + "mafh_splash.gif"))
    ge.get_object('menu').show_menu('title')

def menu_called(id, menu):
    if id == 'new':
        #ge.get_object('menu').remove_from_engine()
        menu.remove_from_engine()
        ge.remove_object('menu')

        if not ge.has_object('profile'):
            ge.add_object( 'profile',
                Profile( name_entry_cb=lambda: ge.add_object('comic', Comic(FMC_PATH+"FMC1/",None,start_game)) ) )

    elif id == 'controls':
        menu.remove_from_engine()
        ge.remove_object('menu')
        ge.add_object('comic', Comic(TOUR_PATH+"setup/",None,menu_screen))
    else:
        print "MENU CALLED %s" % id

# Build menu and add to engine.  Then show menu
menu_screen()

# Draw and start event loop
ge.draw()
ge.start_event_loop()