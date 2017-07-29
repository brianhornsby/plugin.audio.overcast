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


import json
import urllib
import urllib2

from bs4 import BeautifulSoup
import mechanize


class Overcast(object):

    _baseurl = 'https://overcast.fm'

    def __init__(self):
        self._email = None
        self._password = None

    def login(self, email, password):
        self._email = email
        self._password = password
        br = mechanize.Browser()
        br.open(self._baseurl + '/login')
        forms = list(br.forms())
        form = forms[0]
        form['email'] = self._email
        form['password'] = self._password
        request = form.click()
        try:
            response = mechanize.urlopen(request)
        except mechanize.HTTPError, response2:
            pass

    def logout(self):
        try:
            response = mechanize.urlopen(self._baseurl + '/logout')
        except mechanize.HTTPError, response2:
            pass
        response.close()

    def _readsoup(self, url):
        try:
            response = mechanize.urlopen(self._baseurl + url)
        except mechanize.HTTPError, response2:
            pass

        soup = BeautifulSoup(response.read(), 'html5lib')
        response.close()
        return soup

    def episode(self, url):
        soup = self._readsoup(url)
        return {'url': soup.find('audio', id='audioplayer').source['src'],
                'artworkURL': soup.find('img', class_='fullart')['src'],
                'title': unicode(soup.find('div', class_='titlestack').find('div', class_='title').string),
                'podcastTitle': unicode(soup.find('div', class_='titlestack').find('div', class_='caption2').string)}

    def active_episodes(self):
        soup = self._readsoup('/podcasts')

        active_episodes = []
        episodecells = soup.find_all('a', class_='episodecell')
        for episodecell in episodecells:
            active_episodes.append({'url': episodecell['href'], 'thumbURL': episodecell.img['src'], 'podcast': unicode(episodecell.div.div.div.string),
                                    'title': unicode(episodecell.div.div.div.nextSibling.nextSibling.string),
                                    'caption': unicode(episodecell.div.div.div.nextSibling.nextSibling.nextSibling.nextSibling.string)})

        return active_episodes

    def episodes(self, url):
        soup = self._readsoup(url)

        episodes = []
        extendedepisodecells = soup.find_all(
            'a', class_='extendedepisodecell')
        for extendedepisodecell in extendedepisodecells:
            episodes.append({'url': extendedepisodecell['href'], 'title': unicode(extendedepisodecell.div.div.div.string),
                             'caption': unicode(extendedepisodecell.div.div.find('div', class_='caption2').string),
                             'description': unicode(extendedepisodecell.div.div.find('div', class_='lighttext').string).replace('\n', '').strip(),
                             'artworkURL': soup.find('img', class_='fullart')['src']})

        return episodes

    def podcasts(self):
        soup = self._readsoup('/podcasts')

        podcasts = []
        feedcells = soup.find_all('a', class_='feedcell')
        for feedcell in feedcells:
            if unicode(feedcell.div.div.div.string) != 'Uploads':
                podcasts.append({'title': unicode(feedcell.div.div.div.string), 'url': feedcell[
                                'href'], 'thumbURL': feedcell.img['src']})

        return podcasts

    def search(self, query):
        req = urllib2.Request(
            self._baseurl + '/podcasts/search_autocomplete?' + urllib.urlencode({'q': query}))
        f = urllib2.urlopen(req)
        result = json.load(f)
        f.close()
        return result
