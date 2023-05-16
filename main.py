from AT import AT
import argparse
from datetime import datetime
from multiprocessing import Queue, Process

def main() -> None:
    # set end device key values
    DevAddr = "260C5A81"
    DevEUI = "AC1F09FFFE083205"
    AppEUI = "1000000000000420"
    AppKey = "5506761A0149521DCE38CA01A3C1C8A7"
    AppSKey = "CE976B25295D3FF42A80A6305447E942"
    NwkSKey = "FB08E423BDA002A60776631DA16DF2DE"

    # instantiate AT class for end device
    at = AT('/dev/ttyUSB0', 
            DevAddr,
            DevEUI,
            AppEUI,
            AppKey,
            AppSKey,
            NwkSKey,
            115200, 
            False
        )

    queue = Queue()
    join_process = Process(target=at.joinNetwork, args=(queue,))
    join_process.start()

    listener_process = Process(target=at.serialPortListen, args=(queue,))
    listener_process.start()

    join_fail = False
    monitor_join_process = Process(target=at.monitorJoin, args=(queue, join_fail))
    monitor_join_process.start()

    monitor_join_process.join()
    listener_process.join()
    join_process.join()
    
    if join_fail:
        return None

    # Network Join Success! Now wait for requests
    at.monitorRecv()

    return None
         

if __name__ == '__main__':
    main()