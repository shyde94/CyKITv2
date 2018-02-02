'''
Event codes:
999 - Experiment starts
998 - Experiment ends
 

eeg data recording matrix: 
index:
[0] - sample number (0-127)
[1]
...
[-1] - event codes


Modified version of Data_Analysis for pull request with CyKitV2. 

Takes in EEG data only, no reference signals (eg. visual stimulus). Samples and event labels will be returned in edf events format (similar to how the MNE Library organises its event labels and samples for edf files)
'''
from six.moves import cPickle
import numpy as np
import csv
from scipy import signal
import matplotlib.pyplot as plt
from scipy.fftpack import fft

#for offline analysis
class DataAnalyser():
    #Previous constructor, for 2 file names
    def __init__(self, eeg_data_filename, all_event_codes,sample_rate_x=60, sample_rate_y=128):
        self.file = eeg_data_filename
        
        self.event_codes = all_event_codes
        
        self.sample_rate_x = sample_rate_x
        self.sample_rate_y = sample_rate_y 
        self.num_training_samples = 0
        self.num_correct = 0
        self.num_wrong = 0

        self.fileHandler()
        self.eegDataHandler()
        #self.refSigHandler()
    '''
    #New constructor for 1 filename (ref_sig and eeg are combined in 1 file)
    def __init__(self, combined_filename, all_event_codes,sample_rate_x=60, sample_rate_y=128,cca_mode=0,cca_interval=0.25,cca_squareOrSine=0,cca_delay_min=13, cca_delay_max=23):
        self.file = combined_filename
        self.event_codes = all_event_codes
        
        self.sample_rate_x = sample_rate_x
        self.sample_rate_y = sample_rate_y
        self.num_training_samples = 0
        self.num_correct = 0
        self.num_wrong = 0
        
        self.cca_mode = cca_mode
        self.cca_interval = cca_interval
        self.cca_squareOrSine = cca_squareOrSine
        self.cca_delay_min = cca_delay_min
        self.cca_delay_max = cca_delay_max

        self.fileHandler()
        self.eegDataHandler()
        self.refSigHandler()
    '''
    def fileHandler(self):
        f = open(self.file,'rb')
        self.session_details, self.data = cPickle.load(f)
        f.close()
    
    def eegDataHandler(self):
        try:
            eeg_readings = self.data[0:-2]
            length = np.arange(eeg_readings.shape[1])
            
            fig1 = plt.figure(figsize=(20,6))
            for i in range(eeg_readings.shape[0]):
                ax1 = fig1.add_subplot(2,1,i+1)
                plt.plot(length, eeg_readings[i,:])
                ax1.set_ylabel("channel {}".format(i+1))
    
            plt.show()
            plt.close()
            
            #Get event list
            event_channel = self.data[-1,:]
            
            filtered_event_list = []
            sample_index = []
            
            #Get sample number that coincides with each event. 
            for i in range(event_channel.shape[0]):
                if (event_channel[i] != 0):
                    filtered_event_list.append(event_channel[i])
                    sample_index.append(i)
            self.filtered_event_list = np.asarray(filtered_event_list).astype(int)
            self.sample_index = np.asarray(sample_index)
            
            print("List of events: {}".format(self.filtered_event_list))
            print("List of sample indexes: {}".format(self.sample_index))
            
        except Exception, e:
            print("eegDataHandler, Error opening file, ", e )
            return
        
            
    '''  
    def refSigHandler(self):
        
        #Convert ref signal format from ['11100111..', '1010101...' ,...] to a matrix of shape (num_ref_sig, num_samples)
        
        try:
            #f = open(self.ref_filename,'rb')
            #ref_sig = cPickle.load(f)
            #f.close()
            
            #Get list of all frequencies used during the trial
            ref_sig = self.ref_sig_list
            
            self.freq_list = ref_sig[0][0]
            print('a', self.freq_list)
            self.interval = ref_sig[0][1] #duration of minitrial
            print('b', self.interval)
            #Get actual data of all the signals used
            stimulus_list = np.asarray(ref_sig[1])
            ref_sig_list = []
            for stimulus in stimulus_list:
                ref_sig_list.append(list(stimulus))
            
            #replace self.ref_sig_list with matrix instead of list of strings
            self.ref_sig_list = np.asarray(ref_sig_list).astype(int)
            self.event_codes = self.event_codes + (np.arange(100,100+len(self.freq_list))).tolist()
            
            #Check frequencies of reference signal to ensure that they are correct to begin with
            targetRefSignal = self.ref_sig_list[:,0:int(self.sample_rate_x * self.interval)+1]
            self.findFreqFFT(targetRefSignal.T,self.sample_rate_x)
            
        except Exception, e:
            print("refSigHandler, Error opening file, ", e)
            return
    ''' 

    '''
    def Analyse(self):
        
        self.results_comparison_dict = {}
        print("\n\n>>>>> Analysis of EEG Data <<<<<<\n\n")
        print(self.freq_list)
        for freq in range(len(self.freq_list)):
            #Acquire start and end of mini trials from event list
            start_list = []
            end_list = []
            results = []
            freq_code = (np.arange(100,100+len(self.freq_list)))[freq]
            print(freq_code, "freq: " , self.freq_list[freq])
            for i in range(len(self.filtered_event_list) - 2):
                if self.filtered_event_list[i] == freq_code:
                    start_list.append(self.sample_index[i+1])
                    end_list.append(self.sample_index[i+2])
            print(start_list)
            print(end_list)
            eeg_data = self.data[1:-1,:]
            for start, stop in zip(start_list, end_list):
                # Should EEG Samples be detrended first before applying CCA? Hmmm
                targetEEGSamples = eeg_data[:,start:stop+1].T
                self.findFreqFFT(targetEEGSamples,self.sample_rate_y)
                targetRefSignal = self.ref_sig_list[:,0:int(self.sample_rate_x * self.interval)+1]
                #self.findFreqFFT(targetRefSignal.T,60)
                ccaEngine = cca_V2.EngineCCA(targetRefSignal, targetEEGSamples, self.freq_list,self.sample_rate_x, self.sample_rate_y,interval=self.cca_interval, mode = self.cca_mode, squareOrSine = self.cca_squareOrSine, delay_min = self.cca_delay_min, delay_max = self.cca_delay_max)
                stimuli = ccaEngine.get_stimulus()
                results.append(stimuli)
                self.num_training_samples +=1
                if(self.freq_list[freq] == stimuli):
                    self.num_correct += 1
                else:
                    self.num_wrong +=1
            self.results_comparison_dict[self.freq_list[freq]] = results
            #self.cca_engine_attributes_dict = ccaEngine.__dict__

            
            print("Results using CCA: " , results, 'stimulus freq:', self.freq_list[freq])
            print("\n\n")
        
        

        print('a',self.num_training_samples)
        print('b',self.num_correct)
        #print('c',self.num_wrong)
        self.accuracy = (self.num_correct / float(self.num_training_samples))* 100
        print("Accuracy:" , self.accuracy)
        
        self.recordAttributes()
            
    '''  
    def recordAttributes(self):
        #Should improve data recording format. This method is inefficient when i want to analyse all the data to look for trends. 
        #Record all attributes for this Analyzer object? 
        '''
        Header : file,session_details,num_correct,num_wrong,num_training_samples,mini_trial_duration,accuracy,results_comparison_dict,sample_rate_x,sample_rate_y,cca_mode,cca_interval,cca_squareOrSine,cca_delay_min,cca_delay_max
 
        file | Session details | num_correct | num_wrong | num_training_samples | accuracy | results_comparison_dict | event_codes | sample_rate_x | sample_rate_y | cca_mode | cca_squareOrSine | cca_delay_min | cca_delay_max
        '''
        fieldnames = ['file', 'session_details', 'num_correct', 'num_wrong', 'num_training_samples', 'interval', 'accuracy', 'results_comparison_dict', 'sample_rate_x', 'sample_rate_y','cca_mode', 'cca_interval', 'cca_squareOrSine','cca_delay_min', 'cca_delay_max']
        myDict = self.__dict__
        #print(myDict)
        values = []
        for key in fieldnames:
            values.append(myDict[key])
        print(values)    
        with open('Record1.csv','a+') as f:
            writer = csv.writer(f)
            #if(csv.Sniffer().has_header(f.read(1024)) == False):
            #    writer.writerow(fieldnames)
            writer.writerow(values)   
        '''
        inputData = [self.eeg_filename, self.ref_filename, results, targetFreq]
        with open('Temp_Results_19012018.csv','a') as f:
            writer = csv.writer(f)
            writer.writerow(inputData)
        '''
    

    def findFreqFFT(self, data, sample_rate):
        #Finds frequency of input signal
        #Need to include some sort of high pass filter to remove 0,0.1 Hz nonsense
        #arguments: 
        # data - shape (num_samples * num_channels)
        N_samples = data[:,0].shape[0]
        print('N_samples', N_samples)
        for i in range (data.shape[1]):
            channel = i
            print("channel:", channel)
            data_d = signal.detrend(data[:,channel])
            #time = np.arange(N_samples)
            time = np.linspace(0,self.interval,N_samples) #this time...you are assuming that all samples will be delivered. should take, self.interavl instead of N_sampels//sample_rate_y
            fig1 = plt.figure(figsize=(20,5))
            ax1 = fig1.add_subplot(2,1,1)
            ax1.plot(time, data_d)
            ax1.set_ylabel('EEG Readings')
            ax1.set_xlim(0,self.interval)    
            #data_d = data[:,channel] - np.mean(data[:,channel])
            fft_sample = fft(data_d)
            #sample_rate = 128
            xf = np.linspace(0, sample_rate//2, N_samples//2, endpoint=False)
            ax2 = fig1.add_subplot(2,1,2)
            yf = np.abs(fft_sample[:N_samples//2] * 2.0/N_samples)
            #yf = yf[50:100]
            
            #xf = xf[50:100]
            ax2.plot(xf, yf)
            ax2.set_ylabel('Frequency in Hz')
            plt.show()
            print("max frequency: ", xf[np.argmax(yf)])


if __name__ == '__main__':
    
    filename1 = './EEG_Pickle_Files/1517552237.66eeg.save'
    
    event_list = [999,998,997,996]
    
    analyzer = DataAnalyser(filename1,event_list)
    
        
        
        
            
    