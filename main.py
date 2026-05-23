import rclpy
import socket
from rclpy.node import Node
from sensor_msgs.msg import Joy

class JoySubscriber(Node):
    def __init__(self):
        super().__init__('joy2_subscriber')
        self.subscription = self.create_subscription(
            Joy,
            '/joy2',
            self.listener_callback,
            10
        )
        self.angles = [0.0] * 6
        self.offsets = [0.0] * 6  # Change these values to add offsets to each point
        self.offsets[2] = -60;
        # UDP settings
        self.udp_ip = "192.168.2.155"
        self.udp_port = 5010
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def map_axis(self, val):
        # Maps a value from [-1, 1] to [1000, 2000]
        return int((val + 1.0) * 500.0 + 1000.0)

    def listener_callback(self, msg):
        if len(msg.axes) > 6 and len(msg.buttons) > 4:
            # Map specific axes (4, 3, 2, 5, 6) directly to 1000-2000
            mapped_axes = [
                self.map_axis(msg.axes[4]),
                self.map_axis(msg.axes[3]),
                self.map_axis(msg.axes[2]),
                self.map_axis(msg.axes[5]),
                self.map_axis(msg.axes[6])
            ]
            
            # Determine 6th value from buttons 2 and 4
            b2 = msg.buttons[2]
            b4 = msg.buttons[4]
            b3 = msg.buttons[3]
            
            if b2 == 0 and b4 == 0:
                btn_val = 1500
            elif b2 == 1 and b4 == 0:
                btn_val = 1500
            elif b2 == 0 and b4 == 1:
                btn_val = 2000
            elif b2 == 1 and b4 == 1:
                btn_val = 1000
            else:
                btn_val = 1500

            btn_val1 = 1500
            if(btn_val1==1):
                btn_val1 = 2000;
                
            mapped_axes.append(btn_val)
            mapped_axes.append(btn_val1)
            
            if msg.buttons[0] == 1:
                # Create UDP message and send
                udp_msg = f"A:{mapped_axes}"
                self.sock.sendto(udp_msg.encode('utf-8'), (self.udp_ip, self.udp_port))
                
                self.get_logger().info(f"Sent via UDP: {udp_msg}")
            else:
                print("unarmed")

def main(args=None):
    rclpy.init(args=args)
    joy_subscriber = JoySubscriber()
    
    try:
        rclpy.spin(joy_subscriber)
    except KeyboardInterrupt:
        pass
    finally:
        joy_subscriber.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
