# steps to run the code
```
git clone 
```
```
cd ecomm_project
```
* create virtualenv
```
virtualenv venv
```
* setup virtualenv
```
source venv/bin/activate
```
* install requirements
```
pip install -r requirements.txt
```
* make migrations
```
python manage.py makemigrations
```
* migrate the database
```
python manage.py migrate
```
* create superuser
```
python manage.py createsuperuser
```
* to run the code
```
python manage.py runserver
```