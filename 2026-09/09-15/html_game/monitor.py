import csv
import os
import time
from datetime import datetime

import psutil


log_file = "resource_log.csv"
headers = [
    "datetime",
    "cpu_percent",
    "memory_percent",
    "memory_used_mb",
    "bytes_sent_total",
    "bytes_recv_total",
    "bytes_sent_1sec",
    "bytes_recv_1sec",
]

previous_network = psutil.net_io_counters()
psutil.cpu_percent()

try:
    with open(log_file, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not os.path.exists(log_file) or os.path.getsize(log_file) == 0:
            writer.writerow(headers)
            file.flush()

        while True:
            time.sleep(1)

            now = datetime.now()
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            network = psutil.net_io_counters()
            bytes_sent_1sec = network.bytes_sent - previous_network.bytes_sent
            bytes_recv_1sec = network.bytes_recv - previous_network.bytes_recv
            previous_network = network

            writer.writerow([
                now.strftime("%Y-%m-%d %H:%M:%S"),
                cpu_percent,
                memory.percent,
                round(memory.used / 1024 / 1024, 2),
                network.bytes_sent,
                network.bytes_recv,
                bytes_sent_1sec,
                bytes_recv_1sec,
            ])
            file.flush()

            print(
                f"{now:%H:%M:%S} | CPU {cpu_percent:.1f}% | "
                f"RAM {memory.percent:.1f}% | SEND {bytes_sent_1sec} B/s | "
                f"RECV {bytes_recv_1sec} B/s",
                flush=True,
            )
except KeyboardInterrupt:
    pass
