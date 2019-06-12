from flask import Flask, session, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pymysql
import json
import time
import os
import traceback
from flask_cors import CORS
from models import db,User,Workspace,WorkspaceMembership,WorkspaceInvitation
from models import Administrator,Channel,ChannelMembership,ChannelInvitation,Message

app = Flask(__name__)
app.secret_key = 'a3f:4AD3/3yXR~XHH!jm[s]daLWX/,?RT'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:1234@localhost:3306/snickr?charset=utf8"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

CORS(app, resources=r'/*')

conn = pymysql.connect("localhost", "root", "1234", "snickr", 3306)

'''
cursor = conn.cursor()
sql = "Select * from User,Workspace where User.uid = Workspace.creatorid"
cursor.execute(sql)
conn.commit()
for row in cursor.fetchall():
    print(row)
print('Total', cursor.rowcount)
'''


# Control
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return str(session)
    if request.method == 'POST':
        return str(session)


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        if User.query.filter_by(email=data['uemail']).first() is None:
            db.session.add(
                User(data['uname'], data['nickname'], data['upassword'], data['uemail']))
            db.session.commit()
            user = User.query.filter_by(email=data['uemail']).first()
            session[data['uemail']] = user.uid
            return jsonify({'status': 1, 'message': 'Register successfully!'})
        else:
            return jsonify({'status': 0, 'message': 'Email already exists!'})


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        #session.pop(data['uemail'], None)
        if data['uemail'] in session:
            return jsonify({'status': 0, 'message': 'The same user cannot log in repeatedly!'})
        else:
            user = User.query.filter_by(email=data['uemail']).first()
            if user:
                if data['upassword'] == user.upassword:
                    #session.permanent = True
                    session[data['uemail']] = user.uid
                    return jsonify({'status': 1, 'message': 'Login Successfully!'})
                else:
                    return jsonify({'status': 0, 'message': 'Incorrect Password!'})
            else:
                return jsonify({'status': 0, 'message': 'User haven\'t register yet!'})

@app.route('/main', methods=['POST'])
def listWorkspace():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        uid = [user.uid for user in User.query.filter_by(email=data['uemail']).all()]
        wids = []
        for u in uid:
            wids += [workspacemembership.wid for workspacemembership in WorkspaceMembership.query.filter_by(uid=u).all()]

        workspaces = []
        wlist = []

        for wid in wids:
            workspaces = Workspace.query.filter_by(wid=wid).first()
            wlist.append(workspaces.to_json())

        return jsonify({'status': 1,'wlist':wlist})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})

@app.route('/workspace', methods=['POST'])
def listChannelandUser():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        loginid = User.query.filter_by(email=data['uemail']).first().uid
        loginchannel = [loginc.cid for loginc in ChannelMembership.query.filter_by(uid=loginid).all()]

        cids = [channel.cid for channel in Channel.query.filter_by(wid=data['wid']).all()]
        uids = [workspacemembership.uid for workspacemembership in WorkspaceMembership.query.filter_by(wid=data['wid']).all()]

        clist = []
        for cid in cids:
            if cid in loginchannel:
                channels = Channel.query.filter_by(cid=cid).first()
                clist.append(channels.to_json())

        ulist = []
        statuslist = []

        workspace = Workspace.query.filter_by(wid=data['wid']).first()
        admins = [ad.uid for ad in Administrator.query.filter_by(wid=data['wid']).all()]

        for uid in uids:
            users = User.query.filter_by(uid=uid).first()
            ulist.append(users.to_json())
            if(workspace.creatorid == users.uid):
                statuslist.append(0)
            elif users.uid in admins:
                statuslist.append(1)
            else:
                statuslist.append(2)

        user = User.query.filter_by(email=data['uemail']).first()
        if(workspace.creatorid == user.uid):
            creator = 0
        elif user.uid in admins:
            creator = 1
        else:
            creator = 2
        return jsonify({'status': 1, 'clist': clist, 'ulist':ulist, 'creator':creator, 'statuslist':statuslist})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})


