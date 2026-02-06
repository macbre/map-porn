#!/usr/bin/env python3
import logging
import json
from csv import writer
from os import getenv, path

from shared import get_http_client

import requests

DIR = path.abspath(path.dirname(__file__))

FLICKR_REST_URL = 'https://www.flickr.com/services/rest/'

class DuplicatedPhotoError(Exception):
    pass


class FlickrAPIError(Exception):
    pass


def call_flickr_api(params: dict[str, str]) -> object:
    logger = logging.getLogger(name="flickr-api")
    resp = get_http_client().get(
        url=FLICKR_REST_URL,
        params=params
    )
    resp.raise_for_status()

    logger.info(f'HTTP {resp.status_code} {resp.request.url}')

    try:
        logger.debug(f'Headers: {resp.headers}')
        logger.debug(f'Resp: {resp.text}')
        data = json.loads(resp.text)

        # {"stat":"fail","code":100,"message":"Invalid API Key (Key has expired)"}
        if data.get('stat') == 'fail':
            raise FlickrAPIError(f"Request returned error #{data['code']}: {data['message']}")

        return data
    except json.JSONDecodeError as ex:
        logging.error(f'Parsing the response failed: {ex.msg}', exc_info=True)
        logging.warning(ex.doc)
        raise


def main():
    logger = logging.getLogger(name="flickr")

    # bbox
    # The 4 values represent the bottom-left corner of the box and the top-right corner:
    # minimum_longitude, minimum_latitude, maximum_longitude, maximum_latitude.
    FLICKR_BOUNDARY_BOX = [-7.789,61.351,-6.064,62.433]
    FLICKR_API_KEY = getenv('FLICKR_API_KEY')

    if FLICKR_API_KEY is None:
        raise Exception('FLICKR_API_KEY env var needs to be set')

    logger.info(f'Getting Flickr photos from within the boundary box: {FLICKR_BOUNDARY_BOX} ...')

    csv_file = path.join(DIR, '..', 'geojson', 'flickr-faroe.csv')
    logger.info(f'Writing CSV data to {csv_file} ...')

    page = 1

    # for duplicates detection in consequtive responses from the API
    photos: list[str] = []

    with open(csv_file, 'wt') as fp:
        csv = writer(fp, delimiter="\t")
        csv.writerow(['id', 'lat', 'lon', 'date_taken', 'title'])

        while True:
            # https://www.flickr.com/services/api/flickr.photos.search.html
            # DEBUG:flickr-api:Resp: {"photos":{"page":1,"pages":392,"perpage":100,"total":39182,"photo":[{"id":"55076143656"
            resp = call_flickr_api({
                'api_key': FLICKR_API_KEY,
                'format': 'json',
                'nojsoncallback': '1',  # otherwise "jsonFlickrApi()" is added to the response :/
                'method': 'flickr.photos.search',
                'page': str(page),
                'per_page': '100',

                # Geo queries require some sort of limiting agent in order to prevent the database from crying.
                # This is basically like the check against "parameterless searches" for queries without a geo component.
                #
                # A tag, for instance, is considered a limiting agent as are user defined min_date_taken and min_date_upload parameters.
                # If no limiting factor is passed we return only photos added in the last 12 hours (though we may extend the limit in the future).
                'bbox': ','.join(map(lambda item: str(item), FLICKR_BOUNDARY_BOX)),

                # the date can be in the form of a unix timestamp or mysql datetime.
                'min_date_taken': '2012-01-01 00:00:00',

                # date-posted-asc, date-posted-desc, date-taken-asc, date-taken-desc, interestingness-desc, interestingness-asc, and relevance.
                'sort': 'relevance',

                # Currently supported fields are: description, license, date_upload, date_taken, owner_name, icon_server, original_format,
                # last_update, geo, tags, machine_tags, o_dims, views, media, path_alias,
                # url_sq, url_t, url_s, url_q, url_m, url_n, url_z, url_c, url_l, url_o
                'extras': ','.join(['geo', 'views', 'date_taken'])
            })

            if page > resp.get('photos', {}).get('pages'):
                logger.info("Reached the last page")
                break

            if page == 1:
                # INFO:flickr:Results count: 41243
                logger.info(f"Results count: {resp.get('photos', {}).get('total')} on {resp.get('photos', {}).get('pages')} pages")
            else:
                logger.info(f"Page #{page} ...")

            for photo in resp.get('photos', {}).get('photo', []):
                if photo['id'] in photos:
                    # raise DuplicatedPhotoError(f"#{photo['id']} photo already returned by a previous API request")
                    logger.warning(f"#{photo['id']} photo already returned by a previous API request")
                    continue

                # "id":"55076143656","owner":"59703682@N05","title":"Between Land and Tide","latitude":"61.468730","longitude":"-6.764811","datetaken": "2006-07-21 00:25:02"
                # logger.info(f"#{photo['id']}: ({photo['latitude']}, {photo['longitude']} at {photo['datetaken']}")
                csv.writerow([photo['id'], photo['latitude'], photo['longitude'], photo['datetaken'], photo['title']])
                photos.append(photo['id'])

            page +=1

    logger.info(f'Done, {len(photos)} photos found')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
