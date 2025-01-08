# Create virtual environment On macOS/Linux:
   python3 -m venv env
   source env/bin/activate

# Create virtual environment On Windows:
   python -m venv env
   env\Scripts\activate


docker:

 docker exec -it cron_Django python manage.py makemigrations
 docker exec -it cron_Django python manage.py migrate

create superuser
 
 docker exec -it cron_Django python manage.py createsuperuser
