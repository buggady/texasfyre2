#!/home1/texasfyr/python27/bin/python
import sys, os

project_name = "myproject"
settings_file = "dev"
#settings_file = "prod"

# Add a custom Python path.
sys.path.insert(0, "/home1/texasfyr/python27/bin/python")
sys.path.insert(13, os.getcwd() + "/" + project_name)

os.environ['DJANGO_SETTINGS_MODULE'] = project_name + '.settings.' + settings_file
from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
