import time

import requests

from .torrent import Torrent


# Class adapted from https://github.com/jerrymakesjelly/autoremove-torrents
class qBittorrent(object):
    # API Handler for v2
    class qBittorrentAPIHandlerV2(object):
        def __init__(self, host: str):
            # Host
            self._host = host.rstrip("/")
            # Requests Session
            self._session = requests.Session()

        # Check API Compatibility
        def check_compatibility(self):
            request = self._session.get(self._host + '/api/v2/app/webapiVersion')
            return request.status_code != 404  # compatible if API exsits

        # Get API major version
        def api_major_version(self):
            return 'v2'

        # Get API version
        def api_version(self):
            return self._session.get(self._host + '/api/v2/app/webapiVersion')

        # Get client version
        def client_version(self):
            return self._session.get(self._host + '/api/v2/app/version')

        # Login
        def login(self, username, password):
            return self._session.post(self._host + '/api/v2/auth/login',
                                      data={'username': username, 'password': password})

        # Get server state
        def server_state(self):
            return self._session.get(self._host + '/api/v2/sync/maindata')

        # Get torrent list
        def torrent_list(self, sort=None):
            return self._session.get(self._host + '/api/v2/torrents/info', params={"sort": sort})

        # Get torrent's generic properties
        def torrent_generic_properties(self, torrent_hash):
            return self._session.get(self._host + '/api/v2/torrents/properties', params={'hash': torrent_hash})

        # Get torrent's tracker
        def torrent_trackers(self, torrent_hash):
            return self._session.get(self._host + '/api/v2/torrents/trackers', params={'hash': torrent_hash})

        def torrent_peers(self, torrent_hash, rid=None):
            if not rid:
                return self._session.get(self._host + '/api/v2/sync/torrentPeers', params={'hash': torrent_hash})
            else:
                return self._session.get(self._host + '/api/v2/sync/torrentPeers', params={'hash': torrent_hash, 'rid': rid})

        # Batch Delete torrents
        def delete_torrents(self, torrent_hash_list):
            return self._session.get(self._host + '/api/v2/torrents/delete',
                                     params={'hashes': '|'.join(torrent_hash_list), 'deleteFiles': False})

        # Batch Delete torrents and data
        def delete_torrents_and_data(self, torrent_hash_list):
            return self._session.get(self._host + '/api/v2/torrents/delete',
                                     params={'hashes': '|'.join(torrent_hash_list), 'deleteFiles': True})

        def add_torrent(self, url, category):
            return self._session.post(self._host + '/api/v2/torrents/add',
                                      data={"urls": url, "category": category})

        def add_torrent_with_cookie(self, url, category, cookie):
            return self._session.post(self._host + '/api/v2/torrents/add',
                                      data={"urls": url, "category": category, "cookie": cookie})

        def add_category(self, category):
            return self._session.post(self._host + '/api/v2/torrents/createCategory',
                                      data={"category": category})

    def __init__(self, host, username, password, **kwargs):
        # Torrents list cache
        self._torrents_list_cache = []
        self._refresh_cycle = 30
        self._refresh_time = 0

        # Request Handler
        self._request_handler = self.qBittorrentAPIHandlerV2(host)
        self.login(username, password)

    # Login to qBittorrent
    def login(self, username, password):
        try:
            request = self._request_handler.login(username, password)
        except Exception as exc:
            raise RuntimeError(str(exc))

        if request.status_code == 200:
            if request.text == 'Fails.':  # Fail
                raise RuntimeError(request.text)
        else:
            raise RuntimeError('The server returned HTTP %d.' % request.status_code)

    # Get client status
    # def client_status(self):
    #     status = self._request_handler.server_state().json()['server_state']
    #
    #     cs = ClientStatus()
    #     # Remote free space checker
    #     cs.free_space = self.remote_free_space
    #     # Downloading speed and downloaded size
    #     cs.download_speed = status['dl_info_speed']
    #     cs.total_downloaded = status['dl_info_data']
    #     # Uploading speed and uploaded size
    #     cs.upload_speed = status['up_info_speed']
    #     cs.total_uploaded = status['up_info_data']
    #
    #     return cs

    # Get qBittorrent Version
    def version(self):
        request = self._request_handler.client_version()
        return ('qBittorrent %s' % request.text)

    # Get API version
    def api_version(self):
        return ('%s (%s)' % (self._request_handler.api_version().text, self._request_handler.api_major_version()))

    # Get Torrents List
    def torrents_list(self):
        # Request torrents list
        torrent_hash = []
        request = self._request_handler.torrent_list()
        result = request.json()
        # Save to cache
        self._torrents_list_cache = result
        self._refresh_time = time.time()
        # Get hash for each torrent
        for torrent in result:
            torrent_hash.append(torrent['hash'])
        return torrent_hash

    # Get Torrent Properties
    def torrent_properties(self, torrent_hash):
        if time.time() - self._refresh_time > self._refresh_cycle:  # Out of date
            self.torrents_list()
        for torrent in self._torrents_list_cache:
            if torrent['hash'] == torrent_hash:
                # Get other information
                properties = self._request_handler.torrent_generic_properties(torrent_hash).json()
                trackers = self._request_handler.torrent_trackers(torrent_hash).json()
                # Create torrent object
                torrent_obj = Torrent()
                torrent_obj.hash = torrent['hash']
                torrent_obj.name = torrent['name']
                # The category list will be empty if a torrent was not specified categories
                torrent_obj.category = torrent['category']
                torrent_obj.tracker = [tracker['url'] for tracker in trackers]
                torrent_obj.status = torrent['state']
                torrent_obj.stalled = torrent['state'] == 'stalledUP' or torrent['state'] == 'stalledDL'
                torrent_obj.size = torrent['size']
                torrent_obj.ratio = torrent['ratio']
                torrent_obj.uploaded = properties['total_uploaded']
                torrent_obj.downloaded = properties['total_downloaded']
                torrent_obj.create_time = properties['addition_date']
                torrent_obj.seeding_time = properties['seeding_time']
                torrent_obj.upload_speed = properties['up_speed']
                torrent_obj.download_speed = properties['dl_speed']
                torrent_obj.seeder = properties['seeds_total']
                torrent_obj.connected_seeder = properties['seeds']
                torrent_obj.leecher = properties['peers_total']
                torrent_obj.connected_leecher = properties['peers']
                torrent_obj.average_upload_speed = properties['up_speed_avg']
                torrent_obj.average_download_speed = properties['dl_speed_avg']
                # For qBittorrent 3.x, the last activity field doesn't exist.
                # We need to check the existence
                if 'last_activity' in torrent:
                    # Convert to time interval since last activity
                    torrent_obj.last_activity = self._refresh_time - torrent['last_activity'] \
                        if torrent['last_activity'] > 0 else None
                torrent_obj.progress = torrent['progress']

                return torrent_obj

    # Get free space
    def remote_free_space(self):
        status = self._request_handler.server_state().json()['server_state']

        # There is no free space data in qBittorrent 3.x
        if 'free_space_on_disk' in status:
            return status['free_space_on_disk']
        return None

    # Judge Torrent Status (qBittorrent doesn't have stopped status)
    # @staticmethod
    # def _judge_status(state):
    #     if state == 'downloading' or state == 'stalledDL':
    #         status = TorrentStatus.Downloading
    #     elif state == 'queuedDL' or state == 'queuedUP':
    #         status = TorrentStatus.Queued
    #     elif state == 'uploading' or state == 'stalledUP':
    #         status = TorrentStatus.Uploading
    #     elif state == 'checkingUP' or state == 'checkingDL':
    #         status = TorrentStatus.Checking
    #     elif state == 'pausedUP' or state == 'pausedDL':
    #         status = TorrentStatus.Paused
    #     elif state == 'error':
    #         status = TorrentStatus.Error
    #     else:
    #         status = TorrentStatus.Unknown
    #     return status

    # Batch Remove Torrents
    # Return values: (success_hash_list, failed_list -> {hash: reason, ...})
    def remove_torrents(self, torrent_hash_list, remove_data=True):
        request = self._request_handler.delete_torrents_and_data(torrent_hash_list) if remove_data \
            else self._request_handler.delete_torrents(torrent_hash_list)
        if request.status_code != 200:
            return ([], [{
                'hash': torrent,
                'reason': 'The server responses HTTP %d.' % request.status_code,
            } for torrent in torrent_hash_list])
        # Some of them may fail but we can't judge them,
        # So we consider all of them as successful.
        return torrent_hash_list, []

    def add_torrent(self, url, category, cookie=None):
        if cookie:
            request = self._request_handler.add_torrent_with_cookie(url, category, cookie)
        else:
            request = self._request_handler.add_torrent(url, category)
        if request.status_code != 200:
            return [], [{
                'url': url,
                'reason': 'The server responses HTTP %d.' % request.status_code,
            }]
        return [url], []

    def create_category(self, category):
        request = self._request_handler.add_category(category)
        if request.status_code != 200:
            print(request)
            print(request.text)
            print("Could not create category %d" % category)
