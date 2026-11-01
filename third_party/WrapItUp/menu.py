import nuke
import WrapItUp

# ark_nuke: top-level Nuke menubar "Extra" suppressed — Ark menu provides WrapItUp.
# Set True to restore Extra/Wrap It Up on the main menubar.
_REGISTER_EXTRA_MENU = False
if _REGISTER_EXTRA_MENU:
    nuke.menu('Nuke').addCommand('Extra/Wrap It Up', "WrapItUp.WrapItUp()")
