import http_session

def main():
    session = http_session.HTTPSession()
    session.logout()


if __name__ == '__main__':
    main()
