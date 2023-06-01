import json, os, csv
import numpy as np

def extract_arrow_stats(json_file_path):
    with open(json_file_path, 'r') as file:
        eeg_data = json.load(file)
        eeg_data = np.array(eeg_data)
        marker_strings = eeg_data[:, 5]
        marker_timestamp = eeg_data[:, 0]

        left_arrow_delay = []
        right_arrow_delay = []
        stats = {'Dir_Missed_pcg':0, 'Dir_Wrong_pcg':0, 'Dir_empty_call':0, 'L_correct': 0, 'L_missed': 0, 'L_wrong': 0, 'R_correct': 0, 'R_missed': 0, 'R_wrong': 0, 'L_delay_avg': 0, 'R_delay_avg':0, 'L_delay_std': 0, 'R_delay_std':0}
        prev_left = False
        prev_right = False

        for i in range(len(marker_strings)):
            value = marker_strings[i]
           
            timestamp = float(marker_timestamp[i])

            if value == "left arrow":
                if prev_left:
                    left_arrow_delay.append(timestamp - prev_left_timestamp)
                    prev_left = False
                elif prev_right:
                    stats['R_wrong'] += 1
                else:
                    stats['Dir_empty_call'] += 1

            elif value == "right arrow":
                if prev_right:
                    right_arrow_delay.append(timestamp - prev_right_timestamp)
                    prev_right = False
                elif prev_left:
                    stats['L_wrong'] += 1
                else:
                    stats['Dir_empty_call'] += 1

            elif value == "left":
                if prev_left:
                    stats['L_missed'] += 1
                if prev_right:
                    stats['R_missed'] += 1
                
                prev_left = True
                prev_right = False
                prev_left_timestamp = timestamp

            elif value == "right":
                if prev_left:
                    stats['L_missed'] += 1
                if prev_right:
                    stats['R_missed'] += 1
                
                prev_right = True
                prev_left = False
                prev_right_timestamp = timestamp

        if prev_left:
            stats['L_missed'] += 1
        if prev_right:
            stats['R_missed'] += 1

        stats['L_correct'] = len(left_arrow_delay)
        stats['R_correct'] = len(right_arrow_delay)
        tot_correct = stats['L_correct'] + stats['R_correct']

        stats['L_delay_avg'] = np.mean(left_arrow_delay)
        stats['R_delay_avg'] = np.mean(right_arrow_delay)

        stats['L_delay_std'] = np.std(left_arrow_delay)
        stats['R_delay_std'] = np.std(right_arrow_delay)

        stats['Dir_Missed_pcg'] = (stats['L_missed'] + stats['R_missed']) / tot_correct *100
        stats['Dir_Wrong_pcg'] = (stats['L_wrong'] + stats['R_wrong']) / tot_correct *100

    return left_arrow_delay, right_arrow_delay, stats

#-------------

# json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_04_2.json')
# left_arrow_delay, right_arrow_delay, stats = extract_arrow_stats(json_file_path)
# print(stats)

#----------------------------

def merge_obj_performance(circles_file_path, eeg_json_path):

    with open(circles_file_path, 'r') as file:
        reader = csv.reader(file)
        header = next(reader) #leave
        first_row = next(reader)
        true = float(first_row[0])
        reported = float(first_row[1])
        error = reported-true
        error_pcg = error/true *100

        left_arrow_delay, right_arrow_delay, stats = extract_arrow_stats(eeg_json_path)

        performance = {}
        performance['Cir_Error_pcg'] = error_pcg
        performance['Cir_Error'] = error
        for key in stats.keys():
            performance[key] = stats[key]
        performance['L_delay_array'] = left_arrow_delay
        performance['R_delay_array'] = right_arrow_delay


    
    return performance

#--------------

# circles_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data', 'AudioVisual', '04', '2', 'blue_circles.csv')
# eeg_json_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_04_2.json')
# new_file_json = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'results_data', 'Arrow_Circles_performance.json')


# performance = merge_obj_performance(circles_file_path, eeg_json_path)
# all_performances = {}
# all_performances['AudioVisual_04_2'] = performance

# json_data = json.dumps(all_performances, indent=4)

# with open(new_file_json, 'w') as file:
#     file.write(json_data)
#     print("New file at ", new_file_json)
