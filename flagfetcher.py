import requests
from datetime import datetime as time

ServerUrl = "http://10.3.10.104:3000"
s = requests.session()
start = time.now()

class FlagToken:
    def __init__(self, token:str, expiresIn: int, verifyWithin: int, claimWithin: int):
        self.token = token
        self.expiresIn = expiresIn
        self.verifyWithin = verifyWithin
        self.claimWithin = claimWithin
        self.deadline = 0
        self.secret = ""
    def SetSecret(self, secret:str, claimWithin: int, deadline: int):
        self.secret = secret
        self.claimWithin = claimWithin
        self.deadline = deadline

def fetch_token() -> FlagToken:
    endpoint = "/api/token"
    rUrl = ServerUrl + endpoint
    r = s.post(rUrl)
    if not(r.status_code == 201):
        r.raise_for_status()
        raise ConnectionError(f"Unexpected HTTP {r.status_code} respose")
    
    json = r.json()

    tokenstr = json["token"]
    expiresIn = json["expiresInMs"]
    verifyWithin = json["verifyWithinMs"]
    claimWithin = json["claimWithinMs"]

    token = FlagToken(tokenstr,expiresIn,verifyWithin,claimWithin)
    return token

def verify_token(token: FlagToken) -> FlagToken:
    if token.token == "" and token.secret == "":
        raise ValueError("Token and Secret is blank!")
    elif token.token == "":
        raise ValueError("Token is blank!")
    
    endpoint = "/api/verify"
    rUrl = ServerUrl + endpoint
    s.headers.update({"Authorization":"Bearer " + token.token})
    r = s.post(rUrl)
    if not(r.status_code == 200):
        r.raise_for_status()
        raise ConnectionError(f"Unexpected HTTP {r.status_code} respose")
    
    json = r.json()

    secret = json["secret"]
    claimWithin = json["claimWithinMs"]
    deadline = int(json["deadline"])

    token.SetSecret(secret,claimWithin,deadline)
    return token

def fetch_flag(token: FlagToken) -> str:
    if token.token == "" and token.secret == "":
        raise ValueError("Token and Secret is blank!")
    elif token.token == "":
        raise ValueError("Token is blank!")
    elif token.secret == "":
        raise ValueError("Secret is blank!")

    endpoint = "/api/flag"
    rUrl = ServerUrl + endpoint
    r = s.post(url=rUrl,json={"secret":token.secret})
    if not(r.status_code == 200):
        r.raise_for_status()
        raise ConnectionError(f"Unexpected HTTP {r.status_code} respose")
    json = r.json()

    flag = json["flag"]
    return flag

def running_time() -> float:
    return (time.now() - start).microseconds/1000

def main():
    print(r""" _______ _                 ___                  _                    ___     _____  
(_______) |               / __)        _       | |                  (___)   (_____) 
 _____  | | _____  ____ _| |__ _____ _| |_ ____| |__  _____  ____      _    _  __ _ 
|  ___) | |(____ |/ _  (_   __) ___ (_   _) ___)  _ \| ___ |/ ___)    | |  | |/ /| |
| |     | |/ ___ ( (_| | | |  | ____| | |( (___| | | | ____| |       _| |_ |   /_| |
|_|      \_)_____|\___ | |_|  |_____)  \__)____)_| |_|_____)_|      (_____|_)_____/ 
                 (_____|                                                            """)
    try:
        print(f"({running_time()}ms) Requesting token...")
        token = fetch_token()
        if token.token != "":
            print(f"({running_time()}ms) Token recieved!")
        else:
            print("No Token recieved, exiting!")
            return
        
        print(f"({running_time()}ms) Verifying token...")
        token = verify_token(token)
        if token.secret != "":
            print(f"({running_time()}ms) Token verified!")
        else:
            print("Token was not verified but no errors was raised, exiting!")
            return
        
        print(f"({running_time()}ms) Requesting flag...")
        flag = fetch_flag(token)
    except ConnectionError as e:
        print(e)
        return
    except requests.HTTPError as e:
        print(e)
        return
    except ValueError as e:
        print(e)
        return
    
    if flag != "":
        print(f"({running_time()}ms) Flag retrived:")
        print(flag)
    else:
        print("No flag retrived for unknown reason, exiting!")

if __name__ == "__main__":
    main()