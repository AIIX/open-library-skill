import re
import json
import requests
import openlibrary
from adapt.intent import IntentBuilder
from os.path import join, dirname
from string import Template
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.skills.context import *
from mycroft.util import read_stripped_lines
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

__author__ = 'aix'

LOGGER = getLogger(__name__)

class OpenLibrarySkill(MycroftSkill):
    def __init__(self):
        super(OpenLibrarySkill, self).__init__(name="OpenLibrarySkill")

    @intent_handler(IntentBuilder("SearchByTitle").require("FindByTitleKeyword").build())
    def handle_search_by_title_intent(self, message):
        utterance = message.data.get('utterance').lower()
        utterance = utterance.replace(message.data.get('FindByTitleKeyword'), '')
        searchString = utterance.encode('utf-8')
        api = openlibrary.BookSearch()
        res = api.get_by_title(searchString)
        bookisbn = res.docs[0].isbn[0]        
        method = "GET"
        read_url = "http://openlibrary.org/api/volumes/brief/isbn/"
        read_data = "{0}.json".format(bookisbn)
        response = requests.request(method,read_url+read_data)
        try:
            book = json.loads(response.text)
            bookstatus = book["items"][0]["status"];
            bookurl = book["items"][0]["itemURL"];
            bookcover = book["items"][0]["cover"]["large"];
            booktitle = res.docs[0].title
            bookauthor = res.docs[0].author
            bookpublisher = res.docs[0].publisher[0]
            bookyear = res.docs[0].first_publish_year
            bookobject = {};
            bookobject['bkstatus'] = bookstatus
            bookobject['bkurl'] = bookurl 
            bookobject['bkcover'] = bookcover
            bookobject['bkauthor'] = bookauthor 
            bookobject['bkpublisher'] = bookpublisher
            bookobject['bkyear'] = bookyear 
            bookobject['bktitle'] = booktitle
            bookObjJson = json.dumps(bookobject, ensure_ascii=False)
            resultSpeak = "Found book {0} written by author {1}, first published by {2} in the year {3}".format(booktitle, bookauthor, bookpublisher, bookyear)
            self.speak(resultSpeak)
            downloadstatus = self.checkavailable(bookstatus)
            self.enclosure.bus.emit(Message("bookObject", {'desktop': {'data': bookObjJson}}))
    
        except:
            self.speak("No Books Found")
            
    def checkavailable(self, status):
        if status == "'full access":
            #self.speak("Would you like to read this book ?", expect_response=True)
            return "downloadable"
        else:
            return "unavailable"
            
    def stop(self):
        pass
    
def create_skill():
    return OpenLibrarySkill()
