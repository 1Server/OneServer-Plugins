from IStoragePluginObserver import IStoragePluginObserver
import sqlite3
from vfs import Entry
##
# Provides a data source to browse local files for OneServer
# Will add a directory structure like so
# /LocalFilePlugin/browse/* Directly browse the folder monitored
# /LocalFilePlugin/genre/*  Browse based on genres
# /LocalFilePlugin/artist/* Browse based on artists
# etc
# Metadata shoudl be gotten with https://bitbucket.org/haypo/hachoir/wiki/hachoir-metadata
class LocalFilePlugin(IStoragePluginObserver):

	self.PLUGINDATABASE = 'lfpDatabase.db'

	def __init__(self):
		self.dbHelper = LocalFileDatabaseHelper()
		
	def enable(self):
		raise NotImplementedError( "Should have implemented this" )
	
	def disable(self):
		raise NotImplementedError( "Should have implemented this" )
	
	def load(self):
		raise NotImplementedError( "Should have implemented this" )
	
	def unload(self):
		raise NotImplementedError( "Should have implemented this" )
		
	##
	# Gets the Entry given by the path.  Raises a DirectoryException if a directory is given
	#
	# @param path The path to the wanted Entry
	#
	# @return The Entry at the path given
	#
	# @throws DirectoryError If a directory path is given
	# @throws EntryNotFoundError If the path does not lead to an Entry
	def get(self, path):
		raise NotImplementedError( "Should have implemented this" )
		
	##
	# This function functions similar to ls. 
	# If a path to a directory is given, all of the entries in that directory will be returned.
	# If it is given the path to a file, it will return a list with one entry which is that file.
	# If any subdirectories are listed, their path will be prefixed with a d such as "d/path/to/dir".
	#
	# @param path The path to list
	#
	# @throws EntryNotFoundError If the given path does not exist
	def list(self, path):
		raise NotImplementedError( "Should have implemented this" )
		
	##
	# This function takes an Entry and adds it to the given data source.
	#
	# @param entry The Entry to add
	# @param source The source to add it to
	#
	# @throws UploadNotSupportedError If uploading to the given source is not supported
	def put(self, entry, source):
		raise NotImplementedError( "Should have implemented this" )
		
	##
	# This function searches through all sources to find matching entries
	#
	# @param metadata A dict of metadata which consists of keys such as "artist" or "genre".  As many as possible will be matches, and each additional value will be considered an AND
	def search(self, metadata):
		raise NotImplementedError( "Should have implemented this" )
		
	##
	# This function updates the metadata for the given entryy
	# All fields found in the metadata dict will be overwritten
	def updateMetadata(self, entry, metadata):
		pass
		
