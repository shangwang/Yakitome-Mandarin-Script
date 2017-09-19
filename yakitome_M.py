#!/usr/bin/python

import sys, getopt
import urllib
import httplib
import json
import urllib2
import time
import codecs
import re

class YakitoMeConverter:

    def __init__(self, inputfile, outputfile, language):
        self.inputfile = inputfile
        self.outputfile = outputfile
        self.language = language
        self.apiKey = '6CZf2r6qdcVknMAW0l7tW'

    def rest(self,request_type, api_func, vars):
    
        """performs RESTful calls to YAKiToMe API functions"""
      
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"
        }
        print ' '
        print '======== REQUEST ======='
        print api_func + ': ' + str(vars)
        
        conn = httplib.HTTPSConnection('www.yakitome.com')
        conn.request(request_type,
        '/api/rest/%s' % api_func,
        urllib.urlencode(vars),
        headers,
        )
        response = conn.getresponse()
        json = response.read()
        print '======== RESPONSE ======='
        print json
        
        return json


    def startConversion(self):

        file = codecs.open(self.inputfile,encoding='utf-8')
        #io.open(self.inputfile, 'r',)
        oFile = codecs.open(self.outputfile, encoding='utf-8',mode='w')
        
        # Mandarin sound
        sound = 'Gan'
        
        if self.language  == 'E':
            sound = 'Bob'
        
        index = 0
        for line in file:
            textStrings = line.split('|')
            
            for textStrng in textStrings:
                fileName = 'AudioFile' + str(index) + '.mp3'
                fileNameList = re.findall(r'\<([^]]*)\>', textStrng)
                if len(fileNameList) == 0:
                    index += 1
                else:
                    textStrng = re.sub(r'\<([^]]*)\>', '', textStrng)
                    fileName = fileNameList[0]
                    print fileName
                
                            
                
                textStrng = textStrng.strip()
                
            
                if textStrng != '':
                    #time.sleep(5)
                    print ''
                    print 'Converting sentence:', textStrng, ' ...'
                    print ''
                    encodedStr = unicode(textStrng).encode('utf-8')
                    response = self.convertTextToSpeech(sound, encodedStr)
                    output = str(response['book_id'])+ '|'+ fileName + '|' + textStrng+'\n'
                    oFile.write(output)

        file.close()
        oFile.close()
            
    def convertTextToSpeech(self, sound, textString):
        # setup variables
        vars = dict(
                    api_key=self.apiKey,
                    voice=sound,
                    speed=5,
                    text=textString
                    )
        # POST data to tts function
        tts_response = json.loads(self.rest('POST', 'tts', vars))
        return tts_response

    def startDowloading(self):
        print ''
        print 'Starting dowload...'
        file = open(self.outputfile, 'r')
        for line in file:
            textStrings = line.split('|')
            if textStrings[0].isdigit():
                bookId = int(textStrings[0])
                fileName = textStrings[1]
                
                # First add cdl rights
                cdlResponse = self.addCDL(bookId)
                self.download(bookId, fileName)
        file.close()
    
    def addCDL(self, bookId):
        print ''
        print 'Adding cdl rights to '+ str(bookId)
        vars = dict(
            api_key = self.apiKey,
            book_id = bookId,
        )
        cdl_response = json.loads(self.rest('POST', 'cdl', vars))
    

    def download(self, bookId, fileName):
        print 'Getting the mp3 info...'
        vars = dict(api_key=self.apiKey, book_id=bookId, format='mp3')
        downloadResponse = json.loads(self.rest('POST', 'audio', vars))
        audioList = downloadResponse['audios']
        for audio in audioList:
            mp3file = urllib2.urlopen(audio)
            
            print 'Saving the file at ' + fileName
            output = open(fileName,'wb')
            output.write(mp3file.read())
            output.close()

def usage():
    print '\nUSAGE:\n'
    print 'yakitome.py -i <inputfile> -o <outputfile>  -l <language>'
    print ''
    
def main(argv):
   inputfile = ''
   outputfile = ''
   lang = 'E'
   try:
      opts, args = getopt.getopt(argv,"hi:o:l:",["help","ifile=","ofile=","lang="])
   except getopt.GetoptError as err:
      print str(err)
      usage()
      sys.exit(2)
      
   for opt, arg in opts:
      if opt == '-h':
         usage()
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
      elif opt in ("-l", "--lang"):
          lang = arg
   cls = YakitoMeConverter(inputfile, outputfile, lang)
   cls.startConversion()
   cls.startDowloading()

if __name__ == "__main__":
   main(sys.argv[1:])
