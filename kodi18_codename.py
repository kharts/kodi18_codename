BASE_URL = "http://forum.kodi.tv/showthread.php?tid=282241&page="
LOGIN_URL = "http://forum.kodi.tv/member.php"
LAST_PAGE = 45
TOP_RESULTS_NUMBER = 10
SKIP_WORDS = ["L"]


from getpass import getpass
from bs4 import BeautifulSoup
import requests
import pandas as pd


def main():
    # type: () -> None

    session = login()
    words = {}
    for i in range(1, LAST_PAGE+1):
        print "Processing page number {} from {}".format(i, LAST_PAGE)
        url = "{}{}".format(BASE_URL, i)
        process_page(url, words, session)

    df = pd.DataFrame({
        "name": words.keys(),
        "mentions": words.values()
    })
    df = df.sort_values(by="mentions", ascending=False)
    df = df.head(TOP_RESULTS_NUMBER)
    df = df.reset_index(drop=True)
    print df


def login():
    # type: () -> CookieJar
    """
    Perform login and return cookie
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
    # type: (str, words, requests.session)

    response = session.get(page)
    # print "code", response.status_code
    bs = BeautifulSoup(response.text, "html.parser", from_encoding="utf-8")
    divs = bs.find_all("div", attrs={"class": "post-body"})
    for div in divs:
        text = div.text.encode("utf-8")
        tokens = text.split()
        for token in tokens:
            if token.startswith("L"):
                if token in SKIP_WORDS:
                    continue
                if token in words:
                    words[token] += 1
                else:
                    words[token] = 1


if __name__ == '__main__':
    main()