##
# This classs helps with handling the metadata database for the plugin.
class LocalFileDatabaseHelper():
	
	##
	# database is the path to the sqlite file
	def __init__(self, database):
		self.database = sqlite3.connect(database)
		self.cur = database.cursor()
		
	
	##
	# Creates the database if needed
	def onCreate(self):
		try:
			self.cur.execute('''create table if not exists plugin_Video(Filename varchar,Extension varchar,Format varchar,Genres varchar,DateCreated varchar,Directors varchar)''')
			self.cur.execute('''create table if not exists plugin_Audio(Filename varchar,Extension varchar,Format varchar,Genres varchar,DateCreated varchar,Artists varchar,Album varchar)''')
			self.cur.execute('''create table if not exists plugin_Images(Filename varchar,Extension varchar,Format varchar,DateCreated varchar,Artists varchar)''')
		except sqlite3.Error, msg:
			print msg
	
	
	
	##
	# This function addes the given Entry to the database
	# metadata will be a dict with keys such as genre and artist
	#
	# @param title String of title
	# @param metadata dict with keys like genre and artist
	# @param type You need to pass in what type of media object it is.  0 for Video, 1 for Audio, and 2 for images
	def addEntry(self, title, metadata,type):
		try:
			if(type==0):
				filename = metadata[filename]
				extension = metadata[extension]
				format = metadata[format]
				genres = metadata[genres]
				datecreated = metadata[datecreated]
				directors = metadata[directors]
				
				self.cur.execute("insert into plugin_Video values ("+filename+","+extension+","+format+","+genres+","+datecreated+","+directors+")")
				self.database.commit()
			elif(type==1):
				filename = metadata[filename]
				extension = metadata[extension]
				format = metadata[format]
				genres = metadata[genres]
				datecreated = metadata[datecreated]
				artists = metadata[artists]
				album = metadata[album]
				
				self.cur.execute("insert into plugin_Audio values ("+filename+","+extension+","+format+","+genres+","+datecreated+","+artists+","+album+")")
				self.database.commit()
			elif(type==2):
				filename = metadata[filename]
				extension = metadata[extension]
				format = metadata[format]
				datecreated = metadata[datecreated]
				artists = metadata[artists]
				
				self.cur.execute("insert into plugin_Images values ("+filename+","+extension+","+format+","+datecreated+","+artists+")")
				self.database.commit()
		except sqlite3.Error, msg:
			print msg
		
	##
	# This function get a dictionary containing all metadata on the given title
	# In a dict that with keys that define the type of data such as genre
	#
	# @title title String of title
	# @param type You need to pass in what type of media object it is.  0 for Video, 1 for Audio, and 2 for images
	def getEntry(self, title, type=0):
		answer = None
		try:
			if(type==0):
				self.cur.execute("select * from plugin_Video where Filename ='"+title+"';")
				answer = self.cur.fetchone()
				answer = dict(answer)
			elif(type==1):
				answer = self.cur.execute("select * from plugin_Audio where Filename ='"+title+"';")
				answer = self.cur.fetchone()
				answer = dict(answer)
			elif(type==2):
				answer = self.cur.execute("select * from plugin_Images where Filename ='"+title+"';")
				answer = self.cur.fetchone()
				answer = dict(answer)
		except sqlite3.Error, msg:
			print msg
		return answer
	##
	# Returns a list of titles that match the given metadata dict
	#
	# @param metadata dict with keys like Genre or Artists
	# @param type You need to pass in what type of media object it is.  0 for Video, 1 for Audio, and 2 for images
	def findEntry(self, metadata, type=0):
		answer = None
		try:
			if(type==0):
				if(metadata[filename]==None):
					filename = "*"
				else:
					filename = metadata[filename]
				if(metadata[extension]==None):
					extension = "*"
				else:
					extension = metadata[extension]
				if(metadata[format]==None):
					format = "*"
				else:
					format = metadata[format]
				if(metadata[genres]==None):
					genres = "*"
				else:
					genres = metadata[genres]
				if(metadata[datecreated]==None):
					datecreated = "*"
				else:
					datecreated = metadata[datecreated]
				if(metadata[directors]==None):
					directors = "*"
				else:
					directors = metadata[directors]
				
				
				self.cur.execute("select * from plugin_Video where Extension ='"+extension+"' and Format ='"+format+"' and Genres ='"+genres+"' and DateCreated ='"+datecreated+"' and Directors ='"+directors+"';")
				answer = self.cur.fetchall()
				answer = dict(answer)
			elif(type==1):
				if(metadata[filename]==None):
					filename = "*"
				else:
					filename = metadata[filename]
				if(metadata[extension]==None):
					extension = "*"
				else:
					extension = metadata[extension]
				if(metadata[format]==None):
					format = "*"
				else:
					format = metadata[format]
				if(metadata[genres]==None):
					genres = "*"
				else:
					genres = metadata[genres]
				if(metadata[datecreated]==None):
					datecreated = "*"
				else:
					datecreated = metadata[datecreated]
				if(metadata[artists]==None):
					artists = "*"
				else:
					artists = metadata[artists]
				if(metadata[album]==None):
					album = "*"
				else:
					album = metadata[album]
				
				answer = self.cur.execute("select * from plugin_Audio where Extension ='"+extension+"' and Format ='"+format+"' and Genres ='"+genres+"' and DateCreated ='"+datecreated+"' and Artists ='"+artists+" and Album ='"+album+"';")
				answer = self.cur.fetchall()
				answer = dict(answer)
			elif(type==2):
				if(metadata[filename]==None):
					filename = "*"
				else:
					filename = metadata[filename]
				if(metadata[extension]==None):
					extension = "*"
				else:
					extension = metadata[extension]
				if(metadata[format]==None):
					format = "*"
				else:
					format = metadata[format]
				if(metadata[datecreated]==None):
					datecreated = "*"
				else:
					datecreated = metadata[datecreated]
				if(metadata[artists]==None):
					artists = "*"
				else:
					artists = metadata[artists]
				
				answer = self.cur.execute("select * from plugin_Images where Extension ='"+extension+"' and Format ='"+format+"' and DateCreated ='"+datecreated+"' and Artists ='"+artists+"';")
				answer = self.cur.fetchall()
				answer = dict(answer)
		except sqlite3.Error, msg:
			print msg
		return answer
		
	##
	#When ojbect is destroyed it is set up to close the database and cursor to the database
	def __del__ (self):
		self.cur.close()
		self.database.close()