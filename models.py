from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, ENUM
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'User'

    uid = db.Column(INTEGER(11), primary_key=True, autoincrement=True)
    uname = db.Column(VARCHAR(50), nullable=False)
    nickname = db.Column(VARCHAR(50), nullable=True)
    upassword = db.Column(VARCHAR(50), nullable=False)
    email = db.Column(VARCHAR(50), nullable=False)

    create_workspace = db.relationship('Workspace',backref = 'User')
    member_workspace_user = db.relationship('WorkspaceMembership',backref = 'User')
    admin_workspace_user = db.relationship('Administrator',backref = 'User')
    member_channel_user = db.relationship('ChannelMembership',backref = 'User')
    invitee_channel = db.relationship('ChannelInvitation',backref = 'User')

    def __init__(self,uname,nickname,upassword,email):
        self.uname=uname
        self.nickname=nickname
        self.upassword=upassword
        self.email=email

    def to_json(self):
        json_comment = {

            'uid':self.uid,
            'uname':self.uname,
            'nickname':self.nickname,
            'upassword':self.upassword,
            'email':self.email
        }
        return json_comment

class Workspace(db.Model):
    __tablename__ = 'Workspace'

    wid = db.Column(INTEGER(11), primary_key=True, autoincrement=True)
    wname = db.Column(VARCHAR(50), nullable=False)
    creatorid = db.Column(ForeignKey('User.uid'))
    description = db.Column(VARCHAR(200), nullable=True)
    wtime = db.Column(DateTime,nullable=False)

    member_workspace = db.relationship('WorkspaceMembership',backref = 'Workspace')
    admin_workspace = db.relationship('Administrator',backref = 'Workspace')

    def __init__(self,wname,creatorid,description,wtime):
        self.wname = wname
        self.creatorid = creatorid
        self.description = description
        self.wtime = wtime

    def to_json(self):
        json_comment = {
            'wid':self.wid,
            'wname':self.wname,
            'creatorid':self.creatorid,
            'description':self.description,
            'wtime':self.wtime
        }
        return json_comment

class WorkspaceMembership(db.Model):
    __tablename__ = 'WorkspaceMembership'

    uid = db.Column(ForeignKey('User.uid'),primary_key=True)
    wid = db.Column(ForeignKey('Workspace.wid'), primary_key=True)
    wjointime = db.Column(DateTime,nullable=False)

    def __init__(self,uid,wid,wjointime):
        self.uid = uid
        self.wid = wid
        self.wjointime = wjointime

    def to_json(self):
        json_comment = {
            'uid':self.uid,
            'wid':self.wid,
            'wjointime':self.wjointime
        }
        return json_comment

class WorkspaceInvitation(db.Model):
    __tablename__ = 'WorkspaceInvitation'

    winvitorid = db.Column(ForeignKey('WorkspaceMembership.uid'),primary_key=True,nullable=False)
    wid = db.Column(ForeignKey('WorkspaceMembership.wid'),primary_key=True,nullable=False)
    winviteeemail = db.Column(VARCHAR(50),primary_key=True,nullable=False)
    winvitetime = db.Column(DateTime,nullable=False)
    wstatus = db.Column(ENUM('accept','reject','pending'))
    #invite_workspace = db.relationship('WorkspaceInvitation', backref='WorkspaceMembership',
    #                                  primaryjoin=(WorkspaceMembership.uid == winvitorid))

    def __init__(self,winvitorid,wid,winviteeemail,winvitetime,wstatus):
        self.winvitorid = winvitorid
        self.wid = wid
        self.winviteeemail = winviteeemail
        self.winvitetime = winvitetime
        self.wstatus = wstatus

    def to_json(self):
        json_comment = {
            'winvitorid':self.winvitorid,
            'wid':self.wid,
            'winviteeemail':self.winviteeemail,
            'winvitetime':self.winvitetime,
            'wstatus':self.wstatus
        }
        return json_comment

