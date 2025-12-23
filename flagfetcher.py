import getopt, sys
import requests
import pyfiglet
from datetime import datetime as time

args = sys.argv[1:]
options = "hu:"
longOptions = ["help", "url"]

banner = pyfiglet.figlet_format("/Flagfetcher/", font="rounded")
ServerUrl = "http://10.3.10.104:3000"
s = requests.session()
start = time.now()

class FlagToken:
    def __init__(self, token:str):
        self.token = token
        #self.expiresIn = expiresIn
        #self.verifyWithin = verifyWithin
        #self.claimWithin = claimWithin
        #self.deadline = int(time.now().timestamp()) + (verifyWithin + claimWithin)/1000
        self.secret = ""
    def SetSecret(self, secret:str):
        self.secret = secret
        #self.claimWithin = claimWithin
        #self.deadline = deadline

def print_help():
    print(f"""
Flagfetcher is a very basic app to get a flag using a predefined API
Default API server URl is {ServerUrl}

Options:
    -h, --help: Show this help message.
    -u, --url: Set API Server URL (-u "http://www.example.com")""")
def fetch_token() -> FlagToken:
    endpoint = "/api/token"
    rUrl = ServerUrl + endpoint
    r = s.post(rUrl)
    if not(r.status_code == 201):
        r.raise_for_status()
        raise ConnectionError(f"Unexpected HTTP {r.status_code} respose")
    
    json = r.json()

    tokenstr = json["token"]
    # expiresIn = json["expiresInMs"]
    # verifyWithin = json["verifyWithinMs"]
    # claimWithin = json["claimWithinMs"]

    token = FlagToken(tokenstr)
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
    # claimWithin = json["claimWithinMs"]
    # deadline = int(json["deadline"])

    token.SetSecret(secret)
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
    print(banner)
    print(f"Target URL: {ServerUrl}\n")
    try:
        print(f"({running_time()}ms) Requesting token...")
        token = fetch_token()
        if token.token != "":
            print(f"({running_time()}ms) Token recieved!")
        else:
            print("No Token recieved, exiting!")
            sys.exit()
        
        print(f"({running_time()}ms) Verifying token...")
        token = verify_token(token)
        if token.secret != "":
            print(f"({running_time()}ms) Token verified!")
        else:
            print("Token was not verified but no errors was raised, exiting!")
            sys.exit()
        
        print(f"({running_time()}ms) Requesting flag...")
        flag = fetch_flag(token)
    except ConnectionError as e:
        print(e)
        sys.exit()
    except requests.HTTPError as e:
        print(e)
        sys.exit()
    except ValueError as e:
        print(e)
        sys.exit()
    
    if flag != "":
        print(f"({running_time()}ms) Flag retrived: {flag}")
    else:
        print("No flag retrived for unknown reason, exiting!")


try:
    arguments, values = getopt.getopt(args, options, longOptions)
    for arg, val in arguments:
        if arg in ("-h", "--help"):
            print_help()
            sys.exit()
        elif arg in ("-u", "--url"):
            ServerUrl = val.strip("/")
            
except getopt.error as e:
    print(str(e))

if __name__ == "__main__":
    main()