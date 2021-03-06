from plugin.interface import IStoragePlugin
from wrappers.libDLNA import DLNAInterface
from manager import OneServerManager
from vfs import Entry
import os
import os.path
from os.path import join, getsize
import platform
from pyutilib.component.core import *
#import threading
#import Queue
import fnmatch
import string

from os.path import expanduser

try:
	import sqlite3
except ImportError:
	print 'sqlite3 is not found.  Make sure you have python 2.7 installed'

try:
	from pymediainfo import MediaInfo
except ImportError:
	print 'pymediainfo:MediaInfo is not found.  Make sure you have the eyed3 library installed'



##
# Provides a data source to browse local files for OneServer
# Will add a directory structure like so
# /LocalFilePlugin/browse/* Directly browse the folder monitored
# /LocalFilePlugin/genre/*  Browse based on genres
# /LocalFilePlugin/artist/* Browse based on artists
# etc
class LocalFilePlugin(Plugin):
	implements(IStoragePlugin, inherit=False)

	PLUGINDATABASE = 'LocalFilePlugin.db'

	def __init__(self):
		self.ispo = IStoragePlugin('Local Files')
		self.tree = Entry("/lfs", OneServerManager().CONTAINER_MIME, None, [], "LFS", "lfs", -1, None)
		self.dlna = OneServerManager().dlna
	#	self.dbHelper = LocalFileDatabaseHelper(self.PLUGINDATABASE)
		self.os = self.getOperatingSystem()
		self.home = expanduser('~')
		if self.os == 'Windows':
			self.generateList(expanduser('~')+"/My Music", "/Music")
			self.generateList(expanduser('~')+"/My Pictures", "/Pictures")
			self.generateList(expanduser('~')+"/My Videos", "/Videos")
		elif self.os == 'Darwin':
			#TODO Update when figured out Apple Media Storage
			self.generateList(os.environ['HOME'])
		elif self.os == 'Linux':
			self.generateList(expanduser('~')+"/Music", "/Music")
			self.generateList(expanduser('~')+"/Pictures", "/Pictures")
			self.generateList(expanduser('~')+"/Videos", "/Videos")
	#	self.generateList(expanduser('~'))
		
		
		
	def enable(self):
		OneServerManager().log.debug('LocalFilePlugin is enabled')
	
	def disable(self):
		raise NotImplementedError( "Should have implemented this" )
	
	def load(self):
		self.dbHelper = LocalFileDatabaseHelper(self.PLUGINDATABASE)
		self.dlna = OneServerManager().dlna
		OneServerManager().log.debug('LocalFilePlugin is loaded')
	
	def unload(self):
		self.dpHelper = None
		self.idlna = None
		del dbHelper
		
		
	def info(self):
		return "Local File Plugin 1.0.0"
	
	def generateEntryForDirectory(self, directory):
		newEntry = Entry(directory,OneServerManager().CONTAINER_MIME, None, [], directory, directory, -1, None)
		return newEntry
	
	
	def search(f, filter):
		matches = []

		for root, dirnames, filenames in os.walk(f):
			for dir in dirnames:
				matches.append(search(os.path.join(root, dir), filter))
			matches.append((os.path.join(root, filename) for filename in fnmatch.filter(filenames, filter)))
		return matches
	
	def search(root, recurse=0, pattern='*', return_folders=0):
		#initialize
		results = []
		
		# must have at least root folder
		try:
			names = os.listdir(root)
		except os.error:
			return results
		
		#expand pattern
		pattern = pattern or '*'
		pat_list = string.splitfields(pattern, ';')
		
		#check each file
		for name in names:
			fullname = os.path.normpath(os.path.join(root,name))
			
			#grab if it matches our pattern and entry type
			for pat in pat_list:
				if fnmatch.fnmatch(name, pat):
					if os.path.isfile(fullname) or (return_folders and os.path.isdir(fullname)):
						result.append(fullname)
						continue
			
			#recursively scan other folders, appending results
			if recurse:
				if os.path.isdir(fullname) and not os.path.islink(fullname):
					results = results + Walk(fullname, recurse, pattern, return_folders)
		
		return results
	
	
	
	
	def generateList(self, path, location):
		OneServerManager().log.debug('LocalFilePlugin: Loading Tree')
		listOfFiles = {}
		try:
			OneServerManager().log.debug(path)
			for dirpath, dirnames, filenames in os.walk(path):
				for filename in filenames:
					listOfFiles[filename] = os.sep.join([dirpath, filename])
		except EntryNotFoundError:
			print('Entry was not Found')
		
		locationT = location.replace("/","")
		entryForLocation = Entry(location,OneServerManager().CONTAINER_MIME, None, [], locationT.upper(), locationT, -1, None)
		for f in listOfFiles:
			filename = listOfFiles[f]
			profile = OneServerManager().idlna.dlna_guess_media_profile(self.dlna, filename)
			OneServerManager().log.debug('Profile for %s: %s', filename, str(profile))
			if profile is None:
				raise ValueError("Invalid media type on {0}".format(f))
			try:
				profile.contents
				fileSize = os.path.getsize(filename)
				entryForLocation.addChild(Entry(filename,profile,self.tree,None, filename,"",fileSize,LocalFilePlugin.createLocalFileHandle))
			except ValueError:
				OneServerManager().log.debug("Invalid profile object, skipping "+filename)
			
		self.tree.addChild(entryForLocation)
		

	def getOperatingSystem(self):
		return platform.system()
	
	@staticmethod
	def createLocalFileHandle(entry):
		fh =  open(entry.fullPath, "r")
		OneServerManager().log.debug("Opened fh at {0}".format(str(fh)))
		return fh
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
		if os.path.isdir(path):
			raise DirectoryError
		if os.path.isfile(path):
			profile = self.dlna.idlna.dlna_guess_media_profile(self.dlna, path)
			path = os.path.splitext("path")[0]
			fileSize = os.path.getsize(path)
			absolutePath = os.path.abspath(path)
			anEntry = Entry(path,profile,absolutePath,None,path,"",fileSize,None)
		return anEntry
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
		listOfFiles = {}
		try:
			for(dirpath, dirnames, filenames) in os.walk(path):
				for filename in filenames:
					listOfFiles[filename] = os.sep.join([dirpath, filename])
		except EntryNotFoundError:
			print('Entry was not Found')
			
		return listOfFiles
		
	##
	# This function takes an Entry and adds it to the given data source.
	#
	# @param entry The Entry to add
	# @param type You need to pass in what type of media object it is.  0 for Video, 1 for Audio, and 2 for images 
	#
	# @throws UploadNotSupportedError If uploading to the given source is not supported
	def put(self, entry, type=0):
		mediaInfo = MediaInfo.parse(entry.fullPath)
		FileName = entry.title
		metadata[filename] = os.path.splitext(entry.fullPath)[0]
		metadata[extension] = os.path.splitext(entry.fullPath)[1]
		metadata[format] = None
		metadata[datecreated] = None
		if type==0:
			metadata[genres] = None
			metadata[directors] = None
			for track in mediaInfo.tracks:
				if track.track_type == 'Video':
					metadata[format] = track.format
					metadata[genres] = track.genres
					metadata[datecreated] = track.encoded_date
					metadata[directors] = track.directors
			
		elif type==1:
			metadata[genres] = None
			metadata[artists] = None
			metadata[album] = None
			for track in mediaInfo.tracks:
				if track.track_type == 'Audio':
					metadata[format] = track.format
					metadata[genres] = track.genres
					metadata[datecreated] = track.encoded_date
					metadata[artists] = track.artist
					metadata[album] = track.album
			
		elif type==2:
			metadata[artists] = None
			for track in mediaInfo.tracks:
				if track.track_type == 'Image':
					metadata[format] = track.format
					metadata[datecreated] = track.encoded_date
					metadata[artists] = track.artist
		else:
			return
		self.dbHelper.addEntry(entry.title, metadata, type)
		
	##
	# This function searches through all sources to find matching entries
	#
	# @param metadata A dict of metadata which consists of keys such as "artist" or "genre".  As many as possible will be matches, and each additional value will be considered an AND
	def search(self, metadata):
		listOfEntries = None
		listOfEntries = self.dbHelper.findEntry(metadata,0)
		listOfEntries = listOfEntries + self.dbHelper.findEntry(metadata, 1)
		listOfEntries = listOfEntries + self.dbHelper.findEntry(metadata, 2)
		return listOfEntries
		
		
	##
	# This function updates the metadata for the given entry
	# All fields found in the metadata dict will be overwritten
	# 
	# @param entry An Entry object that tells from what media file does the updated media
	# @param metadata Dictionary of metadata that needs to be updated
	# @param type You need to pass in what type of media object it is.  0 for Video, 1 for Audio, and 2 for images
	def updateMetadata(self, entry, metadata,type=0):
		metaData = metadata
		mediaInfo = MediaInfo.parse(entry.fullPath)
		FileName = entry.title
		metadata[filename] = os.path.splitext(entry.fullPath)[0]
		metadata[extension] = os.path.splitext(entry.fullPath)[1]
		metadata[format] = None
		metadata[datecreated] = None
		if type==0:
			self.dbHelper.removeEntry(entry.title,0)
			metadata[genres] = None
			metadata[directors] = None
			for track in mediaInfo.tracks:
				if track.track_type == 'Video':
					metadata[format] = track.format
					metadata[genres] = track.genres
					metadata[datecreated] = track.encoded_date
					metadata[directors] = track.directors
			
			self.dbHelper.addEntry(entry.title, metadata, 0)
		if type==1:
			self.dbHelper.removeEntry(entry.title,1)
			metadata[genres] = None
			metadata[artists] = None
			metadata[album] = None
			for track in mediaInfo.tracks:
				if track.track_type == 'Audio':
					metadata[format] = track.format
					metadata[genres] = track.genres
					metadata[datecreated] = track.encoded_date
					metadata[artists] = track.artist
					metadata[album] = track.album
			
			self.dbHelper.addEntry(entry.title, metadata, 1)
		if type==2:
			self.dbHelper.removeEntry(entry.title,2)
			metadata[artists] = None
			for track in mediaInfo.tracks:
				if track.track_type == 'Image':
					metadata[format] = track.format
					metadata[datecreated] = track.encoded_date
					metadata[artists] = track.artist
			
			self.dbHelper.addEntry(entry.title, metadata, 2)
		return metadata
		
