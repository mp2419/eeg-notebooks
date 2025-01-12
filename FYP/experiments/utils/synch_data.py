# - read two csv
# - get timestamp of marker and see when next timestamp of recording is bigger that marker, add marker in recording and iterate for each marker
# - new csv with sync data between marker and recording data

import csv
import numpy as np
import sys
sys.path.append("..\\")
sys.path.append("C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP")
import utils.data_analysis.trim_data as trim

def merge_data(filename_raw, filename_marked, filename_union):

    # Open the two CSV files and the output CSV file
    with open(filename_raw, 'r') as raw, open(filename_marked, 'r') as markers, open(filename_union, 'w', newline='') as merged:
        # Create CSV readers for both files and a writer for the output file
        # reader1 = np.genfromtxt(raw, delimiter=',', skip_header=1)
        csv_reader1 = csv.reader(raw)
        data = [row for row in csv_reader1]

        data_rows = []
        for row in data[1:]:
            n0 = float(row[0])
            n1 = float(row[1])
            n2 = float(row[2])
            n3 = float(row[3])
            n4 = float(row[4])
            data_rows.append((n0,n1,n2,n3,n4))
        reader1 = np.array(data_rows)

        #----------

        csv_reader2 = csv.reader(markers)
        data = [row for row in csv_reader2]
        data_tuples = []
        for row in data[1:]:
            float_val = float(row[0])
            string_val = row[1]
            data_tuples.append((float_val, string_val))
        reader2 = np.array(data_tuples)

        #----------

        writer = csv.writer(merged)
        writer.writerow(['Timestamp','TP9','AF7','AF8','TP10','Marker', 'Marker_timestamp'])
        idx1 = 0
        row_newfile = []
        done = False
        rows = reader2[idx1]
        for i in reader1:
            # print(rows[0], i[0])
            if (float(rows[0]) < float(i[0])) & (done == False):
                row_newfile = [i[0],i[1],i[2],i[3],i[4],rows[1], rows[0]] 
                #print('new event: ', idx1)
                if idx1 == len(reader2)-1:
                    print('All events recorderd')
                    done = True
                else:
                    idx1 = idx1+1
                    rows = reader2[idx1]
            else:
                row_newfile = [i[0],i[1],i[2],i[3],i[4],'n/a', '']
            
            writer.writerow(row_newfile)
            
    #TODO fix end does not get cut off the first time
    trim.trim(filename_union)
    trim.trim(filename_union)
    print(" -> New merged file at ", filename_union)

    # return filename_union

new_file = merge_data(filename_raw = 'C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\ShapeVisual\\17\\1\\eeg.csv', 
            filename_marked =  'C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\ShapeVisual\\17\\1\\markers.csv',
            filename_union = 'C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\ShapeVisual\\17\\1\\synched_data.csv')



