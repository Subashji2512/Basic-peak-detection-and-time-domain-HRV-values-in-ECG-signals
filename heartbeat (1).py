import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import heartbeat as hb #Assuming we named the file 'heartbeat.py'

measures = {}

def get_data(filename):
    dataset = pd.read_csv(filename)
    return dataset

def process(dataset, hrw, fs):#Remember; hrw was the one-sided window size (we used 0.75) and fs was the sample rate (file is recorded at 100Hz)
    rolmean(dataset, hrw, fs)
    detect_peaks(dataset)
    calc_RR(dataset, fs)
    calc_ts_measures()
    

def rolmean(dataset, hrw, fs):
    mov_avg = dataset['hart'].rolling(int(hrw*fs)).mean()
    avg_hr = np.mean(dataset.hart)
    mov_avg = [avg_hr if math.isnan(x) else x for x in mov_avg]
    mov_avg = [x*1.2 for x in mov_avg]
    dataset['hart_rollingmean'] = mov_avg

def detect_peaks(dataset):
    window = []
    peaklist = []
    listpos = 0
    for datapoint in dataset.hart:
        rollingmean = dataset.hart_rollingmean[listpos]
        if (datapoint < rollingmean) and (len(window) < 1):
            listpos += 1
        elif (datapoint > rollingmean):
            window.append(datapoint)
            listpos += 1
        else:
            maximum = max(window)
            beatposition = listpos - len(window) + (window.index(max(window)))
            peaklist.append(beatposition)
            window = []
            listpos += 1
    measures['peaklist'] = peaklist
    measures['ybeat'] = [dataset.hart[x] for x in peaklist]


    
def calc_RR(dataset, fs):
    peaklist = measures['peaklist']
    RR_list = []
    Hr=[]
    cnt = 0
    
    while (cnt < (len(peaklist)-1)):
        RR_interval = (peaklist[cnt+1] - peaklist[cnt])
        ms_dist = ((RR_interval / fs) * 1000.0)
        ms_hr=(60000/ms_dist)
        RR_list.append(ms_dist)
        Hr.append(ms_hr)
        cnt += 1
    RR_diff = []
    RR_sqdiff = []
    cnt = 0
    
    while (cnt < (len(RR_list)-1)):
        RR_diff.append(abs(RR_list[cnt] - RR_list[cnt+1]))
        RR_sqdiff.append(math.pow(RR_list[cnt] - RR_list[cnt+1], 2))
        cnt += 1
    
    measures['RR_list'] = RR_list
    measures['RR_diff'] = RR_diff
    measures['RR_sqdiff'] = RR_sqdiff
    measures['Hr'] = Hr

def calc_ts_measures():
    RR_list = measures['RR_list']
    RR_diff = measures['RR_diff']
    RR_sqdiff = measures['RR_sqdiff']
    Hr=measures['Hr']
    
    measures['bpm'] = 60000 / np.mean(RR_list)
    measures['max bpm']=np.max(Hr)
    measures['min bpm']=np.min(Hr)
    measures['ibi'] = np.mean(RR_list)
    measures['sdnn'] = np.std(RR_list)
    measures['sdsd'] = np.std(RR_diff)
    measures['rmssd'] = np.sqrt(np.mean(RR_sqdiff))
    NN20 = [x for x in RR_diff if (x>20)]
    NN50 = [x for x in RR_diff if (x>50)]
    measures['nn20'] = NN20
    measures['nn50'] = NN50
    measures['pnn20'] = float(len(NN20)) / float(len(RR_diff))
    measures['pnn50'] = float(len(NN50)) / float(len(RR_diff))
   

dataset = hb.get_data('data 6.csv')

hb.process(dataset, 0.75, 100)
print("THE AVG BPM  IS",measures['bpm'] )
print("THE IBI IS",measures['ibi'] )
print("THE SDNN IS", measures['sdnn'])
print("THE SDSD IS", measures['sdsd'])
print("THE RMSSD IS", measures['rmssd'])
print("THE PNN20 IS", measures['pnn20'])
print("THE PNN50 IS", measures['pnn50'])
print("THE MAX BPM", measures['max bpm'])
print("THE MIN BPM", measures['min bpm'])
if measures['bpm']>56 and measures['bpm']<65:
    print("YOU HAVE A STABLE HEART RATE")
elif measures['bpm']>250 and measures['bpm']<360:
    print("YOU HAVE A STABLE HEART RATE")
else:
    print("YOU DIDN'T HAVE A STABLE HEART RATE")
plt.subplot(1,1,1)
peaklist = measures['peaklist']
ybeat = measures['ybeat']
plt.title("HEARTBEAT PLOT")
plt.plot(dataset.hart, alpha=0.5, color='blue', label="raw signal")
plt.scatter(peaklist, ybeat, color='red', label="average: %.1f BPM" %measures['bpm'])
plt.legend(loc=4, framealpha=0.6)
plt.show()



