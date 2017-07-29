#/*
# *
# * Overcast for Kodi.
# *
# * Copyright (C) 2017 Brian Hornsby
# *
# * This program is free software: you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program.  If not, see <http://www.gnu.org/licenses/>.
# *
# */

import xbmc
import xbmcgui
import xbmcplugin
import ast
import os
import urllib
import urllib2
import re

sys.path.append('resourceslib')
import resources.lib.cache as cache
import resources.lib.kodidownload as download
import resources.lib.kodisettings as settings
import resources.lib.kodiutils as utils
import resources.lib.overcast as overcast

# Set some global values.
__xbmcrevision__ = xbmc.getInfoLabel('System.BuildVersion')
__addonid__ = 'plugin.audio.overcast'
__author__ = 'Brian Hornsby'

# Initialise settings.
__settings__ = settings.Settings(__addonid__, sys.argv)

# Get addon information.
__addonname__ = __settings__.get_name()
__version__ = __settings__.get_version()

# Get addon settings values.
__email__ = __settings__.get('email')
__password__ = __settings__.get('password')
__prompt__ = __settings__.get('prompt') == "true"
__debuglevel__ = __settings__.get('debuglevel')

# Initialise parameters.
__params__ = utils.get_params(__settings__.get_argv(2))
__path__ = utils.get_value(__params__, 'path')
__url__ = utils.get_value(__params__, 'url')


def log_debug(msg, dbglvl):
    if __debuglevel__ >= int(dbglvl):
        print '%s: DEBUG: %s' % (__addonname__, utils.normalize_unicode(msg))


def log_error(msg):
    print '%s: ERROR: %s' % (__addonname__, utils.normalize_unicode(msg))

log_debug('Addon: %s' % __addonname__, 1)
log_debug('Version: %s' % __version__, 1)
log_debug('Params: %s: %s' % (__path__, __params__), 1)

__overcast__ = overcast.Overcast()

if __path__ == 'podcast':
    for episode in __overcast__.episodes(__url__):
        liz = xbmcgui.ListItem(episode['title'], iconImage=episode[
                               'artworkURL'], thumbnailImage=episode['artworkURL'])
        u = utils.add_params(
            root=__settings__.get_argv(0), params={'path': 'episode', 'url': episode['url']})
        ok = xbmcplugin.addDirectoryItem(handle=int(__settings__.get_argv(1)),
                                         url=u,
                                         listitem=liz,
                                         isFolder=False)
    xbmcplugin.endOfDirectory(int(__settings__.get_argv(1)))

# Play an episode
elif __path__ == 'episode':
    episode = __overcast__.episode(__url__)
    liz = xbmcgui.ListItem(episode['title'], iconImage=episode[
                           'artworkURL'], thumbnailImage=episode['artworkURL'])
    liz.setInfo('music', {'title': episode[
                'title'], 'artist': episode['podcastTitle']})
    if (__prompt__ and xbmc.Player().isPlayingAudio()):
        if (utils.yesno(__addonname__, __settings__.get_string(3001))):
            xbmc.Player().play(item=episode['url'], listitem=liz)
    else:
        xbmc.Player().play(item=episode['url'], listitem=liz)

# Refresh display.
elif __path__ == 'refresh':
    xbmc.executebuiltin('Container.Refresh')

# Search for a podcast.
elif __path__ == 'search':
    try:
        searchstring = utils.keyboard(heading=__settings__.get_string(3000))
        if (searchstring and len(searchstring) > 0):
            podcasts = __overcast__.search(searchstring)
            contextmenu = [(__settings__.get_string(
                1001), 'XBMC.RunPlugin(%s?path=refresh)' % (__settings__.get_argv(0)))]
            for podcast in podcasts:
                liz = xbmcgui.ListItem(podcast['title'], iconImage=podcast[
                                       'thumbURL'], thumbnailImage=podcast['artworkURL'])
                liz.addContextMenuItems(items=contextmenu, replaceItems=True)
                u = utils.add_params(
                    root=__settings__.get_argv(0), params={'path': 'podcast', 'url': '/p' + podcast['id'] + '-' + podcast['hash']})
                ok = xbmcplugin.addDirectoryItem(handle=int(__settings__.get_argv(1)),
                                                 url=u,
                                                 listitem=liz,
                                                 isFolder=True)
            xbmcplugin.endOfDirectory(int(__settings__.get_argv(1)))

    # except __overcast__.TuneInError as e:
    #     utils.ok(__addonname__, __settings__.get_string(3004),
    #              __settings__.get_string(3003))
    #     log_error('TuneInError: %s %s' % (e.status, e.fault))
    except urllib2.URLError as e:
        utils.ok(__addonname__, __settings__.get_string(3002),
                 __settings__.get_string(3003))
        log_error('URLError: %s' % e)

# Display main menu.
else:
    __overcast__.login(__email__, __password__)

    contextmenu = [(__settings__.get_string(
        1001), 'XBMC.RunPlugin(%s?path=refresh)' % (__settings__.get_argv(0)))]

    for episode in __overcast__.active_episodes():
        liz = xbmcgui.ListItem(episode['title'], iconImage=episode[
                               'thumbURL'], thumbnailImage=episode['thumbURL'])
        liz.addContextMenuItems(items=contextmenu, replaceItems=True)
        u = utils.add_params(
            root=__settings__.get_argv(0), params={'path': 'episode', 'url': episode['url']})
        ok = xbmcplugin.addDirectoryItem(handle=int(__settings__.get_argv(1)),
                                         url=u,
                                         listitem=liz,
                                         isFolder=False)

    for podcast in __overcast__.podcasts():
        liz = xbmcgui.ListItem(podcast['title'], iconImage=podcast[
                               'thumbURL'], thumbnailImage=podcast['thumbURL'])
        liz.addContextMenuItems(items=contextmenu, replaceItems=True)
        u = utils.add_params(
            root=__settings__.get_argv(0), params={'path': 'podcast', 'url': podcast['url']})
        ok = xbmcplugin.addDirectoryItem(handle=int(__settings__.get_argv(1)),
                                         url=u,
                                         listitem=liz,
                                         isFolder=True)

    iconImage = __settings__.get_path('resources/images/search-32.png')
    thumbnailImage = __settings__.get_path('resources/images/search-256.png')
    liz = xbmcgui.ListItem(__settings__.get_string(1000), iconImage=iconImage, thumbnailImage=thumbnailImage)
    liz.addContextMenuItems(items=contextmenu, replaceItems=True)
    u = utils.add_params(
        root=__settings__.get_argv(0), params={'path': 'search'})
    ok = xbmcplugin.addDirectoryItem(handle=int(
        __settings__.get_argv(1)), url=u, listitem=liz, isFolder=True)

    xbmcplugin.endOfDirectory(int(__settings__.get_argv(1)))
