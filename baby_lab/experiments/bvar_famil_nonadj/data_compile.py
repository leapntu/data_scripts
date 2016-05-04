import sys, os
data_dir = "./data/"
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
    fam_record = []
    stimuli_record = []
    total_fam = 0
    lines = [ line.strip().split(',') for line in open(data_dir+file_name) ][1:]
    fam_record = [ (stim, float(rt)) for sub, stim, rt, data_type in lines if data_type == "lookingFam" ]
    stimuli_record = [ (stim.strip(), float(rt), data_type.strip()) for sub, stim, rt, data_type in lines if data_type in ["under2", "over2", "full_look", "end_while_away"] ]
    total_fam = [ float(rt) for sub, stim, rt, data_type in lines if data_type == "totalPlaying-Fam"][0]
    return (subject_num,
            { 'meta': { 'subject_num': subject_num,
                        'baby_name': baby_name},
              'total_fam': total_fam,
              'fam_record': fam_record,
              'stimuli_record': stimuli_record
              })

def raw_to_full(subject_num, data, df):
    train_looking = sum([ rt for stim, rt, in data['fam_record'] ])
    train_away = data['total_fam'] - train_looking
    train_looking_prop = train_looking / data['total_fam'] 
    test_results = []
    order = 1
    stats = {}
    for stim_name, rt, stim_type in data["stimuli_record"]:
      stats[stim_name] = [0,0] #[looking time , away time]
    for stim_name, rt, stim_type in data["stimuli_record"]:
      if stim_type in ["over2", "end_while_away", "full_look"]:
        stats[stim_name][0] += rt
        if stim_type == "over2":
          stats[stim_name][1] += 2000
        if stim_type == "end_while_away":
          stats[stim_name][1] += 21800 - rt
      if stim_type == "under2":
        stats[stim_name][1] += rt
    for stim_name, rt, stim_type in [ (stim, float(rt), data_type) for stim, rt, data_type in data["stimuli_record"] if data_type in ["over2", "full_look", "end_while_away"]]:
      file_id = stim_name.split('-')[0]
      file_type = file_id.split('.')[1]
      looking = stats[stim_name][0]
      away = stats[stim_name][1]
      record_result = (file_id, file_type, looking, away, order, train_looking, train_away, train_looking_prop)
      test_results.append(record_result)
      order += 1
    df[subject_num] = {'test_results': test_results}

def build_full_data(raw_data, df):
    for subject_num, data in raw_data.items():
        raw_to_full(subject_num, data, df)

def output_basic_data_frame(df):
    output = open("df.csv","w")
    header = "id, stimuli, type, looking, away, order, train_looking, train_away, train_looking_prop" + "\n"
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