class Administrator(db.Model):
    __tablename__ = 'Administrator'

    uid = db.Column(ForeignKey('User.uid'),primary_key=True)
    wid = db.Column(ForeignKey('Workspace.wid'),primary_key=True)

    def __init__(self,uid,wid):
        self.uid = uid
        self.wid = wid

    def to_json(self):
        json_comment = {
            'uid':self.uid,
            'wid':self.wid
        }
        return json_comment

class Channel(db.Model):
    __tablename__ = 'Channel'

    cid = db.Column(INTEGER(11),primary_key=True,autoincrement=True)
    creatorid = db.Column(ForeignKey('WorkspaceMembership.uid'))
    wid = db.Column(ForeignKey('WorkspaceMembership.wid'))
    ctype = db.Column(ENUM('public','private','direct'))
    cname = db.Column(VARCHAR(50),nullable=False)
    ctime = db.Column(DateTime,nullable=False)
    #create_channel = db.relationship('Channel', backref='WorkspaceMembership',
    #                               primaryjoin=(creatorid==WorkspaceMembership.uid))
    member_channel = db.relationship('ChannelMembership',backref = 'Channel')
    def __init__(self,creatorid,wid,ctype,cname,ctime):
        self.creatorid = creatorid
        self.wid = wid
        self.ctype = ctype
        self.cname = cname
        self.ctime = ctime

    def to_json(self):
        json_comment = {
            'cid':self.cid,
            'creatorid':self.creatorid,
            'wid':self.wid,
            'ctype':self.ctype,
            'cname':self.cname,
            'ctime':self.ctime
        }
        return json_comment

class ChannelMembership(db.Model):
    __tablename__ = 'ChannelMembership'

    uid = db.Column(ForeignKey('User.uid'),primary_key=True)
    cid = db.Column(ForeignKey('Channel.cid'),primary_key=True)
    cjointime = db.Column(DateTime,nullable=False)

    #invite_channel = db.relationship('ChannelInvitation', backref='ChannelMembership')
    #send_message = db.relationship('Message',backref='ChannelMembership')

    def __init__(self,uid,cid,cjointime):
        self.uid = uid
        self.cid = cid
        self.cjointime = cjointime

    def to_json(self):
        json_comment = {
            'uid':self.uid,
            'cid':self.cid,
            'cjointime':self.cjointime
        }
        return json_comment

class ChannelInvitation(db.Model):
    __tablename__ = 'ChannelInvitation'

    cinvitorid = db.Column(ForeignKey('ChannelMembership.uid'),primary_key=True)
    cid = db.Column(ForeignKey('ChannelMembership.cid'),primary_key=True)
    cinviteeid = db.Column(ForeignKey('User.uid'),primary_key=True)
    cinvitetime = db.Column(DateTime)
    cstatus = db.Column(ENUM('accept','reject','pending'))

    def __init__(self,cinvitorid,cid,cinviteeid,cinvitetime,cstatus):
        self.cinvitorid = cinvitorid
        self.cid = cid
        self.cinviteeid = cinviteeid
        self.cinvitetime = cinvitetime
        self.cstatus = cstatus

    def to_json(self):
        json_comment = {
            'cinvitorid':self.cinvitorid,
            'cid':self.cid,
            'cinviteeid':self.cinviteeid,
            'cinvitetime':self.cinvitetime,
            'cstatus':self.cstatus
        }
        return json_comment

class Message(db.Model):
    __tablename__ = 'Message'

    mid = db.Column(INTEGER(11),primary_key=True,autoincrement=True)
    senderid = db.Column(ForeignKey('ChannelMembership.uid'))
    cid = db.Column(ForeignKey('ChannelMembership.cid'))
    content = db.Column(VARCHAR(500),nullable=False)
    sendtime = db.Column(DateTime)

    def __init__(self,senderid,cid,content,sendtime):
        self.senderid = senderid
        self.cid = cid
        self.content = content
        self.sendtime = sendtime

    def to_json(self):
        json_comment = {
            'mid':self.mid,
            'senderid':self.senderid,
            'cid':self.cid,
            'content':self.content,
            'sendtime':self.sendtime
        }
        return json_comment

