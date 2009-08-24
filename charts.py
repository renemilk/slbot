'''
Created on Aug 16, 2009

@author: koshi
'''
from sqlalchemy import *
from sqlalchemy.orm import *
from datetime import datetime
from dbentities import *
import cairo
import pycha.bar
from sqlalchemy.sql import and_


class Charts(object):
    '''
    classdocs
    '''


    def __init__(self,dbuser,dbpw,dbname,datadir):
        '''
        Constructor
        '''
        self.engine = create_engine('mysql://%s:%s@localhost/%s'%(dbuser,dbpw,dbname), echo=False)
        self.metadata = Base.metadata
        self.metadata.bind = self.engine
        self.metadata.create_all(self.engine)
        self.sessionmaker = sessionmaker( bind=self.engine )
        self.datadir = datadir
        print 'db init;'      
        
    def GameUsers(self, name = 's44'):
        width, height = (500, 400)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        session = self.sessionmaker()

        query = session.query( User ).filter( User.primary_game == name )
        today = query.filter( and_(User. ) )
        data = []
        ticks = []
        for rev in lobbyrevs:
            num = session.query( User ).filter( User.lobbyrev_id == rev.id ).count()
            if num < 5:
                continue
            print rev.id, num
            el = [ rev.id, num ]
            data.append(el)
            ticks.append( dict(v=rev.id, label=rev.revision) )
            
        dataSet = ( ('Revisions', data), )    
        options = {
                   'legend': {'hide': True},
                   'background': {'color': '#f0f0f0'},
                   'axis': {
                            'x': {
                                'ticks': ticks  ,
                                'label': 'Revisionstrings',
                                'rotate': 60,
                            },
                            'y': {
                                'tickCount': 20,
                                'rotate': 0,
                                'label': '#users',
                            }
                        },
                    'padding': {
                        'bottom': 125,
                    },
                    'title': 'SpringLobby revisions in use'

                   }
        chart = pycha.bar.VerticalBarChart(surface, options) 
        chart.addDataset(dataSet)
        chart.render()
        surface.write_to_png( self.datadir + '/s44users.png')
        session.close()
        
    def test(self):
        width, height = (500, 400)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        session = self.sessionmaker()
        
        lobby = session.query( Lobby ).filter( Lobby.name == 'SpringLobby' ).first()
        lobbyrevs = []
        if lobby:
            lobbyrevs = session.query( LobbyRevision ).filter( LobbyRevision.lobby_id == lobby.id ).all()
            print 'here ', len(lobbyrevs)
        else:
            lobbyrevs = session.query( LobbyRevision ).all()
        data = []
        ticks = []
        for rev in lobbyrevs:
            num = session.query( User ).filter( User.lobbyrev_id == rev.id ).count()
            if num < 5:
                continue
            print rev.id, num
            el = [ rev.id, num ]
            data.append(el)
            ticks.append( dict(v=rev.id, label=rev.revision) )
            
        dataSet = ( ('Revisions', data), )    
        options = {
                   'legend': {'hide': True},
                   'background': {'color': '#f0f0f0'},
                   'axis': {
                            'x': {
                                'ticks': ticks  ,
                                'label': 'Revisionstrings',
                                'rotate': 60,
                            },
                            'y': {
                                'tickCount': 20,
                                'rotate': 0,
                                'label': '#users',
                            }
                        },
                    'padding': {
                        'bottom': 125,
                    },
                    'title': 'SpringLobby revisions in use'

                   }
        chart = pycha.bar.VerticalBarChart(surface, options) 
        chart.addDataset(dataSet)
        chart.render()
        surface.write_to_png( self.datadir + '/revisions.png')
        session.close()
        
 

