import configparser
import json
import threading
import time

import requests
from flask import Flask, render_template, send_from_directory, flash, redirect, url_for

import PortCheck

app = Flask(__name__)
app.secret_key = '1234'

config = configparser.ConfigParser()
config.read("flask_Server.ini")

private_token = config['FLASKSERVER']['PRIVATE_TOKEN']
flask_Listen_Port = config['FLASKSERVER']['FlaskListenPort']
Dev_Server_IP = config['FLASKSERVER']['DevServerIP']
Dev_Server_Port = config['FLASKSERVER']['DevServerPort']
Qa_Server_IP = config['FLASKSERVER']['QaServerIP']
Qa_Server_Port = config['FLASKSERVER']['QaServerPort']

Dev_Server_Name = config['FLASKSERVER']['DevServerName']
Qa_Server_Name = config['FLASKSERVER']['QaServerName']

Dev_Sever_Tag = config['FLASKSERVER']['DevServerTag']
Qa_Sever_Tag = config['FLASKSERVER']['QaServerTag']

Login_Server_Port = config['LOGINSERVER']['LoginServerPort']
AdminTool_Server_Port = config['ADMINTOOLSERVER']['AdminToolServerPort']

IsBuildEnable = True
TestName = 'feature/gitlabBuild'
DevServerName = Dev_Server_Name
QaServerName = Qa_Server_Name
DevServerTag = Dev_Sever_Tag
QaServerTag = Qa_Sever_Tag

portChecker = PortCheck.PortChecker()

def Process(servername, machine_value, extra_variables):
    global IsBuildEnable

    headers = {'PRIVATE-TOKEN': private_token, "Content-Type": "application/json"}

    variables = ', '.join([json.dumps({"key": k, "value": v}) for k, v in extra_variables.items()])
    variables += ', ' + json.dumps({"key": "Machine", "value": machine_value})

    # data를 JSON 문자열로 생성
    data = '{"ref": "' + servername + '", "variables": [' + variables + ']}'

    res = requests.post("http://anotherworld.internal.dev1.com:9080/api/v4/projects/2/pipeline", data=data, headers=headers)
    bodyJson = res.json()
    pipelineID = bodyJson["id"]

    while True:
        reqUrl = "http://anotherworld.internal.dev1.com:9080/api/v4/projects/2/pipelines/%s" % pipelineID
        print(reqUrl)
        get = requests.get(reqUrl, headers=headers)
        getJson = get.json()
        print(getJson)
        getStatus = getJson["status"]
        if getStatus == "failed":
            IsBuildEnable = True
            print("Login Build failed")
            return False
        elif getStatus == "success":
            print("Login Build success")
            break
        time.sleep(10)

    IsBuildEnable = True
    return True

def initiate_build_process(server_name, server_tag, variables, flash_message, redirect_endpoint):
    global IsBuildEnable

    if not IsBuildEnable:
        flash(flash_message)
        return redirect(url_for(redirect_endpoint))
    else:
        IsBuildEnable = False
        worker = threading.Thread(target=Process, args=(server_name, server_tag, variables))
        worker.daemon = True
        worker.start()
        return redirect(url_for(redirect_endpoint))

@app.route("/devAllBuild", methods=["GET", "POST"])
def dev_all_build():
    global DevServerName, DevServerTag
    return initiate_build_process(DevServerName, DevServerTag, {"BUILD": "true", "Restart": "true", "GameServer": "true", "AdminToolServer": "true", "LoginServer": "true"}, "dev all build processing..", 'dev_home')

@app.route("/qaAllBuild", methods=["GET", "POST"])
def qa_all_build():
    global QaServerName, QaServerTag
    return initiate_build_process(QaServerName, QaServerTag, {"BUILD": "true", "Restart": "true", "GameServer": "true", "AdminToolServer": "true", "LoginServer": "true"}, "qa all build processing..", 'qa_home')

@app.route("/devAllRestart", methods=["GET", "POST"])
def dev_all_restart():
    global DevServerName, DevServerTag
    return initiate_build_process(DevServerName, DevServerTag, {"BUILD": "false", "Restart": "true", "GameServer": "true", "AdminToolServer": "true", "LoginServer": "true"}, "dev all restarting..", 'dev_home')

@app.route("/qaAllRestart", methods=["GET", "POST"])
def qa_all_restart():
    global QaServerName, QaServerTag
    return initiate_build_process(QaServerName, QaServerTag, {"BUILD": "false", "Restart": "true", "GameServer": "true", "AdminToolServer": "true", "LoginServer": "true"}, "qa all restarting..", 'qa_home')

@app.route("/devOnlyBuild", methods=["GET", "POST"])
def dev_build():
    global DevServerName, DevServerTag
    return initiate_build_process(DevServerName, DevServerTag, {"BUILD": "true", "Restart": "false", "GameServer": "true"}, "dev only build processing..", 'dev_home')

@app.route("/qaOnlyBuild", methods=["GET", "POST"])
def qa_build():
    global QaServerName, QaServerTag
    return initiate_build_process(QaServerName, QaServerTag, {"BUILD": "true", "Restart": "false", "GameServer": "true"}, "qa only build processing..", 'qa_home')

