import mne, os
from eeg_analysis_lib import create_raw_object
import numpy as np


def extract_direction_evoked(raw, plot_display=False):
    marker_mapping = {"blue": 1, "red": 2, "right": 3, "left": 4, "right arrow": 5, "left arrow": 6}
    events, event_id= mne.events_from_annotations(raw, event_id=marker_mapping)
    filtered_raw = raw.copy().filter(l_freq=0.1, h_freq=40, fir_design='firwin')
    duration = 30.0  # Duration of each epoch (seconds)

    # Extract epochs
    epochs = mne.Epochs(filtered_raw, events, event_id=event_id, tmin=-0.3, tmax=0.7, baseline=None, preload=True, event_repeated='merge')
    # fig = epochs.plot(events=events)

    # #TODO 
    # reject_criteria = dict(eeg=100e-6)  # 100 µV, 200 µV
    # epochs.drop_bad(reject=reject_criteria)
    # or directly 
    # reject_threshold = 200.0  # Threshold for epoch rejection (microvolts)
    # # reject=dict(eeg=reject_threshold)
    # epochs.plot_drop_log()

    # Get unique event types from annotations
    event_types = np.unique(events[:, -1])

    l = epochs["left"].average()
    r = epochs["right"].average()
    fig1 = l.plot(titles="Left event")
    fig2 = r.plot(titles="Right event")
    
    # Mean and Std across epochs, both left and right
    evokeds = dict(
        left=list(epochs["left"].iter_evoked()),
        right=list(epochs["right"].iter_evoked()),
    )

    if plot_display:
        l.plot_topomap(times=[-0.2, 0.3, 0.5], average=0.05, title="Left event")
        l.plot_joint(title="Left event")
        r.plot_topomap(times=[-0.2, 0.3, 0.5], average=0.05, title="Right event")
        r.plot_joint(title="Right event")


        l.plot(gfp=True, spatial_colors=True, titles="Left event")
        r.plot(gfp=True, spatial_colors=True, titles="Right event")

        mne.viz.plot_compare_evokeds(evokeds, combine="mean")

    return evokeds 

json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_04_1.json')
raw = create_raw_object(json_file_path)
evoked = extract_direction_evoked(raw, plot_display=True)

#--------------------OTHER

# mne.viz.plot_compare_evokeds({'mean': allEvokeds}, ylim=dict(eeg=[-5,5]), picks=picks,
#                              title=None, axes=axes, ci=0.95, show_sensors=False, 
#                              truncate_yaxis = False, truncate_xaxis=False, legend=False,
#                              colors = {'mean': '#808080'}, combine=None)

#-------TODO all ERP 

# # Create evoked objects for each event type and channel
# evokeds = {}
# for event_type in event_types:
#     evokeds[event_type] = {}
#     for ch_name in raw.info['ch_names']:
#         print(epochs)
#         evokeds[event_type][ch_name] = epochs[event_type].average(picks=ch_name)#TODO how erp exctraction, window? average?

# # Plot evoked potentials (ERPs) for each event type and channel
# for event_type in event_types:
#     for ch_name in raw.info['ch_names']:
#         evokeds[event_type][ch_name].plot()
