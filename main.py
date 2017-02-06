# -*- coding: utf-8 -*-
# Module: default
# Author: Roman V. M.
# Created on: 28.11.2014
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
import os
from urllib import urlencode
from urlparse import parse_qsl
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import httplib
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
import json


# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

addon = xbmcaddon.Addon()
home = xbmc.translatePath(addon.getAddonInfo('path'))



def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Get video categories
    # Iterate through categories
    # Create a list item with a text label and a thumbnail image.
    list_item = xbmcgui.ListItem(label='LiveTV')
    # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
    # Here we use the same image for all items for simplicity's sake.
    # In a real-life plugin you need to set each image accordingly.
    list_item.setArt({'thumb': os.path.join(home, 'icon.png'),
                      'icon': os.path.join(home, 'icon.png'),
                      'fanart': os.path.join(home, 'fanart.jpg')})
    # Set additional info for the list item.
    # Here we use a category name for both properties for for simplicity's sake.
    # setInfo allows to set various information for an item.
    # For available properties see the following link:
    # http://mirrors.xbmc.org/docs/python-docs/15.x-isengard/xbmcgui.html#ListItem-setInfo
    list_item.setInfo('video', {'title': 'LiveTV', 'genre': 'LiveTV'})
    # Create a URL for a plugin recursive call.
    # Example: plugin://plugin.video.xs4me/?action=listing&category=Animals
    url = get_url(action='listing', category='LiveTV')
    # is_folder = True means that this item opens a sub-list of lower level items.
    is_folder = True
    # Add our item to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def get_icon(channel):
    """
    Get icon path.
    
    return: icon url
    rtype: str
    """
    
    _check_icon = False
    
    _url = os.path.join(home, 'icon.png')
    _icon_server = "webtv.xs4all.nl"
    _correct_icon_path = "/images/channels/" + channel + ".png"
    _correct_icon_url = "https://" + _icon_server + _correct_icon_path
    
    if _check_icon:
        conn = httplib.HTTPSConnection(_icon_server)
        conn.request("HEAD", _correct_icon_path)
        res = conn.getresponse()
        if res.status == 200:
	    headers = res.getheaders()
	    content_type = [x[1] for x in headers if x[0] == 'content-type'][0]
            if content_type == 'image/png':
	        _url = _correct_icon_url
    else:
        _url = _correct_icon_url
	
    return _url	    


def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """
    # Get the list of videos in the category.
    url_channels="https://webtv-api.xs4all.nl/2/listchannels.json"
    response_channels = urlopen(url_channels)
    data = json.load(response_channels)
    sorted_channels = sorted(data['channels'], key = lambda x: x['number'])
    # Iterate through videos.
    for video in sorted_channels:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['name'])
        # Set additional info for the list item.
        list_item.setInfo('video', {'title': video['name'], 'genre': 'TV'})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': get_icon(video['id']), 'icon': get_icon(video['id']), 'fanart': get_icon(video['id'])})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.xs4me/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
        url = get_url(action='play', video=video['id'])
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def play_video(channel):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    _url_channels="https://webtv-api.xs4all.nl/2/listchannels.json"
    _response_channels = urlopen(_url_channels)
    _data = json.load(_response_channels)
    _data = [x for x in _data['channels'] if x['id'] == channel][0]
    _title = _data['name']

    _url_channel="https://webtv-api.xs4all.nl/2/channel/" + channel + "/dashwv/medium.json"
    _response_channel = urlopen(_url_channel)
    _data = json.load(_response_channel)

    listitem = xbmcgui.ListItem(label=_title, path=_data['streamurl'])

    #if extern or trailer == '1':
    #    listitem.setInfo('video', Info)

    #if 'adaptive' in is_addon:
    #    listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    
    listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')

    #Log('Using %s Version:%s' %(is_addon, xbmcaddon.Addon(is_addon).getAddonInfo('version')))
    listitem.setArt({'thumb': get_icon(channel)})
    #listitem.setSubtitles(subs)
    if 'laurl' in _data.keys():
        listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
        listitem.setProperty('inputstream.adaptive.license_key', _data['laurl'])
	
    # save (quick and dirty) the .mpd file:
    local_filename = "manifest.mpd"
    r = requests.get(_data['streamurl'], stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
	    if chunk:
	        f.write(chunk)
    
    listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
    xbmcplugin.setResolvedUrl(_handle, True, listitem=listitem)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
