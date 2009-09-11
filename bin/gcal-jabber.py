#!/usr/bin/env python
# encoding: utf-8

import atom, atom.service
import gdata, gdata.service, gdata.calendar, gdata.calendar.service
import os
import sys
import xmpp
import ConfigParser
import logging, logging.handlers

def ProcessEvents(conn):
	if not conn.isConnected():
		print "Attempting to reconnect"
		conn.reconnectAndReauth()

	try:
		conn.Process(1)
	except KeyboardInterrupt:
		return 1

def commandHandler(conn, message):
	if message.getBody() is None: return

	logger.info("Handling incoming message from %s: %s", message.getFrom(), message.getBody())
	# TODO: add a sender filter

	event           = gdata.calendar.CalendarEventEntry()
	event.content   = atom.Content(text=message.getBody())
	event.quick_add = gdata.calendar.QuickAdd(value='true')
	new_event       = calendar_service.InsertEvent(event, '/calendar/feeds/default/private/full')

	conn.send(xmpp.Message(message.getFrom(), "You can view your new event here: %s" % new_event.GetHtmlLink().href))

def presenceHandler(conn, message):
	u = message.getFrom();

	logger.info("Handling incoming presence message from %s: %s", u, message.getType())

	if message.getType() == "subscribe":
		conn.send(xmpp.Presence(to=u, typ='subscribed'))
		conn.send(xmpp.Presence(to=u, typ='subscribe'))

def disconnectHandler(conn):
	conn.disconnectAndReauth()
	setBotPresence(conn)

def setBotPresence(conn):
	botPresence = xmpp.Presence()
	botPresence.setShow("default")
	botPresence.setStatus("Send me something to Quick-Add!")
	botPresence.setTimestamp()
	conn.send(botPresence)

config      = ConfigParser.ConfigParser()
config_file = os.path.expanduser("~/.gcal-jabber")

try:
	config.read(os.path.expanduser(config_file))
	if os.stat(config_file).st_mode != 0100600:
		logger.warning("%s should not be readable by other users! Changing to mode 0600", config_file)
		os.chmod(config_file, 0600)
except:
	config.add_section("Google")
	config.add_section("Jabber")
	config.set("Google", "Password", 	"GOOGLE_PASSWORD")
	config.set("Google", "Email", 		"user@example.com")
	config.set("Jabber", "JID", 			"jabber@example.com")
	config.set("Jabber", "Password", 	"JABBER_PASSWORD")
	config.write(open(config_file, "w"))
	os.chmod(config_file, 0600)
	print "Please edit %s to provide your account information" % config_file
	sys.exit(1)

# TODO: switch to storing the logging config info in our config file
logger                    = logging.getLogger("gcal-jabber")
logger.setLevel(logging.DEBUG)

syslog_handler            = logging.handlers.SysLogHandler()
syslog_handler.setLevel(logging.DEBUG)
logger.addHandler(syslog_handler)

calendar_service          = gdata.calendar.service.CalendarService()
calendar_service.email    = config.get('Google', 'email')
calendar_service.password = config.get('Google', 'password')
calendar_service.source   = 'org.improbable.gcal-jabber'

logger.info("Authenticating to Google account %s", config.get('Google', 'email'))
calendar_service.ProgrammaticLogin()

logger.info("Connecting to Jabber account %s", config.get('Jabber', 'jid'))

jid = xmpp.protocol.JID(config.get('Jabber', 'jid'))
cl  = xmpp.Client(jid.getDomain(), debug='always')
cl.connect()

logger.info("Authenticating to Jabber server")
cl.auth(jid.getNode(), config.get('Jabber', 'password'))

logger.debug("Registering Jabber handlers")
cl.RegisterHandler('message', commandHandler)
cl.RegisterHandler('presence', presenceHandler)
cl.RegisterDisconnectHandler(disconnectHandler)

logger.debug("Sending Jabber presence information")
cl.sendInitPresence()
setBotPresence(cl)

logger.info("Starting bot")

while ProcessEvents(cl): pass