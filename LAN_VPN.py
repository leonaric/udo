import requests
import webview
import time

# Example of a GET request
# response = requests.get('http://192.168.1.10:5000/items')
# print(response.json())

html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <style>
        *{
            position: relative;
            margin: 0;
            padding: 0;
            font-family: Impact, Haettenschweiler, 'Arial Narrow Bold', sans-serif;
        }
        body{
            width: 100vw;
            height: 100vh;
            background-color: rgb(23, 23, 23);
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 10px;
            box-sizing: border-box;
        }
        .main{
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 10px;
            box-sizing: border-box;
            border-radius: 5px;
            border: 1px solid rgba(255, 255, 255, 0.8);
            flex-direction: column;
        }
        .inputs{
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            box-sizing: border-box;
            border-radius: 10px;
            flex-direction: column;
        }
        .inputs .input{
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            box-sizing: border-box;
            border-radius: 10px;
        }
        p{
            font-size: 14px;
            text-align: right;
            margin-right: 10px;
            color: rgb(204, 229, 255);
            width: 40%;
        }
        input{
            width: 40%;
            height: fit-content;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid rgba(255, 255, 255, 0.8);
            background-color: rgba(255, 255, 255, 0.1);
            box-shadow: -1px -1px 10px rgba(0, 0, 0, 0.5);
            font-size: 14px;
            color: white;
        }
        .connect{
            width: fit-content;
            height: fit-content;
            display: flex;
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.8);
            border-radius: 10px;
            padding: 5px;
            margin-right: calc(40% - 50px);
            cursor: pointer;
        }
        .connect p{
            width: 40px;
            height: 30px;
            background-color: rgba(255, 112, 112, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.8);
            border-radius: 5px;
            margin-right: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            transition: all 0.5s cubic-bezier(0.455, 0.03, 0.515, 0.955);
        }
        .connect p[active="true"]{
            margin: 0;
            margin-left: 20px;
            border: 1px solid rgba(255, 255, 255, 0.8);
            background-color: rgba(105, 251, 166, 0.3);
        }
    </style>
    <div class="main">
        <div class="inputs">
            <div class="input">
                <p>Host IP-Address :</p>
                <input type="text" placeholder="eg. http,127.0.0.1" spellcheck="false">
            </div>
            <div class="input">
                <p>Authentication key :</p>
                <input type="text" placeholder="eg. QujTcqMML89nn" spellcheck="false">
            </div>
            <div class="input">
                <p>Click to connect :</p>
                <div class="connect"><p></p></div>
            </div>
        </div>
    </div>
</body>
<script>
    let connect = document.querySelector(".connect");
    let connectP = document.querySelector(".connect p");
    let inputs = document.querySelectorAll("input");
    connect.addEventListener("click",()=>{
        if(connectP.hasAttribute("active") && inputs[0].value.length > 0 && inputs[1].value.length > 0) {
            let request = pywebview.api.connectVpn("disc",inputs[0].value);
            connectP.removeAttribute("active");
            setTimeout(()=>{
                request.then((response)=>{
                    if (response == "Failed") {
                        console.log(response);
                    }else{
                        console.log("Internal error");
                    };
                });
            }, 5000);
        }else if(!connectP.hasAttribute("active") && inputs[0].value.length > 0 && inputs[1].value.length > 0){
            connectP.setAttribute("active", "true");
            let request = pywebview.api.connectVpn(inputs[1].value,inputs[0].value);
            setTimeout(()=>{
                request.then((response)=>{
                    if (response == "Connected") {
                        console.log("Connected");
                    }else if(response == "Failed"){
                        connectP.removeAttribute("active");
                    };
                });
            }, 5000);
        };
    });
</script>
</html>
"""

# Example of a POST request
def sendRequest(authkey, host, go_to):
    if go_to:
        hostAddr = host.split(",")
        hostprotocol = hostAddr[0]
        hostip = hostAddr[1]
        try:
            response = requests.post(f'{hostprotocol}://{hostip}:4444/api', json={'item': authkey}, verify=False)
            return response
        except Exception as e:
            print(e)

class Api:
    def __init__(self) -> None:
        self.VPN = True

    def connectVpn(self, auth, iphost):
        if self.VPN and auth != "disc":
            req = sendRequest(auth, iphost, self.VPN)
            time.sleep(1)
            print(req)
            if req:
                self.VPN = True
                print(f"Listening to host and port : {req}")
                return "Connected"
            else:
                # VPN = False
                print("Failed to connect")
                return "Failed"
        elif self.VPN and auth == "disc":
            req = sendRequest(auth, iphost, self.VPN)
            time.sleep(2)
            return "Failed"


if __name__ == "__main__":
    api = Api()
    app = webview.create_window("My VPN", html=html, js_api=api, width=350, height=250, frameless=True, resizable=False)
    webview.start(debug=False)