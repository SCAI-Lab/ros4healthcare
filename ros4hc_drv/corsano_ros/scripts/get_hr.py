from corsano import CorsanoInterface
from parsers import ActivityParser
from util import FileNames, PLAN_FREQUENCY, PLAN
import time


def connect(mac_add, adapter_add):
    cors = CorsanoInterface(mac_add, adapter_add)
    if cors.connect():
        return cors,True
    return None ,False

def reconnect(cors):
    is_connected  = cors.reconnect()
    return cors, is_connected
 

def get_hr_rr(cors, cmd_get_file_size, cmd_stream_file_with_size, cmd_stream_file_with_size_offset):

    debug = False

    size = cors.execute(cmd_get_file_size.cmd, file=FileNames["Activity_file"])["size"]
    offset = size - 38 
    if debug:
        print('offset: ', offset)
    #make sure offset is not negative 
    if offset < 0 :
        data = cors.execute(cmd_stream_file_with_size.cmd, file=FileNames["Activity_file"], size = 38)
        if debug:
            print('choice 1 offset')
    else: 
        data = cors.execute(cmd_stream_file_with_size_offset.cmd, file=FileNames["Activity_file"], size = 38, offset= offset)
        if debug:
            print('choice 2 offset')
        
    time.sleep(1)
    buffer_data = cors.get_buffer().read()
    data_dict = ActivityParser.parse(buffer_data)
    if debug:
        print(data_dict)
    # hr = data_dict['hr_raw']
    # hr_quality = data_dict['hr_raw_q']
    hr = data_dict['hr_filtered']
    hr_quality = data_dict['hr_filtered_q']
    rr = data_dict['rr_filtered']
    rr_quality = data_dict['rr_raw_q']
    batt = data_dict['battery']
    return hr, hr_quality, rr, rr_quality, batt


def set_max_act_plan(cors,cmd_set_plan):
    data = cors.execute(cmd_set_plan.cmd, plan= PLAN['HIGH_RESOLUTION'] ,  ppgfreq= PLAN_FREQUENCY['FREQ_512HZ'], actfreq= 1)
    return data['plan']


def main():
    mac_add = "C4:8D:E7:96:BD:AD" # Heba
   # mac_add = "d2:10:73:90:52:6c" # Ricardo
    
    cors,is_connected = connect(mac_add)
    if is_connected == False:
        print("Connection failed. Trying again")
    else:
        type_to_command = {type(v).__name__:v for v in cors.commands.values()}
        cmd_get_file_size = type_to_command["CMD_GET_FILE_SIZE"]
        cmd_stream_file_with_size = type_to_command["CMD_START_STREAMING_FILE_WITH_SIZE"]
        cmd_stream_file_with_size_offset = type_to_command["CMD_START_STREAMING_FILE_WITH_SIZE_OFFSET"] 
        cmd_set_plan = type_to_command["APP_CMD_SET_PLAN"] 

        res = set_max_act_plan(cors,cmd_set_plan)
        print('Plan set to :', res)

        while True:
           hr, hr_quality = get_hr(cors,cmd_get_file_size,cmd_stream_file_with_size, cmd_stream_file_with_size_offset)
           print(f'Heart Rate: {hr}, Quality: {hr_quality}')


   
        
        
#if __name__ == "__main__":
#    main()