#!/usr/bin/env python3
import logging
import json
from os import path

from shared import Node, nodes_to_geojson_collection, get_http_client

DIR = path.abspath(path.dirname(__file__))

def iterate_posts(blog_url: str, per_page: int = 75) -> iter:
    logger = logging.getLogger('iterate_posts')

    base_url = f'{blog_url.rstrip("/")}/wp-json/wp/v2/posts'
    logger.info(f'Using <{base_url}> as the base URL')

    page = 1
    while(True):
        resp = get_http_client().get(base_url, params=dict(page=page, per_page=per_page))
        logger.info(f'Page #{page} | HTTP {resp.status_code}')
        
        # we're out of posts!
        if resp.status_code == 400:
            logger.info("Run out of posts")
            return

        resp.raise_for_status()

        posts = json.loads(resp.text)

        for post in posts:
            yield post

        page += 1


def index_wp_geo(blog_url: str):
    """
    https://developer.wordpress.org/rest-api/reference/posts/
    e.g. https://farerskiekadry.pl/wp-json/wp/v2/posts?per_page=100
    """
    logger = logging.getLogger('index_wp_geo')
    logger.info(f"Index WordPress geo data from the <{blog_url}> blog ...")

    nodes = []

    for post in iterate_posts(blog_url):
        # no geo-data found
        geo_data = post.get("geo", False)
        if geo_data == False:
            continue

        # e.g. https://farerskiekadry.pl/wp-json/wp/v2/posts/4220
        post_title = post.get("title", {}).get("rendered")

        node = Node(
            lat=str(geo_data.get("geo_latitude")),
            lon=str(geo_data.get("geo_longitude")),
            tags=[
                ('title', post_title),
                ('url', post.get("link")),
                ('date', post.get("date")),
                ('excerpt', post.get("excerpt", {}).get("rendered")),
                ('address', geo_data.get("geo_address")),
            ]
        )

        logger.info(f'#{post.get("id")} | {post_title} {repr(node)}')

        nodes.append(node)


    geojson_file = path.join(DIR, '..', 'geojson', f'farerskie_kadry.json')
    logger.info(f'Posts with geo-data found: {len(nodes)}, saving to {geojson_file} ...')

    with open(geojson_file, 'wt') as fp:
        json.dump(
            obj=nodes_to_geojson_collection(nodes),
            fp=fp,
            indent=True
        )

    logger.info("Done!")


if __name__ == '__main__':
    BLOG_URL = 'https://farerskiekadry.pl/'
    logging.basicConfig(level=logging.INFO)
    index_wp_geo(blog_url=BLOG_URL)
