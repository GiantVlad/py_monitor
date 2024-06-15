### Python Monitor
CPU, MEM, Disk usage monitoring with email notifications

```
pip install virtualenv
cd this_project
virtualenv custom_env
source custom_env/bin/activate
pip install -r requirements.txt
cp .env.example .env 
touch monitoring.log 
```

Add this line to the cron to run script every 15 minutes
```
sudo crontab -e
``` 
5-59/15 * * * * python3 /var/app/py_monitor.py >> /var/log/cron.log 2>&1