@app.route('/channel', methods=['POST'])
def listMessage():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        wid = Channel.query.filter_by(cid=data['cid']).first().wid
        wuser = [wm.uid for wm in WorkspaceMembership.query.filter_by(wid=wid).all()]
        users = [cm.uid for cm in ChannelMembership.query.filter_by(cid=data['cid']).all()]
        userlist = []
        for u in users:
            user = User.query.filter_by(uid=u).first().to_json()
            userlist.append(user)

        inviteelist = []
        for wu in wuser:
            if wu not in users:
                user = User.query.filter_by(uid=wu).first()
                inviteelist.append(user.to_json())

        messages = Message.query.filter_by(cid=data['cid']).all()
        senderlist = []
        mlist = []
        for m in messages:
            mlist.append(m.to_json())
            sender = User.query.filter_by(uid=m.senderid).first()
            senderlist.append(sender.to_json())

        channel = Channel.query.filter_by(cid=data['cid']).first().to_json()
        return jsonify({'status': 1, 'senderlist':senderlist,'mlist':mlist,'inviteelist':inviteelist,'channel':channel,'userlist':userlist})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})

@app.route('/send', methods=['POST'])
def sendmessage():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        uid = User.query.filter_by(email=data['uemail']).first().uid
        currenttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db.session.add(
            Message(uid, data['cid'], data['content'], currenttime))
        db.session.commit()
        return jsonify({'status': 1})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})

@app.route('/assignadmin', methods=['POST'])
def assign():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        db.session.add(Administrator(data['uid'], data['wid']))
        db.session.commit()
        return jsonify({'status': 1, 'message':'Assign Success!'})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})

@app.route('/removeadmin', methods=['POST'])
def remove():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        Administrator.query.filter(Administrator.wid==data['wid'],Administrator.uid==data['uid']).delete()
        #db.session.delete(Administrator(data['uid'], data['wid']))
        db.session.commit()
        return jsonify({'status': 1, 'message':'Remove Success!'})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})


@app.route('/wdeleteuser', methods=['POST'])
def delete():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        WorkspaceMembership.query.filter(WorkspaceMembership.wid==data['wid'], WorkspaceMembership.uid==data['uid']).delete()
        db.session.commit()
        return jsonify({'status': 1, 'message': 'Delete Success!'})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})

@app.route('/showinvitation', methods=['POST'])
def showinvitation():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        winvitations = WorkspaceInvitation.query.filter(WorkspaceInvitation.winviteeemail==data['uemail'],WorkspaceInvitation.wstatus=='pending').all()
        winvitationlist = []
        winvitorlist = []
        workspacelist = []
        for wi in winvitations:
            winvitor = User.query.filter_by(uid=wi.winvitorid).first()
            winvitorlist.append(winvitor.to_json())
            workspace = Workspace.query.filter_by(wid=wi.wid).first()
            workspacelist.append(workspace.to_json())
            winvitationlist.append(wi.to_json())

        uid = User.query.filter_by(email=data['uemail']).first().uid
        cinvitations = ChannelInvitation.query.filter(ChannelInvitation.cinviteeid == uid,
                                                 ChannelInvitation.cstatus == 'pending').all()
        cinvitationlist = []
        cinvitorlist = []
        channellist = []
        for ci in cinvitations:
            cinvitor = User.query.filter_by(uid=ci.cinvitorid).first()
            cinvitorlist.append(cinvitor.to_json())
            channel = Channel.query.filter_by(cid=ci.cid).first()
            channellist.append(channel.to_json())
            cinvitationlist.append(ci.to_json())

        return jsonify({'status': 1, 'winvitorlist': winvitorlist, 'workspacelist': workspacelist,'winvitationlist':winvitationlist,
                    'cinvitorlist': cinvitorlist, 'channellist': channellist,'cinvitationlist':cinvitationlist})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})


@app.route('/WAccept', methods=['POST'])
def waccept():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        winvitation = WorkspaceInvitation.query.filter(WorkspaceInvitation.wid==data['wid'], WorkspaceInvitation.winviteeemail==data['uemail']).first()
        winvitation.wstatus = 'accept'
        db.session.commit()
        uid = User.query.filter_by(email=data['uemail']).first().uid
        wjointime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db.session.add(WorkspaceMembership(uid, data['wid'],wjointime))
        db.session.commit()
        return jsonify({'status':1, 'message':"Accepted!"})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})

@app.route('/WReject', methods=['POST'])
def wreject():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        winvitation = WorkspaceInvitation.query.filter(WorkspaceInvitation.wid==data['wid'], WorkspaceInvitation.winviteeemail==data['uemail']).first()
        winvitation.wstatus = 'reject'
        db.session.commit()
        return jsonify({'status':1, 'message':"Rejected!"})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})