@app.route("/devBuild", methods=["GET", "POST"])
def dev_build_and_restart():
    global DevServerName, DevServerTag
    return initiate_build_process(DevServerName, DevServerTag, {"BUILD": "true", "Restart": "true", "GameServer": "true"}, "dev build restart processing...", 'dev_home')

@app.route("/qaBuild", methods=["GET", "POST"])
def qa_build_and_restart():
    global QaServerName, QaServerTag
    return initiate_build_process(QaServerName, QaServerTag, {"BUILD": "true", "Restart": "true", "GameServer": "true"}, "qa build restart processing...", 'qa_home')

@app.route("/devRestart", methods=["GET", "POST"])
def dev_restart():
    global DevServerName, DevServerTag
    return initiate_build_process(DevServerName, DevServerTag, {"BUILD": "false", "Restart": "true", "GameServer": "true"}, "dev restart processing..", 'dev_home')

@app.route("/qaRestart", methods=["GET", "POST"])
def qa_restart():
    global QaServerName, QaServerTag
    return initiate_build_process(QaServerName, QaServerTag, {"BUILD": "false", "Restart": "true", "GameServer": "true"}, "qa restart processing..", 'qa_home')

@app.route("/devLoginBuild", methods=["GET", "POST"])
def dev_login_build():
    global DevServerName, DevServerTag
    return initiate_build_process(DevServerName, DevServerTag, {"BUILD": "true", "Restart": "true", "LoginServer": "true"}, "dev login restarting..", 'qa_home')

@app.route("/qaLoginBuild", methods=["GET", "POST"])
def qa_login_build():
    global QaServerName, QaServerTag
    return initiate_build_process(QaServerName, QaServerTag, {"BUILD": "true", "Restart": "true", "LoginServer": "true"}, "qa login restarting..", 'qa_home')
0
@app.route("/devLoginRestart", methods=["GET", "POST"])
def dev_login_restart():
    global DevServerName, DevServerTag
    return initiate_build_process(DevServerName, DevServerTag, {"BUILD": "false", "Restart": "true", "LoginServer": "true"}, "dev login restarting..", 'qa_home')

@app.route("/qaLoginRestart", methods=["GET", "POST"])
def qa_login_restart():
    global QaServerName, QaServerTag
    return initiate_build_process(QaServerName, QaServerTag, {"BUILD": "false", "Restart": "true", "LoginServer": "true"}, "qa login restarting..", 'qa_home')

@app.route("/devAdminBuild", methods=["GET", "POST"])
def dev_admin_build():
    global DevServerName, DevServerTag
    return initiate_build_process(DevServerName, DevServerTag, {"BUILD": "true", "Restart": "true", "AdminToolServer": "true"}, "dev admin building..", 'qa_home')

@app.route("/qaAdminBuild", methods=["GET", "POST"])
def qa_admin_build():
    global QaServerName, QaServerTag
    return initiate_build_process(QaServerName, QaServerTag, {"BUILD": "true", "Restart": "true", "AdminToolServer": "true"}, "qa admin building..", 'qa_home')

@app.route("/devAdminRestart", methods=["GET", "POST"])
def dev_admin_restart():
    global DevServerName, DevServerTag
    return initiate_build_process(DevServerName, DevServerTag, {"BUILD": "false", "Restart": "true", "AdminToolServer": "true"}, "dev admin restarting..", 'qa_home')

@app.route("/qaAdminRestart", methods=["GET", "POST"])
def qa_admin_restart():
    global QaServerName, QaServerTag
    return initiate_build_process(QaServerName, QaServerTag, {"BUILD": "false", "Restart": "true", "AdminToolServer": "true"}, "qa admin restarting..", 'qa_home')

@app.route("/")
@app.route("/dev")
def dev_home():
    dev_game_server_live = portChecker.GameServerCheck(Dev_Server_IP, int(Dev_Server_Port))
    dev_login_server_live = portChecker.ToolServerCheck(Dev_Server_IP, int(Login_Server_Port))
    dev_admin_server_live = portChecker.ToolServerCheck(Dev_Server_IP, int(AdminTool_Server_Port))

    return render_template("dev.html",
                           IsBuildEnable=IsBuildEnable,
                           value=dev_game_server_live,
                           ls_value=dev_login_server_live,
                           am_value=dev_admin_server_live)

@app.route("/qa")
def qa_home():
    qa_game_server_live = portChecker.GameServerCheck(Qa_Server_IP, int(Qa_Server_Port))
    qa_login_server_live = portChecker.ToolServerCheck(Qa_Server_IP, int(Login_Server_Port))
    qa_admin_server_live = portChecker.ToolServerCheck(Qa_Server_IP, int(AdminTool_Server_Port))
    return render_template("qa.html",
                           IsBuildEnable=IsBuildEnable,
                           value=qa_game_server_live,
                           ls_value=qa_login_server_live,
                           am_value=qa_admin_server_live)

@app.route('/<path:name>')
def start(name):
    return send_from_directory('templates', name)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(flask_Listen_Port), threaded=True)
