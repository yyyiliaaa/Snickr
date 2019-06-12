drop database snickr;
create database snickr;
use snickr;

CREATE TABLE User (
    uid INT AUTO_INCREMENT PRIMARY KEY,
    uname VARCHAR(50) NOT NULL,
    nickname VARCHAR(50),
    upassword VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL
);
    
CREATE TABLE Workspace (
    wid INT AUTO_INCREMENT PRIMARY KEY,
    wname VARCHAR(50) NOT NULL,
    creatorid INT,
    description VARCHAR(200),
    wtime TIMESTAMP,
    FOREIGN KEY (creatorid)
        REFERENCES User (uid)
        ON DELETE CASCADE
);
    
CREATE TABLE WorkspaceMembership (
    uid INT,
    wid INT,
    wjointime TIMESTAMP,
    PRIMARY KEY (uid , wid),
    FOREIGN KEY (uid)
        REFERENCES User (uid)
        ON DELETE CASCADE,
    FOREIGN KEY (wid)
        REFERENCES Workspace (wid)
        ON DELETE CASCADE
);

CREATE TABLE WorkspaceInvitation (
    winvitorid INT NOT NULL,
    wid INT NOT NULL,
    winviteeemail VARCHAR(50) NOT NULL,
    winvitetime TIMESTAMP,
    wstatus ENUM('accept', 'reject', 'pending'),
    PRIMARY KEY (winvitorid , wid , winviteeemail),
    FOREIGN KEY (winvitorid , wid)
        REFERENCES WorkspaceMembership (uid , wid)
        ON DELETE CASCADE
);

CREATE TABLE Channel (
    cid INT AUTO_INCREMENT PRIMARY KEY,
    creatorid INT,
    wid INT,
    ctype ENUM('public', 'private', 'direct'),
    cname VARCHAR(50) NOT NULL,
    ctime TIMESTAMP,
    FOREIGN KEY (creatorid , wid)
        REFERENCES WorkspaceMembership (uid , wid)
        ON DELETE CASCADE
);
    
CREATE TABLE Administrator (
    uid INT,
    wid INT,
    PRIMARY KEY (uid , wid),
    FOREIGN KEY (uid , wid)
        REFERENCES WorkspaceMembership (uid , wid)
        ON DELETE CASCADE
);
        
CREATE TABLE ChannelMembership (
    uid INT,
    cid INT,
    cjointime TIMESTAMP,
    PRIMARY KEY (uid , cid),
    FOREIGN KEY (uid)
        REFERENCES User (uid)
        ON DELETE CASCADE,
    FOREIGN KEY (cid)
        REFERENCES Channel (cid)
        ON DELETE CASCADE
);
  
CREATE TABLE ChannelInvitation (
    cinvitorid INT NOT NULL,
    cid INT NOT NULL,
    cinviteeid INT NOT NULL,
    cinvitetime TIMESTAMP,
    cstatus ENUM('accept', 'reject', 'pending'),
    PRIMARY KEY (cinvitorid , cid , cinviteeid),
    FOREIGN KEY (cinvitorid , cid)
        REFERENCES ChannelMembership (uid , cid)
        ON DELETE CASCADE,
    FOREIGN KEY (cinviteeid)
        REFERENCES User (uid)
        ON DELETE CASCADE
);

CREATE TABLE Message (
    mid INT AUTO_INCREMENT PRIMARY KEY,
    senderid INT,
    cid INT,
    content VARCHAR(500) NOT NULL,
    sendtime TIMESTAMP,
    FOREIGN KEY (senderid , cid)
        REFERENCES Channelmembership (uid , cid)
        ON DELETE CASCADE
);

    

    