##
# This classs helps with handling the metadata database for the plugin.
class LocalFileDatabaseHelper():
	
	##
	# The instance of this singleton
	_instance = None
	
	##
	# Overides the __new__ of object to make sure we only have one instance
	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(LocalFileDatabaseHelper, cls).__new__(cls, *args, **kwargs)
		return cls._instance
	
	##
	# database is the path to the sqlite file
	def __init__(self, database):
		self.database = sqlite3.connect(database)
		self.cur = database.cursor()
		onCreate()
		
	##
	# Creates the database if needed
	def onCreate(self):
		try:
			self.cur.execute('''create table if not exists plugin_Video(Title varchar,Filename varchar,Extension varchar,Format varchar,Genres varchar,DateCreated varchar,Directors varchar)''')
			self.cur.execute('''create table if not exists plugin_Audio(Title varchar,Filename varchar,Extension varchar,Format varchar,Genres varchar,DateCreated varchar,Artists varchar,Album varchar)''')
			self.cur.execute('''create table if not exists plugin_Images(Title varchar,Filename varchar,Extension varchar,Format varchar,DateCreated varchar,Artists varchar)''')
		except sqlite3.Error, msg:
			print msg
	
	
	
	##
	# This function addes the given Entry to the database
	# metadata will be a dict with keys such as genre and artist
	#
	# @param title String of title
	# @param metadata dict with keys like genre and artist
	# @param type You need to pass in what type of media object it is.  0 for Video, 1 for Audio, and 2 for images
	def addEntry(self, title, metadata, type=0):
		try:
			filename = metadata[filename]
			extension = metadata[extension]
			format = metadata[format]
			datecreated = metadata[datecreated]
			if type==0:
				genres = metadata[genres]
				directors = metadata[directors]
				self.cur.execute("insert into plugin_Video values ("+title+","+filename+","+extension+","+format+","+genres+","+datecreated+","+directors+")")
			elif type==1:
				genres = metadata[genres]
				artists = metadata[artists]
				album = metadata[album]
				self.cur.execute("insert into plugin_Audio values ("+title+","+filename+","+extension+","+format+","+genres+","+datecreated+","+artists+","+album+")")
			elif type==2:
				artists = metadata[artists]
				self.cur.execute("insert into plugin_Images values ("+title+","+filename+","+extension+","+format+","+datecreated+","+artists+")")
			
			self.database.commit()
		except sqlite3.Error, msg:
			print msg
		
	##
	# This function get a dictionary containing all metadata on the given title
	# In a dict that with keys that define the type of data such as genre
	#
	# @title title MediaFile Title
	# @param type You need to pass in what type of media object it is.  0 for Video, 1 for Audio, and 2 for images
	def getEntry(self, title, type=0):
		answer = None
		try:
			if type==0:
				self.cur.execute("select * from plugin_Video where Title ='"+title+"';")
			elif type==1:
				answer = self.cur.execute("select * from plugin_Audio where Title ='"+title+"';")
			elif type==2:
				answer = self.cur.execute("select * from plugin_Images where Title ='"+title+"';")
			
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
			if metadata[filename]==None:
				filename = "*"
			else:
				filename = metadata[filename]
			if metadata[extension]==None:
				extension = "*"
			else:
				extension = metadata[extension]
			if metadata[format]==None:
				format = "*"
			else:
				format = metadata[format]
			if metadata[genres]==None:
				genres = "*"
			else:
				genres = metadata[genres]
			if metadata[datecreated]==None:
				datecreated = "*"
			else:
				datecreated = metadata[datecreated]
			if metadata[directors]==None:
				directors = "*"
			else:
				directors = metadata[directors]
			if metadata[artists]==None:
				artists = "*"
			else:
				artists = metadata[artists]
			if metadata[album]==None:
				album = "*"
			else:
				album = metadata[album]
			
			if type==0:
				self.cur.execute("select * from plugin_Video where Extension ='"+extension+"' and Format ='"+format+"' and Genres ='"+genres+"' and DateCreated ='"+datecreated+"' and Directors ='"+directors+"';")
			elif type==1:
				answer = self.cur.execute("select * from plugin_Audio where Extension ='"+extension+"' and Format ='"+format+"' and Genres ='"+genres+"' and DateCreated ='"+datecreated+"' and Artists ='"+artists+" and Album ='"+album+"';")
			elif type==2:
				answer = self.cur.execute("select * from plugin_Images where Extension ='"+extension+"' and Format ='"+format+"' and DateCreated ='"+datecreated+"' and Artists ='"+artists+"';")
			
			answer = self.cur.fetchall()
			answer = dict(answer)
		except sqlite3.Error, msg:
			print msg
		return answer
		
		
	##
	#This method is called when an Entry needs to be removed from a db
	#
	# @param title name of the file
	# @param type You need to pass in what type of media object it is.  0 for Video, 1 for Audio, and 2 for images
	def removeEntry(self,title,type=0):
		try:
			if type==0:
				self.cur.execute("delete * from plugin_Video where Title ='"+title+"'")
			elif type==1:
				self.cur.execute("delete * from plugin_Audio where Title ='"+title+"'")
			elif type==2:
				self.cur.execute("delete * from plugin_Images where Title ='"+title+"'")
		except sqlite3.Error, msg:
			print msg
	##
	#When ojbect is destroyed it is set up to close the database and cursor to the database
	def __del__ (self):
		self.cur.close()
		self.database.close()