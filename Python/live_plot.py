import python_client
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from scipy import signal
from scipy.fftpack import fft


fig1 = plt.figure(figsize=(20,5))
fig2 = plt.figure(figsize=(20,5))



ax1 = fig1.add_subplot(1,1,1)
ax2 = fig2.add_subplot(1,1,1)


class LivePlotter():
    
    def __init__(self, dataReceiver, sample_rate, max_duration):
        self.client = dataReceiver
        self.sample_rate = sample_rate
        self.max_range = sample_rate * max_duration    
        #self.counter = counter #keep track of which sample number you are looking at
        self.ax1 = ax1
        self.ax2 = ax2 
        self.tracker = 0
        self.y_scale = (-200,200) #set default scale
        
    def calculate(self):
        #you only want to display a certain range. you want it to be live..up till that range and then the graph gets cleaned. 
        #so, you need to maintain a count on the length of client.sampleReadings. So that you know where to start from. 
        self.anchorPoint = self.tracker * self.max_range
        #print("anchorPoint: ", anchorPoint)
        data = client.sampleReadings
        eeg_reading = (np.asarray(data)).astype(float)
        eeg_reading = eeg_reading[self.anchorPoint:,:].T #mark starting point
        length = eeg_reading.shape[1] #get number of samples read in from anchorpoint till current time
        
        #print('length: ', length)
        if (length >= self.max_range):
            self.tracker += 1
        if length>self.max_range:
            increase = self.max_range
        else: 
            increase = length
        x = np.arange(self.anchorPoint, self.anchorPoint + increase)
        return x, eeg_reading
        
       
    def minMaxAxis(self,x):
        #x is a tuple, determine y_lim for graphs
        a = x[0]
        b = x[1]
        
        if(abs(a-b) > 1000):
            #self.y_scale = x
            return x
        else:
            #print("too small")
            return (self.y_scale[0],self.y_scale[1]) 
            #pass
   
    

def animate(i):
        try:
            x, readings = livePlot.calculate()
            #print('x: ', x)
            o1 = readings[1,:]
            o2 = readings[2,:]
            
            o1 = signal.detrend(o1)
            o2 = signal.detrend(o2)
            #print('o1 shape', o1.shape)
            #print('o2 shape', o2.shape)
            
            ax1.clear()
            ax2.clear()
            ax1.plot(x,o1)
            ax2.plot(x,o2)
            
            o1_y_axis_range = ax1.get_ylim()
            o2_y_axis_range = ax2.get_ylim()
            
            o1_min, o1_max = livePlot.minMaxAxis(o1_y_axis_range)
            o2_min, o2_max = livePlot.minMaxAxis(o2_y_axis_range)
            
            
            ax1.set_xlim(livePlot.anchorPoint, livePlot.anchorPoint+livePlot.max_range)
            ax2.set_xlim(livePlot.anchorPoint, livePlot.anchorPoint+livePlot.max_range)
            
            ax1.set_ylim([o1_min,o1_max])
            ax2.set_ylim([o2_min,o2_max])
            ax1.set_title('O1 readings')
            ax2.set_title('O2 readings')
            
            
        except Exception, msg:
            print("Error Plotting graphs", msg)
         


            
client = python_client.receiverSocket("127.0.0.1", 15525, [0,8,9])
client.start()
livePlot = LivePlotter(client, 128,5)            
            
if __name__ == "__main__":
    print("start live plot")    
    ani = animation.FuncAnimation(fig1, animate, interval=100)
    ani2 = animation.FuncAnimation(fig2, animate, interval=100)
    plt.show()

def plotGraphs():
    ani = animation.FuncAnimation(fig1, animate, interval=10)
    ani2 = animation.FuncAnimation(fig2, animate, interval=10)
    plt.show()
    