# Create virtual environment On macOS/Linux:
```
   python3 -m venv env
   source env/bin/activate
```
# Create virtual environment On Windows:
```
   python -m venv env
   env\Scripts\activate
```

docker:
```
 docker exec -it cron_Django python manage.py makemigrations
 docker exec -it cron_Django python manage.py migrate
```
create superuser
 
``` 
   docker exec -it cron_Django python manage.py createsuperuser
```

to run cron, go to manage.py directory then run these commans:
```
run pip install -r requirements.txt from root

python manage.py runcrons

python manage.py shell

from import_export.cron_jobs import FileProcessingCronJob

cron = FileProcessingCronJob()
cron.do()

exit()
```
