from multiprocessing import Queue
from datetime import datetime
import serial
import time

class AT:
    def __init__ (self, 
                serial_port: str, 
                DevAddr: str, 
                DevEUI: str, 
                AppEUI: str, 
                AppKey: str, 
                AppSKey: str, 
                NwkSKey: str,
                baud_rate: int = 115200, 
                verbose: str = False
                ) -> None:

        self.serial_port = serial_port
        self.baud_rate = baud_rate

        self.devaddr = DevAddr
        self.deveui = DevEUI
        self.appeui = AppEUI
        self.appkey = AppKey
        self.appskey = AppSKey
        self.nwkskey = NwkSKey

        self.verbose = verbose
        
        if self.verbose:
            print(f"Attempting to Open Serial Port {serial_port}")

        self.openSerialPort()
        return None
    
    def openSerialPort (self) -> None:
        try:
            self.s = serial.Serial(self.serial_port, self.baud_rate, bytesize=8, parity='N', stopbits=1, timeout=1)
            print(f"Success Opening Serial Port {self.serial_port}")

        except serial.serialutil.SerialException:
            print(f"Failure Opening Serial Port {self.serial_port}")
        
        return None

    def serialPortListen(self, q: Queue) -> None:
        while True: 
            r = self.s.readline()
            if r != b'':
                r = r.replace(b'\n',b'')
            
                # parse for network join
                if r.decode() == '+EVT:JOIN_FAILED_RX_TIMEOUT':
                    attempts += 1
                    if attempts == join_attempts:
                        q.put('JOIN FAIL')
                        return None

                elif 'JOINED' in r.decode():
                    q.put('JOIN SUCCESS')
                    return None

                else:
                    q.put(f'{r.decode()}')

    def sendATCommand(self, explanation: str, cmd: str, q: Queue) -> None:
        # ensure case, encode and append necessary EOI data
        cmd = cmd.upper()
        q.put(cmd)
        self.s.write(cmd.encode() + b'\r\n')
        self.s.flush()
        return None

    def setNetworkValues (self, q: Queue) -> None:
        commands = [('Attempting to Connect to RAK3172', 'AT'),
                    ('Set AT Command Mode', 'AT+ATM'),
                    ('Set LoRaWAN® Mode', 'AT+NWM=1'),
                    ('Set OTAA Join Mode', 'AT+NJM=1'),
                    ('Set Device Class', 'AT+CLASS=A'),
                    ('Set Device Band to US', 'AT+BAND=5'),
                    ('Set DevEUI (JoinEUI)', f'AT+DEVEUI={self.deveui}'),
                    ('Set AppEUI', f'AT+APPEUI={self.appeui}'),
                    ('Set AppKey', f'AT+APPKEY={self.appkey}')
                ]

        for cmd in commands:
            self.sendATCommand(cmd[0], cmd[1], q)
        return None

    def joinNetwork (self, q: Queue) -> None:
        # connects a device to the LoRaWAN Network

        self.setNetworkValues(q)

        join_interval = 10
        join_attempts = 8

        # send join request
        self.sendATCommand('Joining LoRaWAN® Network', f'AT+JOIN=1:0:{join_interval}:{join_attempts}',q)
        return None

    def monitorJoin(self, q: Queue, join_fail: bool) -> int:
        msg = ''
        while msg != 'JOIN SUCCESS':
            if msg == 'JOIN FAIL':
                print('LoRaWAN® Network Join Failure')
                join_fail = True
                return None
        
            msg = q.get()
            if self.verbose:
                print(msg)

        print('LoRaWAN® Network Join Success!')
        print('Now Listening for Messages...')
        join_fail = False
        return None


    def sendMessage (self, msg) -> None:
        print('=============================================')
        try:
            command, datatype, filename = msg.split(':')
        except ValueError:
            print('ValueError, Message not expected request format')
            garb, data = msg.split(':')
            print(f'MESSAGE RECEIVED : {data}')
            return None

        print(f'Request for {filename} received')
        f = open('./DER_files/'+filename+'.xml', 'r')
        data = f.read()
        f.close()
        chunks = []
        encoded_data = data.encode('utf-8').hex()
        for i in range(0, len(encoded_data), 256):
            chunks.append( encoded_data[i:i+256] )

        for i, chunk in enumerate(chunks):
            print(f'Sending chunk {i+1} of {len(chunks)}')
            print(f'Chunk {i+1} :: {chunk}')
            self.s.write(f'AT+SEND=2:{chunk}\r\n'.encode())
            self.s.flush()
            time.sleep(7)
        
        print(f'Succesfully fulfilled request for {filename}')

    def monitorRecv (self) -> str:
        while True:
            # send 'QUERY' in hex to monitor for input
            self.s.write(b'AT+SEND=2:5155455259\r\n')
            self.s.flush()
            r = self.s.readline()
            while r != b'':
                r = r.replace(b'\n',b'')
                if (r.decode())[:7] == '+EVT:RX':
                    now=datetime.now()
                    millisecond=('%02d:%02d.%d'%(now.minute,now.second,now.microsecond))[:-4]
                    print(f'Message received at minute:second:millisecond : {millisecond}')
                    # specifically hunts for "REQUEST:PAYLOAD:FILENAME" (must be xml)
                    garbage, request = (r.decode()).split(':3:5245')
                    decoded_request =  bytes.fromhex(request).decode("utf-8")
                    self.sendMessage(decoded_request)
                r = self.s.readline()
            time.sleep(7)
                