@app.route('/CAccept', methods=['POST'])
def caccept():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        cinvitation = ChannelInvitation.query.filter(ChannelInvitation.cid == data['cid'],
                                                     ChannelInvitation.cinviteeid == data['uid']).first()
        cinvitation.cstatus = 'accept'
        db.session.commit()
        cjointime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db.session.add(ChannelMembership(data['uid'], data['cid'], cjointime))
        db.session.commit()
        return jsonify({'status': 1, 'message': "Accepted!"})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})


@app.route('/CReject', methods=['POST'])
def creject():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        cinvitation = ChannelInvitation.query.filter(ChannelInvitation.cid == data['cid'],
                                                     ChannelInvitation.cinviteeid == data['uid']).first()
        cinvitation.cstatus = 'reject'
        db.session.commit()
        return jsonify({'status': 1, 'message': "Rejected!"})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})


@app.route('/search', methods=['POST'])
def search():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        uid = User.query.filter_by(email=data['uemail']).first().uid
        channels = ChannelMembership.query.filter_by(uid=uid).all()
        messagelist = []
        cnamelist = []
        ulist = []
        for c in channels:
            messages = Message.query.filter(Message.cid == c.cid, Message.content.like('%' + data['key'] + '%')).all()
            for m in messages:
                messagelist.append(m.to_json())
                cname = Channel.query.filter_by(cid=m.cid).first().cname
                cnamelist.append(cname)
                sender = User.query.filter_by(uid=m.senderid).first().nickname
                ulist.append(sender)
        return jsonify({'status': 1, 'ulist': ulist, 'cnamelist': cnamelist, 'messagelist': messagelist})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})


@app.route('/createworkspace', methods=['POST'])
def createw():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        uid = User.query.filter_by(email=data['uemail']).first().uid
        createtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db.session.add(
            Workspace(data['wname'], uid, data['wdes'], createtime))
        db.session.commit()
        wid = Workspace.query.filter(Workspace.wname == data['wname'], Workspace.wtime == createtime).first().wid
        db.session.add(WorkspaceMembership(uid, wid, createtime))
        db.session.commit()
        return jsonify({'status': 1, 'message': 'Create successfully!'})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})


@app.route('/createchannel', methods=['POST'])
def createc():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        uid = User.query.filter_by(email=data['uemail']).first().uid
        createtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db.session.add(
            Channel(uid, data['wid'], data['ctype'], data['cname'], createtime)
        )
        db.session.commit()
        cid = Channel.query.filter(Channel.creatorid == uid, Channel.wid == data['wid'],
                                   Channel.ctime == createtime).first().cid
        db.session.add(
            ChannelMembership(uid, cid, createtime)
        )
        db.session.commit()
        return jsonify({'status': 1, 'message': 'Create successfully!'})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})


@app.route('/inviteworkspace', methods=['POST'])
def invitew():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        uid = User.query.filter_by(email=data['uemail']).first().uid
        invitetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        inviteelist = data['invitee'].split('\n')
        for invitee in inviteelist:
            db.session.add(
                WorkspaceInvitation(uid, data['wid'], invitee, invitetime, 'pending')
            )
            db.session.commit()
        return jsonify({'status': 1, 'message': 'Invite successfully!'})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})


@app.route('/invitechannel', methods=['POST'])
def invitec():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        uid = User.query.filter_by(email=data['uemail']).first().uid
        invitetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        inviteelist = data['invitee'].split(';')
        inviteelist.pop()
        print(inviteelist)
        for invitee in inviteelist:
            db.session.add(
                ChannelInvitation(uid, data['cid'], invitee, invitetime, 'pending')
            )
            db.session.commit()
        return jsonify({'status': 1, 'message': 'Invite successfully!'})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})


@app.route('/profile', methods=['POST'])
def profile():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        user = User.query.filter_by(email=data['uemail']).first()
        return jsonify({'status': 1, 'name': user.uname, 'nickname': user.nickname})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})


@app.route('/nickname', methods=['POST'])
def nickname():
    data = json.loads(request.get_data())
    if data['uemail'] in session:
        user = User.query.filter_by(email=data['uemail']).first()
        user.nickname = data['nick']
        db.session.commit()
        return jsonify({'status': 1, 'message': 'Change successfully!'})
    else:
        return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})


@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        if data['uemail'] in session:
            session.pop(data['uemail'], None)
            return jsonify({'status': 1, 'message': 'Logout Successfully!'})
        else:
            return jsonify({'status': 0, 'message': 'User haven\'t login yet!'})


if __name__ == '__main__':
    app.run()
