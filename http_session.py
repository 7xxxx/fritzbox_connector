import requests
import hashlib
import keyring
import getpass


class HTTPSession:
    def __init__(self):
        self.set_fb_pass()
        self.sid = self.compute_sid_md5()

    def compute_sid_md5(self):
        """ Current FritzOS supports only MD5 Challenge Response, but will be changed soon to PBKDF2.
        """

        # get current challenge
        chal_get = requests.get("https://fritz.box/login_sid.lua?version=2", verify="fbcert.cer")

        # extract challange
        chal_start = chal_get.text.find("<Challenge>") + 11
        chal_end = chal_get.text.find("</Challenge>")
        chal = chal_get.text[chal_start:chal_end]

        # build response with challenge + password. Format of response is "challenge-md5(challenge-password)"
        response = chal + '-' + keyring.get_password("fritzbox", "fritzbox")
        response = response.encode("utf_16_le")
        md5_sum = hashlib.md5(response).hexdigest()
        response = chal + "-" + md5_sum

        # Get valid SID using the created response
        chal_post = requests.post("https://fritz.box/login_sid.lua?version=2",
                                  data={"username": None, "response": response},
                                  verify="fbcert.cer")

        # Extract and return the valid SID
        sid_start = chal_post.text.find("<SID>") + 5
        sid_end = chal_post.text.find("</SID>")
        return chal_post.text[sid_start:sid_end]

    def set_fb_pass(self):
        keyring.set_password("fritzbox", "fritzbox", getpass.getpass())

    def logout(self):
        payload = {"logout": "logout", "sid": self.sid}
        logout_post = requests.post("https://fritz.box/login_sid.lua?version=2",
                                    data=payload,
                                    verify="fbcert.cer")