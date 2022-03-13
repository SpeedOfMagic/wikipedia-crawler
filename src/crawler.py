import requests

from server_config import EXCLUDE_SECTIONS


def get_links(url: str) -> set[str]:
    html = requests.get(url).content.decode()
    result = set()
    for possible_link in html.split('"'):
        if possible_link.startswith('/wiki/'):
            possible_link = possible_link.removeprefix('/wiki/')
            exclude = False
            for exclude_link in EXCLUDE_SECTIONS:
                if possible_link.startswith(exclude_link):
                    exclude = True
                    break
            if not exclude:
                result.add(possible_link)
    return result
