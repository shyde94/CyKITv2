import socket
import threading
import select
import struct
import time
import datetime
import numpy as np
from random import randint
from six.moves import cPickle



class receiverSocket():
    def __init__(self,localhost, port,channels_list):
        global eventLabel 
        self.localhost = localhost
        self.port = port
        
        self.thread1 = threading.Thread(name='clientThread', target=self.run)
        self.thread1.setDaemon = False
        self.stop_thread = False
        self.clientCyKitSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       
        self.channels = channels_list
        self.sampleReadings = []
        self.eventList = []
        self.eventLabel = '0000'
        self.filename = './EEG_Pickle_Files/'
        self.mode = '2'
        

    def start(self):
        #eventLabel = '0000'
        self.socketThreadRunning = True
        for t in threading.enumerate():
            print str(t.getName())
            if 'clientThread' == t.getName():
                print("clientThread already exists")
                return

        self.thread1.start() 

    def connect(self):
        try:
            self.clientCyKitSocket.connect((self.localhost, self.port))
            print("connection success")
        except Exception, e:
            print(e)
    
    def send_init_msg(self):
        try:
            self.clientCyKitSocket.send("GET /CyKITv2 HTTP/1.1\r\nHost: 127.0.0.1:15525\r\nConnection: Upgrade\r\nPragma: no-cache\r\nCache-Control: no-cache\r\nUpgrade: websocket\r\nOrigin: file://\r\nSec-WebSocket-Version:13\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\nSec-WebSocket-Key: E86Y2LkrfDNjc2cpFGPgbg==\r\nSec-WebSocket-Extensions: permessage-deflate; client_max_window_bits\r\n\r\n")
            #self.clientCyKitSocket.send('Start')
        except Exception:
            print(Exception)
    
    
    def run(self):
        self.socketThreadRunning = True
        self.connect()
        self.send_init_msg()
        
        
        self.now = datetime.datetime.now()    
        
        
        start = time.time()
        while self.socketThreadRunning == True:
            
            #print(start)
            try:
                #Data collection
                self.clientCyKitSocket.setblocking(0)
                ready = select.select([self.clientCyKitSocket],[],[],1)
                if ready[0]:
                    serverData = self.clientCyKitSocket.recv(1024)
                    try:
                        data = self.findChannel(self.channels,serverData)
                    except Exception, msg:
                        print("Error, findChannel() function: ", msg)
                    #data = np.asarray(data)
                   
                    
                    if data is not None:
                        #print("Inside")
                        self.sampleReadings.append(data) #store reading in list
                        
                        #For recording of events. 999 and 998 represent start and end of experiment respectively. The rest of the event labels can be customized.
                        if self.eventLabel == '999': 
                            print("Trial Start")
                            self.eventList.append(999) 
                        elif self.eventLabel == '998':
                            self.eventList.append(998)
                            print("Trial Ended")
                            break;
                        elif self.eventLabel != '' and self.eventLabel != '0000':
                            self.eventList.append(int(self.eventLabel))
                        elif self.eventLabel == '0000':
                            self.eventList.append(0)
                        else:
                            self.eventList.append(-1)
                        self.eventLabel = '0000' #reset to default event code
                        
                    #master_list.append(data)
                    end = time.time()  
                        
                
                    
            
            except Exception, e:
                print("clientThreadError: ", e)
                self.socketThreadRunning = False
                #self.clientCyKitSocket.shutdown() 
                self.clientCyKitSocket.close()
                return
        
        self.session_details, self.master_list = self.preprocessData()
        self.clientCyKitSocket.close()
            
    def findChannel(self, channels, text):
        
        '''
        Extracts channels of interest.
        Arguments: 
        channels - channels of interest 
        text - data received from cykit 
        
        Returns:
        A list containing data of each specified channel. Length of list returned = Length of argument 'channels'
        '''
        
        if(len(text)>10):
            #print(text) #for debugging purposes
            try:
                raw_data = (text.split("<split>")[2]).split(", ")
                print("raw_data: {}".format(raw_data))
            except Exception, msg:
                print("Error splitting raw data:", msg)
                return
            if(len(raw_data) <2):
               
                print(raw_data, len(raw_data))
            
            if (len(raw_data)>max(channels)):
                
                if(raw_data[1] == '16'):
                    
                    result = []
                    for channel in channels:
                        result.append(raw_data[channel])
                    print('result: {}'.format(result))
                    return result 
                
    def preprocessData(self):
        '''
        Converts self.sampleReadings into shape num_Channels * num_Samples.

        How do you want to store the data? What format?? Pickle entire numpy array. 
        
        cPickle.dump((session_detals, mater_list,ref_list),f) then extract later? Okay.
        
        
        session_details - [date_time_recorded, subject_name, self.channels]
        master_list - numpy array
            shape - (num_channels + 1, num_samples)
            [0] - sample counter
            [1:-1] - specified channels
            [-1] - event list
        ref_list - list (from ExperimentInterface.py)
            [0] - frequencies of stimulus, eg [7.5,8.57,10,...]
            [1] - stimulus frame log. Its a list of strings, eg ['000111000...', '111000111...' ...]
            [2] - event log (for debugging purposes)
        
        returns 2 variables: 
        session_details - of type list
        master_list - of type numpy array
        '''
        
        
        self.subject_name = "zhiyan"
        date_time_recorded = self.now.strftime("%Y-%m-%d %H%M")
        session_details = [date_time_recorded, self.subject_name, self.channels]
        
        
        #transpose matrix
        eeg_reading = (np.asarray(self.sampleReadings)).astype(float).T
        mode = self.mode
        file_time_log = time.time()
        file = self.filename + str(file_time_log)+'eeg'
        event_list = np.asarray(self.eventList)
        event_list = event_list.reshape(1,-1)
        
        #combine nparray containing eeg data and events into 1 matrix labeled master_list
        master_list = np.append(eeg_reading,event_list, axis=0)
        try:
            if(mode=='1'):
                np.savetxt(file+'.csv',master_list,delimiter=',')
            elif(mode=='2'):
                f = open(file+'.save', 'wb')
                cPickle.dump(master_list,f,protocol=cPickle.HIGHEST_PROTOCOL)
                f.close()
                

        except Exception:
            print("Error, could not save as csv file. Saved as backup.save instead. Use cPickle to load file")
            #backup file saved using pickle
            f = open('backup.save', 'wb')
            cPickle.dump(master_list,f,protocol=cPickle.HIGHEST_PROTOCOL)
            f.close()
            
        return session_details, master_list
        
    def testInterface(self):
        start = time.time()
        events = ['999','998','997', '996']
        while(1):
            time.sleep(0.1)
            
            #index = randint(0,len(events)-1)
            eventCode = raw_input("Event code: \n")
            self.setStimCode(eventCode)
    

    #for interface to call, changes eventLabel to be inserted into eventList
    def setStimCode(self, eventCode):
        self.eventLabel = eventCode
    
    def setRefList(self, ref_sig_list):
        self.ref_sig_list = ref_sig_list
    
    def setSubjectName(self, string):
        self.subject_name = string
        
        
if __name__ == '__main__':
    client = receiverSocket('127.0.0.1', 15525, [0,8,9])
    client.start()
    client.testInterface()