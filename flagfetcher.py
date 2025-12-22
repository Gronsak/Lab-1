import requests

ServerUrl = "http://10.3.10.104:3000"
s = requests.session()

class FlagToken:
    def __init__(self, token:str, expiresIn: int, verifyWithin: int, claimWithin: int):
        self.token = token
        self.expiresIn = expiresIn
        self.verifyWithin = verifyWithin
        self.claimWithin = claimWithin
        self.secret = ""
    def SetSecret(self, secret:str, claimWithin: int):
        self.secret = secret

def fetch_token() -> FlagToken:
    
    endpoint = "/api/token"
    rUrl = ServerUrl + endpoint
    r = s.post(rUrl)
    if not(r.status_code == 201):
        r.raise_for_status()
        raise ConnectionError()
    print(r.content.decode())
    json = r.json()

    tokenstr = json["token"]
    expiresIn = json["expiresInMs"]
    verifyWithin = json["verifyWithinMs"]
    claimWithin = json["claimWithinMs"]

    token = FlagToken(tokenstr,expiresIn,verifyWithin,claimWithin)
    return token

def verify_token(token: FlagToken) -> FlagToken:
    endpoint = "/api/verify"
    rUrl = ServerUrl + endpoint
    s.headers.update({"Authorization":"Bearer " + token.token})
    r = s.post(rUrl)
    if not(r.status_code == 200):
        r.raise_for_status()
        raise ConnectionError()
    
    print(r.content.decode())
    json = r.json()

    secret = json["secret"]
    claimWithin = json["claimWithinMs"]

    token.SetSecret(secret,claimWithin)
    return token

def fetch_flag(token: FlagToken) -> str:
    endpoint = "/api/flag"
    rUrl = ServerUrl + endpoint
    r = s.post(url=rUrl,json={"secret":token.secret})
    if not(r.status_code == 200):
        r.raise_for_status()
        raise ConnectionError()
    print(r.content.decode())
    json = r.json()

    flag = json["flag"]
    return flag

def main():
    print("Requesting token...")
    token = fetch_token()
    print("Verifying token...")
    token = verify_token(token)
    print("Requesting flag...")
    flag = fetch_flag(token)
    print("Flag retrived:")
    print(flag)

main()