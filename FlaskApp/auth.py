import jwt
import time
import requests
import json

def generate_access_token():
    '''
    Generates an access token using JWT
    '''
    pub_file = open("/home/vignesh/Desktop/FlaskApp/ds/rsa_public.txt", "rb")
    rsa_public = pub_file.read()
    pub_file.close()

    priv_file = open("/home/vignesh/Desktop/FlaskApp/ds/rsa_private.txt", "rb")
    rsa_private = priv_file.read()
    priv_file.close()

    start_time = int(time.time())
    end_time = start_time + 3600

    data = {
        "iss": "420edd88-3c32-4898-88b5-3f131cd48f50",
        "sub": "26f73d2a-71ee-403a-aa6c-4cb829ce9259",
        "aud": "account-d.docusign.com",
        "iat": start_time,
        "exp": end_time,
        "scope": "signature impersonation"
    }

    encoded_jwt = jwt.encode(data, rsa_private, algorithm="RS256").decode("utf-8")

    response_data = requests.post("https://account-d.docusign.com/oauth/token", data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": encoded_jwt})

    access_token = json.loads(response_data.content.decode("utf-8"))["access_token"]

    response_data_user = requests.get("https://account-d.docusign.com/oauth/userinfo", headers={"Authorization":"Bearer "+access_token})

    base_uri = json.loads(response_data_user.content)["accounts"][0]["base_uri"]

    account_id = json.loads(response_data_user.content)["accounts"][0]["account_id"]

    return access_token, base_uri, account_id