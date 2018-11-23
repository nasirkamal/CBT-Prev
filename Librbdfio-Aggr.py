#Usage: python Aggr_Results.py /path/to/cbt/archive
#This code only works for Librbdfio
#
#!/usr/bin/python
import sys
import os
import glob
import json
import yaml

print_all_entries = False

path = sys.argv[1]
f_name = path + "/results/cbt_config.yaml"

def get_parameters(file_name):
    my_dict = {}
    with open(f_name, 'r') as stream:
        try:
            data = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    my_dict['clients'] = data['cluster']['clients']
    my_dict['osds'] = data['cluster']['osds']
    my_dict['op_size'] = data['benchmarks']['librbdfio']['op_size']
    my_dict['volumes_per_client'] = data['benchmarks']['librbdfio']['volumes_per_client']
    my_dict['vol_size'] = data['benchmarks']['librbdfio']['vol_size']
    my_dict['mode'] = data['benchmarks']['librbdfio']['mode']
    my_dict['total_client_procs'] = len(data['cluster']['clients']) * data['benchmarks']['librbdfio']['volumes_per_client']
    return my_dict

def load_yaml(file_path):
    with open(file_path, 'r') as stream:
        try:
            data = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return data

print '\n'        
my_dict = get_parameters(f_name)
print 'Test Parameters:'
print '----------------'
for x in my_dict:
    print x + ' : ' + str(my_dict[x])


print '\n'
for x in os.walk(path):
    if len(x[2]) > 2:
        write_iops = 0.0
        read_iops = 0.0
        write_bw = 0.0
        read_bw = 0.0
        write_lat = 0.0
        read_lat = 0.0
        n = 1
        missed = 0
        exp_yaml = x[0] + '/benchmark_config.yaml'
        data = load_yaml(exp_yaml)
        print 'Packet Size = ' + str(data['cluster']['op_size']) + '\nMode of Operation = ' + data['cluster']['mode'] + '\n'
        json_files = glob.glob(x[0] + '/json_output*')
        if (len(json_files) != (my_dict['volumes_per_client'] * len(my_dict['clients']))):
            print 'Expected number of json files = ' + str(my_dict['volumes_per_client'] * len(my_dict['clients']))
            print 'Number of files in folder ' + x[0] + ' = ' + str(len(json_files))
        for file in json_files:
            try:
                with open(file) as f:
                    data = json.load(f)
            
                for job in data["jobs"]:
                    if print_all_entries == True:
                        print file + ' Write IOPS = ' + str(job["write"]["iops_mean"])
                        print file + ' Read IOPS = ' + str(job["read"]["iops_mean"])
                        print file + ' Write Bandwidth = ' + str(job["write"]["bw_mean"])
                        print file + ' Read Bandwidth = ' + str(job["read"]["bw_mean"])
                        print file + ' Write Latency = ' + str(job["write"]["lat_ns"]["mean"])
                        print file + ' Read Latency = ' + str(job["read"]["lat_ns"]["mean"])
                    write_iops += job["write"]["iops_mean"]
                    read_iops += job["read"]["iops_mean"]
                    write_bw += job["write"]["bw_mean"]
                    read_bw += job["read"]["bw_mean"]
                    write_lat = (((write_lat * (n-1)) + job["write"]["lat_ns"]["mean"]) / n)
                    read_lat = (((read_lat * (n-1)) + job["read"]["lat_ns"]["mean"]) / n)
            except:
                print 'Missed File ' + file
                missed += 1
        print '\tWrite-IOPS = ' + str('%.0f'%(write_iops)) + '\t\t\t\tRead-IOPS = ' + str('%.0f'%(read_iops))
        print '\tWrite-Bandwidth = ' + str('%.1f'%(write_bw/1024)) + 'MB/s\t\tRead-Bandwidth = ' + str('%.1f'%(read_bw/1024)) + 'MB/s'
        print '\tWrite-Latency = ' + str('%.1f'%(write_lat/1000000)) + 'ms\t\t\tRead-Latency = ' + str('%.1f'%(read_lat/1000000)) + 'ms'
        print '------------------------------------------------------------------------'
        print 'Total missed files = ' + str(missed)
        print '\n'
