#!/usr/bin/env python3

from get_hr import get_hr_rr, set_max_act_plan, connect, reconnect
import rclpy
import rclpy.logging
from rclpy.node import Node
#from ros_healthcare_msg.msg import HR, HRHeader
#from std_msgs.msg import Header
from std_msgs.msg import Int32

class CorsanoWrapper(Node):

    def __init__(self):

        super().__init__('corsano_wrapper')


        self.device_exists = None


        self.declare_parameter('mac_add', "D9:D9:DF:CB:74:79") #C4:8D:E7:96:BD:AD") #F1:3B:40:28:CB:EC 
        self.declare_parameter('adapter_mac_add', "00:1A:7D:DA:71:12")  #E4:5F:01:B1:87:D6 , 00:1A:7D:DA:71:11


        self.address = self.get_parameter('mac_add').get_parameter_value().string_value
        self.adapter_address = self.get_parameter('adapter_mac_add').get_parameter_value().string_value
        # self.driver = CorsanoDriver(self.address)

    
        self.cors, is_connected = connect(self.address, self.adapter_address) #mac_add)
        if is_connected == False:
            self.get_logger().info("Connection failed. Please try again")
        else:
            type_to_command = {type(v).__name__:v for v in self.cors.commands.values()}
           
            self.cmd_get_file_size = type_to_command["CMD_GET_FILE_SIZE"]
            self.cmd_stream_file_with_size = type_to_command["CMD_START_STREAMING_FILE_WITH_SIZE"]
            self.cmd_stream_file_with_size_offset = type_to_command["CMD_START_STREAMING_FILE_WITH_SIZE_OFFSET"] 
            cmd_set_plan = type_to_command["APP_CMD_SET_PLAN"] 

            # self.cmd_get_file_size = cmd_get_file_size
            # self.cmd_stream_file_with_size =  cmd_stream_file_with_size 
            # self.cmd_stream_file_with_size_offset = cmd_stream_file_with_size_offset 

            res = set_max_act_plan(self.cors,cmd_set_plan)
            self.get_logger().info(f'Plan set to:{res}')

            # while True:
            # hr, hr_quality = get_hr(cors,cmd_get_file_size,cmd_stream_file_with_size, cmd_stream_file_with_size_offset)
            # self.get_logger().info(f'Heart Rate: {hr}, Quality: {hr_quality}')

            self.publisher_ = self.create_publisher(Int32, 'hr', 10)
            self.rr_publisher_ = self.create_publisher(Int32, 'rr', 10)

            self.logger_ = self.get_logger()
            

            timer_period = 0.1 # 1 - Frequency of the sampling
            self.timer = self.create_timer(timer_period, self.timer_callback)

    def reconnect(self):
        self.cors, is_connected  = reconnect(self.cors) 
        if not is_connected:
            self.get_logger().info("Failed to reconnect, will reattempt...")

    def timer_callback(self):

        msg = Int32()
        msg_rr = Int32()

        #msg = HR()
        #msg.header = HRHeader()
        #msg.header.header= Header()
        #msg.header.device_serial_number = self.address
        try:

            #data = self.driver.get_data()  
            #msg.header.header.stamp = self.get_clock().now().to_msg()

            hr, hr_quality, rr, rr_quality, batt = get_hr_rr(
                self.cors, 
                self.cmd_get_file_size,
                self.cmd_stream_file_with_size, 
                self.cmd_stream_file_with_size_offset
            )
            msg.data = hr
            msg_rr.data = int(rr)
            self.get_logger().info(f'Heart Rate: {hr}, Quality: {hr_quality}')
            if rr != 0:
                self.get_logger().info(f'Respiratory Rate: {rr}, Quality: {rr_quality}')
                self.rr_publisher_.publish(msg_rr)

            self.publisher_.publish(msg) # publish the message




        except Exception as e:

            self.logger_.info('Failed to read data from peripheral: %s' % self.address)
            self.logger_.info('Error: %s' % str(e))
            self.reconnect()





def main(args = None):

    try:

        rclpy.init(args=args)  

        corsano_wrapper = CorsanoWrapper()




        # if corsano_wrapper.device_exists is not None:

        rclpy.spin(corsano_wrapper)




        corsano_wrapper.destroy_node()

        rclpy.shutdown()

    except Exception as e:

        print("An error occurred:", str(e))




if __name__ == "__main__":

    main()
