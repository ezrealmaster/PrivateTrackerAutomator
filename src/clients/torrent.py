import time
from dataclasses import dataclass
from urllib.parse import urlparse


# Class adapted from https://github.com/jerrymakesjelly/autoremove-torrents
@dataclass()
class Torrent:
    hash = None
    name = None
    progress = None
    category = None
    tracker = None
    status = None
    size = None
    ratio = None
    uploaded = None
    create_time = None
    seeding_time = None

    # NOTE: The attribute 'last_activity' stores the time interval since last activity,
    #       not the unix timestamp of last activity.

    def __str__(self):
        def disp(prop, converter=None):
            if hasattr(self, prop):
                if converter is None:
                    return getattr(self, prop)
                else:
                    return converter(getattr(self, prop))
            else:
                return '(Not Provided)'

        return ("%s\n" +
                "\tProgress:%.2f%%\tSize:%s\tRatio:%.3f\tTotal Uploaded:%s\n" +
                "\tSeeder(connected/total):%d/%d\tLeecher(connected/total):%d/%d\tStatus:%s\n" +
                "\tDownload Speed:%s(Avg.:%s)\tUpload Speed:%s(Avg.:%s)\n" +
                "\tCreate Time:%s\tSeeding Time:%s\tDownloading Time:%s\tLast Activity:%s\n" +
                "\tCategory:%s\tTracker:%s") % \
            (
                disp('name'),
                disp('progress', lambda x: x * 100),
                disp('size', convert_bytes),
                disp('ratio'),
                disp('uploaded', convert_bytes),
                disp('connected_seeder'),
                disp('seeder'),
                disp('connected_leecher'),
                disp('leecher'),
                disp('status', lambda s: s.name),
                disp('download_speed', convert_speed),
                disp('average_download_speed', convert_speed),
                disp('upload_speed', convert_speed),
                disp('average_upload_speed', convert_speed),
                disp('create_time', convert_timestamp),
                disp('seeding_time', convert_seconds),
                disp('downloading_time', convert_seconds),
                disp('last_activity', convert_seconds),
                disp('category', ','.join),
                disp('tracker', lambda t: \
                    ','.join(
                        [urlparse(x).hostname if urlparse(x).hostname is not None else x for x in t]
                    )
                     ),
            )


def convert_bytes(byte):
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB', 'BiB', 'NiB', 'DiB', 'CiB']
    for x in units:
        if divmod(byte, 1024)[0] == 0:
            break
        else:
            byte /= 1024
    return '%.2lf%s' % (byte, x)


def convert_seconds(sec):
    if sec is None:
        return 'None'

    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return '%dd %02d:%02d:%02d' % (d, h, m, s)


def convert_speed(byte):
    return '%s/s' % convert_bytes(byte)


def convert_timestamp(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
