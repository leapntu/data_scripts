import sys, os
data_dir = "./data/raw/"
data_files = os.listdir(data_dir)
baby_data_raw = {}
baby_data_full = {}

def read_files(file_names, df):
    for file_name in file_names:
        subject_num, raw_data = read_file(file_name)
        df[subject_num] = raw_data
        
def read_file(file_name):
    meta_data = file_name.split('_')
    subject_num = meta_data[0]
    baby_name = meta_data[1]
    age = meta_data[2]
    ra = meta_data[3][:-4]
    look_record = []
    stimuli_record = []
    lines = [ line for line in open(data_dir+file_name) ]
    look_record =[ float(item) for item in  lines[0].split(',')[1:] ]
    stimuli_record = lines[1].split(',')[1:]

    return (subject_num,
            { 'meta': { 'subject_num': subject_num,
                        'baby_name': baby_name,
                        'age': age,
                        'ra': ra},
              'look_record': look_record,
              'stimuli_record': stimuli_record
              })

def sum_periods(start_index, stop_index, look_record):
  #calculate looking and away times between to indexes in the look_record
  looking = 0
  away = 0
  current_index = start_index
  print "PER", start_index, stop_index, len(look_record)
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

def sum_between(start_time, stop_time, look_record):
  #given two time points, calculate total looking and away times between them
  looking = 0
  away = 0
  start_index = 'none'
  stop_index = 'none'

  
  for index, time in enumerate(look_record):
    if start_index == 'none' and time > start_time:
      start_index = index
      break
    if start_index == 'none' and index == len(look_record) - 1:
      start_index = 'max'
  for index, time in enumerate(look_record[::-1]):
    if stop_index == 'none' and time < stop_time:
      stop_index = len(look_record) - 1 - index
      break
      
  if type(start_index) == type(0) and type(stop_index) == type(0):
    looking, away = sum_periods(start_index, stop_index, look_record)
    if start_index > stop_index:
      if stop_index % 2 == 0:
        looking += stop_time - start_time
      else:
        away += stop_time - start_time
      return (looking, away)
    
    if start_index % 2 == 0:
      away += look_record[start_index] - start_time
    else:
      looking += look_record[start_index] - start_time
    if stop_index % 2 == 0:
      looking += stop_time - look_record[stop_index]
    else:
      away += stop_time - look_record[stop_index]
    return (looking,away)

  elif start_index == 'max':
    distance = stop_time - start_time
    last_index = len(look_record) - 1
    if last_index % 2 == 0:
      looking += distance
    else:
      away += distance
    return (looking, away)

def raw_to_full(subject_num, data, df):
    print data['meta']['baby_name']
    total_looking, total_away = sum_periods(0, len(data['look_record']) -1, data['look_record'])
    test_record = [ item for item in data['stimuli_record'] if item.find("test") > -1 ]
    test_looking, test_away = sum_between(float(test_record[0].split(';')[1]), float(test_record[-1].split(';')[1]), data['look_record'])
    total_looking_prop =  total_looking / (total_looking + total_away)
    train_looking = 0
    train_away = 0
    train_looking_prop = 0
    test_results = []
    
    start = 0
    stop = 1
    while start < len(test_record) - 1:
        begin_look = float(test_record[start].split(';')[1])
        end_look = float(test_record[stop].split(';')[1])
        print "TIME", begin_look, end_look
        record_looking, record_away = sum_between(begin_look, end_look, data['look_record'])        
        train_looking += record_looking
        train_away += record_away
        start += 2
        stop += 2
    train_looking_prop =  train_looking / (train_looking + train_away)
    
    start = 0
    stop = 1
    order = 1
    while start < len(test_record) - 1:
        file_name = test_record[start].split(';')[0].replace('_','.').split('.')[4]
        begin_look = float(test_record[start].split(';')[1])
        end_look = float(test_record[stop].split(';')[1])
        condition = 'NA'
        if file_name in ["dafa", "drogu","pagu", "zeka"]:
          condition = "part"
        elif file_name in ["fama","pera","kadro","zupa"]:
          condition = "word"
        record_looking, record_away = sum_between(begin_look, end_look, data['look_record'])
        record_results = (file_name, condition, record_looking, record_away, order, train_looking, train_away, train_looking_prop, total_looking, total_away, total_looking_prop)
        test_results.append(record_results)
        start += 2
        stop += 2
        order += 1

    df[subject_num] = {'test_results': test_results}

def build_full_data(raw_data, df):
    for subject_num, data in raw_data.items():
        raw_to_full(subject_num, data, df)

def output_basic_data_frame(df):
    output = open("df.csv","w")
    header = "id, stimuli, condition, looking, away, order, train_looking, train_away, train_looking_prop, total_looking, total_away, total_looking_prop" + "\n"
    output.write(header)
    for baby, data in df.items():
        for result in data['test_results']:
            data_out = "" + baby
            for datum in result:
                data_out += "," + str(datum)
            output.write(data_out + "\n")
    output.close()

def main():
    read_files(data_files[:], baby_data_raw)
    build_full_data(baby_data_raw, baby_data_full)
    output_basic_data_frame(baby_data_full)
    return baby_data_full

main()
data = baby_data_full
