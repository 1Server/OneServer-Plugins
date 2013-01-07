from IStoragePluginObserver import IStoragePluginObserver
import sqlite3
##
# Provides a data source to browse local files for OneServer
# Will add a directory structure like so
# /LocalFilePlugin/browse/* Directly browse the folder monitored
# /LocalFilePlugin/genre/*  Browse based on genres
# /LocalFilePlugin/artist/* Browse based on artists
# etc
# Metadata shoudl be gotten with https://bitbucket.org/haypo/hachoir/wiki/hachoir-metadata
class LocalFilePlugin(IStoragePluginObserver):

	def __init__(self):
		pass
		
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
		pass
	
	##
	# Creates the database if needed
	def onCreate(self):
		pass
		
	##
	# This function addes the given Entry to the database
	# metadata will be a dict with keys such as genre and artist
	def addEntry(self, title, metadata):
		pass
		
	##
	# This function get a dictionary containing all metadata on the given title
	# In a dict that with keys that define the type of data such as genre
	def getEntry(self, title):
		pass
		
	##
	# Returns a list of titles that match the given metadata dict
	def findEntry(self, metadata):
		pass
		