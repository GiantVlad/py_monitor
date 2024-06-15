import logging
import psutil
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SERVER = os.getenv('SERVER_NAME')
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
RECEIVERS = os.getenv('RECEIVERS')
BASE_DIR = os.getenv('BASE_DIR', '.')
MAILGUN_SANDBOX = os.getenv('MAILGUN_SANDBOX')

log_path = os.path.join(BASE_DIR, 'py_monitoring', 'monitoring.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
if not os.access(os.path.dirname(log_path), os.W_OK):
    raise PermissionError(f"Log directory '{os.path.dirname(log_path)}' is not writable")

logging.basicConfig( #NOSONAR
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
    filename=log_path,
    filemode='a'
)

logger = logging.getLogger(__name__)

total = int()
used  = int()
free  = int()

def send_mailgun_email(message):
    return requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_SANDBOX}.mailgun.org/messages",
        auth=("api", MAILGUN_API_KEY),
        data={"from": "Admin: vlad.sadkou@dubz.com",
              "to": RECEIVERS.split(','),
              "subject": "TRS monitoring warning",
              "text": message},
        )

vMemUsed = psutil.virtual_memory().percent
cpuUsed = psutil.cpu_percent()

logger.info("Memory %s used.", vMemUsed)
logger.info("CPU %s used.", cpuUsed)

if vMemUsed > 80:
    r = send_mailgun_email("Server: %s, Memory %s used" % (SERVER, vMemUsed))

if cpuUsed > 85:
    r = send_mailgun_email("Server: %s, CPU %s used" % (SERVER, cpuUsed))

for disk in psutil.disk_partitions():
    if disk.fstype and ("loop" not in disk.device):
        total = int(psutil.disk_usage(disk.mountpoint).total)
        free  = int(psutil.disk_usage(disk.mountpoint).free)
        freePr = int((free / total) * 100)
        logger.info("Disk:%s Free:%.2f" % (disk.device, freePr))
        if freePr < 25:
            r = send_mailgun_email("Server: %s, Disk:%s, Free:%.2f" % (SERVER, disk.device, freePr))
