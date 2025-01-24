#!/usr/bin/python3

from argparse import ArgumentParser
import json
import os
import sys

import ox
import ox.api


def upload(api_url, files, metadata):
    '''
        create new item with metadata and upload all files to that item
        returns the item id of the new item

        upload('https://pandora/api/', ['/home/pandora/Videos/example.mp4'], {'title': 'This is an example'})
    '''
    api = ox.api.signin(api_url)
    item_id = None
    if isinstance(files, str):
        files = [files]
    for path in files:
        oshash = ox.oshash(path)
        filename = os.path.basename(path)
        data = {
            'id': oshash,
            'filename': filename
        }
        if item_id:
            data['item'] = item_id
        r = api.addMedia(data)
        if not item_id:
            item_id = r['data']['item']

        api.upload_chunks(api.url + 'upload/direct/', path, {'id': oshash})
    if item_id:
        data = metadata.copy()
        data['id'] = item_id
        api.edit(data)
    return item_id

def main():
    usage = "usage: %(prog)s [options] path"
    parser = ArgumentParser(usage=usage, prog='pandora-upload')
    parser.add_argument('-v', '--version', action="version", version="%(prog)s 1.0")
    parser.add_argument('-p', '--pandora', dest='api_url',
        help='pandora api url', default='http://127.0.0.1:2620/api/')
    parser.add_argument('-d', '--debug', dest='debug',
        help='output debug information', action="store_true")
    parser.add_argument('-m', '--meta', dest='meta', help='metadata key=value', action='append')
    parser.add_argument('files', metavar='path', type=str, nargs='*', help='file or files to upload')
    opts = parser.parse_args()
    meta = {}
    if opts.meta:
        for m in opts.meta:
            if '=' not in m:
                parser.print_help()
                print('\ninvalid metadata argument, format is -m "key=value"')
                sys.exit(1)
            k, v = m.split('=', 1)
            if k in meta:
                if isinstance(meta[k], str):
                    meta[k] = [meta[k]]
                meta[k].append(v)
            elif v[0] == '[' and v[-1] == ']':
                meta[k] = v[1:-1]
            else:
                meta[k] = v
    files = opts.files
    if not files:
        parser.print_help()
        sys.exit(1)

    id = upload(opts.api_url, files, meta)
    print(id)

