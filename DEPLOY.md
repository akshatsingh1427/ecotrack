# Run locally
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py runserver

# Deploy on Render (easiest)
1. Push this folder to a GitHub repo.
2. On render.com: New > Blueprint > pick the repo. render.yaml sets up the web service and the Postgres database.
3. Wait for the build, then open the URL Render gives you.

# Deploy on PythonAnywhere
1. Upload the zip, unzip in a Bash console, then: mkvirtualenv ecoenv --python=python3.10 ; pip install django pillow whitenoise
2. python manage.py migrate
3. Web tab > Manual configuration. Source: /home/USER/ecotrack, Virtualenv: /home/USER/.virtualenvs/ecoenv
4. In the WSGI file use: sys.path.insert(0,'/home/USER/ecotrack'); os.environ['DJANGO_SETTINGS_MODULE']='ecotrack.settings'; from ecotrack.wsgi import application
5. Web tab > Environment variables: DEBUG=0, SECRET_KEY=<long random text>, ALLOWED_HOSTS=USER.pythonanywhere.com, CSRF_TRUSTED_ORIGINS=https://USER.pythonanywhere.com
6. Reload.
Optional photo OCR: pip install rapidocr-onnxruntime (too large for PythonAnywhere free tier).
