"""
p2pTorrent Generator and Parser
"""
import json
from hashlib import sha256
from uuid import uuid4
from collections import namedtuple


class Torrent:
    def __init__(self, name, _uuid, digest, description, size, chunks, digests, chunk_size):
        self.name = name
        self.uuid = _uuid
        self.digest = digest
        self.description = description
        self.size = size
        self.chunks = chunks
        self.digests = digests
        self.chunk_size = chunk_size

    @staticmethod
    def create_torrents(filename, data, name=None, description=None, chunk_size=102400):
        """
        Create a torrent file with a given chunk size from a path (aka. filename)

        :param name: the torrent name
        :param description: the description of this torrent file
        :param filename: the path of the file
        :param data: the data of the file
        :param chunk_size: the chunk size of the torrent
        :return: a Torrent instance
        """
        if name is None:
            name = filename
        if description is None:
            description = 'Torrent of {}. Made by p2pTorrent Generator.'.format(name)
        # TODO: calc the digest without read all into memory
        sliced_obj = [data[i: i + chunk_size] for i in range(0, len(data), chunk_size)]
        digests = [None] * len(sliced_obj)
        for i in range(len(sliced_obj)):
            _hash = sha256()
            _hash.update(sliced_obj[i])
            digests[i] = _hash.hexdigest()
        _hash = sha256()
        _hash.update(data)
        torrent = Torrent(name, str(uuid4()), _hash.hexdigest(), description,
                          size=len(data), chunks=len(sliced_obj), digests=digests,
                          chunk_size=chunk_size)
        return torrent

    @staticmethod
    def create_torrent(filename, name=None, description=None, chunk_size=102400):
        """
        Create a torrent file with a given chunk size from a path (aka. filename)

        :param name: the torrent name
        :param description: the description of this torrent file
        :param filename: the path of the file
        # :param data: the data of the file
        :param chunk_size: the chunk size of the torrent
        :return: a Torrent instance
        """
        if name is None:
            name = filename
        if description is None:
            description = 'Torrent of {}. Made by p2pTorrent Generator.'.format(name)
        with open(filename, mode='rb') as reader:
            _data = reader.read()
            return Torrent.create_torrents(filename, _data, name, description, chunk_size)

    def dumps(self):
        return json.dumps(self.__dict__, indent=2)

    def dump(self, filename):
        with open(filename, 'w') as writer:
            writer.write(self.dumps())

    @staticmethod
    def loads(string):
        _dict = json.loads(string)
        return namedtuple('Torrent', _dict.keys())(*_dict.values())

    @staticmethod
    def load(filename):
        with open(filename, 'r') as reader:
            return Torrent.loads(reader.read())

    def __str__(self):
        return self.dumps
