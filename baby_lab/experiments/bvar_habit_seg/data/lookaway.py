#given a data bvar_habit_seg filename as a command line option, print out the total looking and away times for the data, i.e. the sums of all looking and away events from beginning to end of the experiment

import os, sys

file_name = sys.argv[1]

lines = [ line for line in open(file_name) ]
look_record =[ float(item) for item in  lines[0].split(',')[1:] ]
stimuli_record = lines[1].split(',')[1:]

def sum_periods(start_index, stop_index, look_record):
  #calculate looking and away times between to indexes in the look_record
  looking = 0
  away = 0
  current_index = start_index
  if start_index == stop_index or start_index > stop_index:
    return (0,0)
  while current_index != stop_index:
    if current_index % 2 == 0:
      looking += look_record[current_index + 1] - look_record[current_index]
      current_index += 1
      continue
    else:
      away += look_record[current_index + 1] - look_record[current_index]
      current_index += 1
      continue
  return (looking, away)

looking, away = sum_periods(0, len(look_record)-1, look_record)
print "LOOKING: ", looking
print "AWAY: ", away
