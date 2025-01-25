import uvicore
from ohmyi3 import util
from uvicore.typing import Dict
from uvicore.configuration import env
from uvicore.support.dumper import dump, dd
from ohmyi3.util import set, gather, path, plugin

# Ohmyi3 user configuration.
#
# This config is what drives the i3ctl generator.
# All variables inside config() will be available to the jinja2 templating engine
# and may be used in your config.d/* i3 configs for dynamic conditions.
# Use the before_generate() and after_generate() hooks to fire off plugins/*
# to control the rest of your system (set wallpaper, alacritty themes, polybar...)
# From here on out, the power is in your hands.  Automation is now limitless!

def config():
    """Ohmyi3 variables for configuring and templating i3"""

    # Hostname and user from system
    host = util.hostname()
    user = util.loggedinuser()


    # Paths to all relevant locations
    # If you need to change the ohmyi3 path, use the
    # environment variable OHMYI3_PATH (default ~/.config/ohmyi3)
    ohmyi3_path = uvicore.config('ohmyi3.config_path')
    paths = set({
        'ohmyi3': path(ohmyi3_path),
        'ohmyi3_configd': path([ohmyi3_path, 'config.d']),
        'ohmyi3_themes': path([ohmyi3_path, 'themes']),
        'i3': path('~/.config/i3'),
        'i3status': path('~/.config/i3status'),
        'alacritty': path('~/.config/alacritty'),
        'polybar': path('~/.config/polybar'),
    })

    # Unix OS Variant
    os = set('manjaro', host, {
        'p14s': 'lmde',
    })


    # Main network interface
    net_interface = set('enp11s0', host, {
        'p15': 'enp11s0',
        'p53': 'wlp0s20f3',
        'deajaro': 'wlp2s0',
    })


    # Has battery (laptop?)
    has_battery = set(True, host, {
        'sunjaro': False,
        'p53': True,
        'p15': True,
        'p14s': True,
    })
    battery_device = set('BAT0')


    # Backlinght
    backlight_device = set('intel_backlight')


    # Desktop Environment (kde, xfce, i3, cinnamon, mate, gnome)
    # I like to run i3 inside kde and xfce etc...  If runing under these DE's
    # I need to tweak the configs (no screen lock, different autostarts etc...)
    desktop = set('i3', host, {
        'sunjaro': 'kde',
        'p53': 'i3',
        'p15': 'i3',
        #'p14s': 'cinnamon',
    })


    # Main desktop tools (kde, xfce...)
    # Not the same as desktop, which is the running Desktop Environment
    desktop_tools = set('kde', host, {
        'deajaro': 'xfce'
    })


    # Using i3 capable of gaps
    i3_gaps = set(True, host, {
        'p14s': False
    })


    # Restart i3 command
    i3_restart = set('~/.files/scripts/i3ctl-dev generate && i3-msg restart', host, {
        'deajaro': 'i3ctl generate && i3-msg restart',
        'p14s': '/home/mreschke/.pyenv/shims/i3ctl generate && i3-msg restart',
    })


    # Wallpaper base
    wallpaper_base = set('~/Wallpaper', host, {
        'sunjaro': '~/Pictures/Wallpaper',
        'p53': '~/Pictures/Wallpaper',
    })


    # Current theme (amber, archlinux, manjaro, pink)
    theme = set('manjaro', host, {
        'sunjaro': 'manjaro',
        'p53': 'manjaro',
        'p15': 'amber',
        'p14s': 'manjaro',
    })


    # Extra theme details
    # Wallpaper is an OVERRIDE, else defaults to the themes folder/background.[jpg|png]
    themes = set({
        'amber': {
            'color': '#EF5B1A',
            'archey3': 'yellow',
            #'wallpaper': 'Abstract/cracked_orange.jpg',
            #'wallpaper': 'Manjaro/antelope-canyon-984055.jpg',
            #'wallpaper': 'Scenes/digital_sunset.jpg',
            #'wallpaper': 'LinuxMint/linuxmint-vera/mpiwnicki_red_dusk.jpg',
            #'wallpaper': 'LinuxMint/linuxmint-vanessa/navi_india.jpg',
            #'wallpaper': 'LinuxMint/linuxmint-una/nwatson_eclipse.jpg',
            #'wallpaper': 'LinuxMint/linuxmint-vera/navi_india.jpg',
            #'wallpaper': 'LinuxMint/linuxmint-ulyssa/tangerine_nanpu.jpg',
            #'wallpaper': 'Manjaro/sky-3189347.jpg',
        },
        'archlinux': {
            'color': '#1793D1',
            'archey3': 'blue',
            #'wallpaper': 'Archlinux/349880.jpg',
            'wallpaper': 'De/budgie.jpg',

        },
        'manjaro': {
            'color': '#106E5C',
            'archey3': 'green',
            #'wallpaper': 'Manjaro/illyria-default-lockscreen-nobrand.jpg',
            #'wallpaper': 'Manjaro/wpM_orbit2_textured.jpg'
            'wallpaper': 'De/deepin.jpg',

        },
        'pink': {
            'color': '#b41474',
            'archey3': 'magenta',
            #'wallpaper': 'Abstract/artistic_colors2.jpg',
            #'wallpaper': 'Landscape/backlit-chiemsee-dawn-1363876.jpg',
            #`'wallpaper': 'Manjaro/DigitalMilkyway.png',
            #'wallpaper': 'LinuxMint/linuxmint-una/eeselioglu_istanbul.jpg',
            #'wallpaper': 'Abstract/neon_huawei.jpg',
            #'wallpaper': 'De/budgie.jpg',
            'wallpaper': 'De/deepin.jpg',
        },
    },
        host, {
            #'p15': {'manjaro.wallpaper': 'Manjaro/wpM_orbit2_textured.jpg'}
            #'p53': {'manjaro.wallpaper': 'De/deepin.jpg!!!'}
        }
    )


    # Polybar
    # Specific to the custom qpanel theme made from this https://github.com/adi1090x/polybar-themes
    polybar = set({
        'enabled': True,
        # blocks|colorblocks|cuts|docky|forest|grayblocks|hack|material
        # panels|pwidgets|qpanels|shades|shapes
        'theme': 'qpanels',
        # budgie|deepin|elight|edark|gnomw|klight|kdark
        # liri|mint|ugnome|unity|xubuntu|zorin
        'subtheme': 'deepin'
    }, host, {
        'p14s': {'enabled': False},
    })


    # Rofi
    rofi = set({
        'launcher': f'~/.config/polybar/{polybar.theme}/scripts/launcher.sh --{polybar.subtheme}',
        'powermenu': f'~/.config/polybar/{polybar.theme}/scripts/powermenu.sh --{polybar.subtheme}',
    }, host, {
        'p14s': {'launcher': 'rofi -show drun'}
    })


    # Alacritty
    alacritty = set({
        'font_size': '9.0',
    }, host, {
        'p15': {'font_size': '8.0'}
    })


    # Default font for window titles (not bar.font)
    font = set('xft:URWGothic-Book 9')


    # Task tray
    tasktray = set({
        'enabled': True,
        'position': 'right',
    })


    # i3bar configs
    # All themes may obey these global bar configs, or they may set their own
    bar = set({
        'enabled': False,
        #'cmd': 'i3bar',
        'cmd': 'i3bar --transparency',
        'status_cmd': 'i3status',
        'position': 'bottom',
        'font': 'xft:URWGothic-Book 8',

        # Hide or show the bar
        'mode': 'dock', # dock|hide|invisible
        'hidden_state': 'hide', # hide|show

        # Modifier makes the hidden bar show up while key is pressed
        'modifier': 'none',
        #'modifier': 'Ctrl+$alt',
    },
        desktop != 'i3', {
            'mode': 'hide'
        },
        host, {
            'p15': {'position': 'top'},
            'p14s': {'enabled': True},
        },
    )


    # Applications (not autostarts)
    # Preferred applications, could change depending on DE installed
    apps = set({
        # These are mostly common generic all Desktop Environments and Installed Desktop Tools
        'terminal': 'alacritty',
        'webbrowser': 'firefox',
        'webbrowser2': 'chromium',
        'dmenu': set(path('~/.files/scripts/dmenu-run-blue'),
            theme, {'manjaro': path('~/.files/scripts/dmenu-run-green')
        }),
        'htop': 'htop',
        'bashtop': 'bashtop',
        'codeeditor': 'code',
        'screenlock': 'blurlock',
        'powermanager': 'xfce4-power-manager', # move to autostart
        'powermanagersettings': 'xfce4-power-manager-settings',
        'spotify': 'spotify',
        'networkeditor': 'nm-connection-editor',
    },
        desktop_tools=='kde', {
            #'terminal': 'konsole',
            'filemanager': 'dolphin',
            'calculator': 'kcalc',
            'settings': 'systemsettings',
            'taskmanager': 'ksysguard',
            'screenshot': 'spectacle',
            'colorpicker': 'kcolorchooser',
            'notepad': 'kate',
    },
        desktop_tools=='xfce', {
            #'terminal': 'gnome-terminal',
            'filemanager': 'thunar',
            'calculator': 'galculator', # xcalc
            'settings': 'xfce4-settings-manager',
            'taskmanager': 'xfce4-taskmanager',
            'notepad': 'mousepad',
    },
        desktop_tools=='gnome', {
            'filemanager': 'nautilus', # ???
            'terminal': 'gnome-terminal',
            'calculator': 'gnome-calculator',
    })


    # Autostarts
    #exec --no-startup-id blueman-applet
    #exec_always --no-startup-id sbxkb
    #exec --no-startup-id start_conky_maia
    #exec --no-startup-id start_conky_green
    autostart = set({
        # These only fire up if we are in pure i3 mode (no other desktop environment+i3)
        'session':  set(None, desktop=='i3' and desktop_tools=='xfce', 'exec --no-startup-id xfsettingsd --replace'),
        'locker':   set(None, desktop=='i3', 'exec_always --no-startup-id xss-lock -- blurlock'),
        #'locker':  set(None, desktop=='i3', 'exec_always --no-startup-id xss-lock -- i3lock --nofork --image ' + wallpaper_base + '/De/deepin.jpg'),
        'polkit':   set(None, desktop=='i3', 'exec --no-startup-id /usr/lib/polkit-kde-authentication-agent-1'),
        'screen':   set(None, desktop=='i3', 'exec --no-startup-id ~/.screenlayout/screen-laptop.sh'),
        'powerman': set(None, desktop=='i3', 'exec_always --no-startup-id ' + apps.powermanager),

        # If using polybar in pure i3
        'bar': set(None, desktop=='i3' and polybar.enabled, 'exec_always --no-startup-id ~/.config/polybar/launch.sh --' + polybar.theme),

        # Threse always fire up, regardless of how i3 is used
        'wallpaper': 'exec_always --no-startup-id nitrogen --restore',
        'compositor': 'exec_always --no-startup-id picom --config ~/.config/picom/picom.conf -b',
        'keyboard': 'exec_always --no-startup-id xset r rate 250 50',

        # Theme specific alttab
        'alttab': 'exec_always --no-startup-id "alttab -w 1 -s 1 -bw 0 -fg \'' + themes[theme].color + '\' -bg \'#0E2229\' -frame \'' + themes[theme].color + '\' -t 128x150 -i 127x64"',
    },
        # If tasktray is enabled running in pure i3
        tasktray.enabled and desktop=='i3', {
            'matray':  set(None, os=='manjaro', 'exec --no-startup-id matray'),
            'clipman': set('exec --no-startup-id clipit --daemon'),
            'netman':  set('exec --no-startup-id nm-applet'),
            'volume':  set('exec --no-startup-id volumeicon'),
        },
    )

    # Volume Control
    volume = set({
        'up': 'amixer -D pulse sset Master 5%+',
        'down': 'amixer -D pulse sset Master 5%-',
        'mute': 'amixer -D pulse set Master 1+ toggle',
        #'mixer': apps.terminal + ' -e alsamixer',
        'mixer': 'pavucontrol',
    })

    # Media Control
    media = set({
        'play_pause': 'playerctl play-pause',
        'next': 'playerctl next',
        'previous': 'playerctl previous',
    })

    # Brightness Control
    brightness = set({
        'up': 'brightnessctl -q set 3%+',
        'down': 'brightnessctl --min-val=2 -q set 3%-',
    })


    # Dynamically Load and Instantiate Plugins
    # Pluging must be LAST after all variables are set
    _vars = gather(locals())
    plugins = set({
        'nitrogen': plugin('nitrogen.Nitrogen')(_vars),
        'archey3': plugin('archey3.Archey3')(_vars),
        'polybar': plugin('polybar.Polybar')(_vars),
        'alacritty': plugin('alacritty.Alacritty')(_vars),
    })

    # Return all variables to the ohmyi3 generator for templating
    return gather(locals())




async def before_generate(config):
    """This hook fires before the new i3 config is generated"""

    # Kill some applications, as they don't re-autostart if already running
    util.shell('killall alttab')



async def after_generate(config):
    """This hook fires after the new i3 config is generated"""
    #dump('after hook')

    # REVIEW all these plugins.  They are very specific
    # For example, the polybar theme is specific to
    # https://github.com/adi1090x/polybar-themes style themes only and
    # is currently designed mostly for the "panels" variant.

    # Set themed wallpaper
    #config.plugins.nitrogen.set_wallpaper()

    # Set themed archey in my .zshrc and or .bashrc
    #config.plugins.archey3.set_archey()

    # Modify polybar theme files (template some variables)
    #config.plugins.polybar.adjust_polybar()

    # Template the alacritty config
    #config.plugins.alacritty.template_config()
