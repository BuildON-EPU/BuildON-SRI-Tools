#echo "Sleep...(wait to be Postges UP)"
#sleep 30
echo "Do the migrations...."
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py makemigrations smurf_web_app
python3 manage.py migrate smurf_web_app
echo "Fill the models"
python3 ./manage.py shell < fill_models.py
python3 manage.py collectstatic --noinput
echo "Run Gunicorn"
gunicorn --workers=4 -t 30  --log-level INFO -b 0.0.0.0:8001 smurf_web.wsgi:application
