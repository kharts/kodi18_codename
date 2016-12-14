"""
kodi18_codename.py - script for counting votes for new Kodi version codename

Parses pages of this forum thread:
http://forum.kodi.tv/showthread.php?tid=282241
and counts mentions for each suggestion.

Dependencies:
- BeautifulSoup;
- requests;
- pandas

Author: kharts
https://github.com/kharts/kodi18_codename

License: GPL 2
"""

BASE_URL = "http://forum.kodi.tv/showthread.php?tid=282241&page="
LOGIN_URL = "http://forum.kodi.tv/member.php"
TOP_RESULTS_NUMBER = 10
SKIP_WORDS = ["L"]


from getpass import getpass
from bs4 import BeautifulSoup
import requests
import pandas as pd


def main():
    # type: () -> None

    # session = login()
    session = requests.session()
    words = {}
    i = 1
    while True:
        print "Processing page number {}".format(i)
        url = "{}{}".format(BASE_URL, i)
        if not process_page(url, words, session):
            break
        i += 1

    df = pd.DataFrame({
        "name": words.keys(),
        "mentions": words.values()
    })
    df = df.sort_values(by="mentions", ascending=False)
    df = df.head(TOP_RESULTS_NUMBER)
    df = df.reset_index(drop=True)
    print df


def login():
    # type: () -> requests.session
    """
    Perform login and return session
    """

    username = raw_input("Enter your forum username:")
    password = getpass("Enter your forum password:")

    session = requests.session()
    session.post(LOGIN_URL, data={
        "action": "do_login",
        "url": "http://forum.kodi.tv/index.php",
        "quick_login": "1",
        "quick_username": username,
        "quick_password": password,
        "submit": "Login",
        "quick_remember": "yes"
    })
    return session


def process_page(page, words, session):
    # type: (str, dict, requests.session) -> bool

    response = session.get(page)
    bs = BeautifulSoup(response.text, "html.parser", from_encoding="utf-8")
    if bs.find("a", attrs={"class": "pagination_next"}):
        result = True
    else:
        result = False
    divs = bs.find_all("div", attrs={"class": "post-body"})
    for div in divs:
        text = div.text.encode("utf-8")
        tokens = text.split()
        # select only unique words
        for token in set(tokens):
            if token.startswith("L"):
                if token in SKIP_WORDS:
                    continue
                if token in words:
                    words[token] += 1
                else:
                    words[token] = 1
    return result


if __name__ == '__main__':
    main()