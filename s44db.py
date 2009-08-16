'''
Created on Aug 15, 2009

@author: koshi
'''
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import *
from datetime import datetime
from dbentities import *
        
class S44DB(object):
    '''
    classdocs
    '''
    

    def __init__(self,dbuser,dbpw,dbname):
        '''
        Constructor
        '''
        self.engine = create_engine('mysql://%s:%s@localhost/%s'%(dbuser,dbpw,dbname), echo=False)
        self.metadata = Base.metadata
        self.metadata.bind = self.engine
        self.metadata.create_all(self.engine)
        self.sessionmaker = sessionmaker( bind=self.engine )
        self.usersessions = dict()
        self.InitialData()
        print 'db init;'
     
    def AddUser(self, nick, country, cpu ):
        session = self.sessionmaker()
               
        user = session.query( User ).filter( User.nick == nick ).first()
        if not user: #new user
            user = User( nick, country, cpu )
            user.firstlogin = datetime.now()
            user.lobby = self.GetDefaultLobby()
            user.lobbyrev = self.GetDefaultLobbyRevision()
            user.os = self.GetDefaultOs()
            session.add( user )
            #session.commit() #commit so we get valid ids??? breaks next commit...
        #update user info
        user.country = country
        user.cpu = cpu
        user.lastlogin = datetime.now()
                    
        session.add( user )
        session.commit()
        session.close()
        
    def UpdateUser(self, nick, lobbyname, lobbyrev_name, osname ):
        session = self.sessionmaker()
        
        user = session.query( User ).filter( User.nick == nick ).first()
        if not user: 
            #some error output
            return
        
        lobby = session.query( Lobby ).filter( Lobby.name == lobbyname ).first()
        if not lobby: #new lobby
            lobby = Lobby( lobbyname )
            session.add( lobby )
            session.commit()
            lobby = session.query( Lobby ).filter( Lobby.name == lobbyname ).first()
            
        lobbyrev = session.query( LobbyRevision ).filter( LobbyRevision.revision == lobbyrev_name ).first()
        if not lobbyrev:
            lobbyrev = LobbyRevision( lobbyrev_name, lobby.id )
            session.add( lobbyrev ) 
            session.commit()
            lobbyrev = session.query( LobbyRevision ).filter( LobbyRevision.revision == lobbyrev_name ).first()
        
        os = session.query( OperatingSystem ).filter( OperatingSystem.name == osname ).first()
        if not os:
            os = OperatingSystem( osname )
            session.add( os ) 
            session.commit()
            os = session.query( OperatingSystem ).filter( OperatingSystem.name == osname ).first()
        user.os_id = os.id

        if user.lobby: #previously set lobby?
            if user.lobby_id != lobby.id:
                switch = LobbySwitch( user.lobby_id, lobby.id, user.id )
                session.add( switch )             
            elif user.lobbyrev_id != lobbyrev.id : #same lobby, but diff rev 
                update = LobbyUpdate( user.lobbyrev_id, lobbyrev.id, user.id )
                session.add( update )            
            user.lobbyrev_id = lobbyrev.id
            user.lobby_id = lobby.id
            
        session.add( user )
        session.commit()
        session.close()
        
    def PrintAll(self):
        session = self.sessionmaker()
        print '-'*60
        for instance in session.query(User).order_by(User.id): 
            print instance.nick, instance.country
            for sess in instance.sessions:
                print sess.start, ' -- ', sess.end 
        print '-'*60
        session.close()
            
    def StartUsersession(self,nick):
        session = self.sessionmaker()
        user = session.query(User).filter(User.nick==nick).first()
        usersession = Usersession(user.id)
        self.usersessions[nick] = usersession
        session.close()
        
    def EndUsersession(self,nick):
        session = self.sessionmaker()
        if nick in self.usersessions:
            usersession = self.usersessions[nick]
            usersession.end = datetime.now()
            session.add(usersession)
            session.commit()
            del self.usersessions[nick]
        session.close()
        
    def GetDefaultLobby(self):
        session = self.sessionmaker()
        ret = session.query( Lobby ).filter( Lobby.name == 'other' ).first()
        session.close()
        return ret
    
    def GetDefaultLobbyRevision(self):
        session = self.sessionmaker()
        ret = session.query( LobbyRevision ).filter( LobbyRevision.revision == 'unknown' ).first()
        session.close()
        return ret        

    def GetDefaultOs(self):
        session = self.sessionmaker()
        ret = session.query( OperatingSystem ).filter( OperatingSystem.name == 'unknown' ).first()
        session.close()
        return ret           
    
    def InitialData(self):
        session = self.sessionmaker()
        lobby = self.GetDefaultLobby() 
        if not lobby: 
            lobby = Lobby( 'other' )
            session.add( lobby )
            session.commit()
            lobby = self.GetDefaultLobby()
        lobbyrev = self.GetDefaultLobbyRevision()
        if not lobbyrev:
            lobbyrev = LobbyRevision( 'unknown', lobby.id )
            session.add( lobbyrev ) 
        
        os = self.GetDefaultOs()
        if not os:
            os = OperatingSystem( 'unknown' )
            session.add( os ) 

        session.commit()
        session.close()
    
    def CloseAllSessions(self):
        names = []
        for name in self.usersessions:
            names.append( name )
        for name in names:
            self.EndUsersession( name )
            
    def GetLobbyUsers( self, lobbyname ):
        session = self.sessionmaker()
        lobby = session.query( Lobby ).filter( Lobby.name == lobbyname ).first()
        ret = 0
        if lobby:
            ret = session.query( User ).filter( User.lobby_id == lobby.id ).count()
        session.close()
        return ret
        
    def GetAllUsers( self ):
        session = self.sessionmaker()
        ret = session.query( User ).count()
        session.close()
        return ret    
    
    def SetPrimaryGame( self, nick, game ):    
        session = self.sessionmaker()
        user = session.query( User ).filter( User.nick == nick ).first()
        if user and user.primary_game != 'multiple':
            user.primary_game = game
            session.commit()
        session.close()   
        
    def GetGameUsers( self, game_name ):
        session = self.sessionmaker()
        users = session.query( User ).filter( User.primary_game == game_name )
        ret = []
        for user in users:
            ret.append( user.nick )
        session.close()
        return ret
         
         
