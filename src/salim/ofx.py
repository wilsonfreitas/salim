#!/usr/bin/python
# vim: expandtab ts=4 sw=4 ai

from HTMLParser import HTMLParser

__all__ = [ 'OFXFileParser', 'OFXTextParser' ]


class OFXParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__content = {'__parent__': None}
        self.__cs = self.__content
        self.__ct = None
        self.__open = False

    def __getitem__(self, key):
        key = str(key).lower()
        return self.__find_key(key, self.__content)

    def __setitem__(self, key, value):
        self.__content[str(key).lower()] = value

    def __delitem__(self, key):
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass

    def __contains__(self, item):
        pass

    def __find_key(self, key, cont):
        try:
            return cont[key]
        except KeyError:
            keys = filter(lambda x: type(cont[x]) is dict and x != '__parent__', cont.keys())
            for k in keys:
                r = self.__find_key(key, cont[k])
                if r: return r

    def handle_starttag(self, tag, attrs):
        self.__ct = tag
        self.__open = True

    def handle_data(self, data):
        if self.__ct and self.__open:
            data = data.strip()
            if data == '':
                if self.__ct in self.__cs:
                    d = self.__cs[self.__ct]
                    if type(d) is dict:
                        self.__cs[self.__ct] = [ d ]
                self.__cs = {'__parent__': self.__cs}
            else:
                self.__cs[self.__ct] = data

    def handle_endtag(self, tag):
        self.__ct = tag
        self.__open = False
        if tag not in self.__cs:
            try:
                if type(self.__cs['__parent__'][tag]) is list:
                    self.__cs['__parent__'][tag].append(self.__cs)
            except KeyError:
                self.__cs['__parent__'][tag] = self.__cs
            self.__cs = self.__cs['__parent__']


class OFXTextParser(OFXParser):
    def __init__(self, content):
        OFXParser.__init__(self)
        self.feed(content)


class OFXFileParser(OFXParser):
    def __init__(self, filename):
        OFXParser.__init__(self)
        # process header
        file = open(filename)
        content = file.read()
        self.__process_header(content)
        file.close()
        # process xml content
        if self['charset']:
            import codecs
            file = codecs.open(filename, encoding=self['charset'])
            content = file.read()
            file.close()
            self.feed(content)
            
    def __process_header(self, content):
        """ process ofx file header to obtain information about enconding and 
            charset """
        header = {}
        for line in content.splitlines():
            if len(line) and line[0] == '<':
                break
            if line.strip() != '':
                k, v = line.split(':')
                header[k.lower()] = v
        self['header'] = header

