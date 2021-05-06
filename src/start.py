import os
import signal
import subprocess
import platform
import re

# Making sure to use virtual environment libraries

# Change directory to where your Flask's app.py is present
#os.chdir("/home/ubuntu/Desktop/Medium/keras-and-tensorflow-serving/flask_server")
tf_ic_server = ''
flask_server = ''

env_command = 'set' if platform.system() == 'Windows' else 'export'
end_line = '&&' if platform.system() == 'Windows' else ' '

# Environment variables
FLASK_APP = f'{env_command} FLASK_APP={os.environ.get("FLASK_APP")}{end_line}'
FLASK_ENV = f'{env_command} FLASK_ENV={os.environ.get("FLASK_ENV")}{end_line}'
FLASK_DEBUG = f'{env_command} FLASK_DEBUG="{os.environ.get("FLASK_DEBUG")}"{end_line}'
REQUESTS_CA_BUNDLE = f'{env_command} REQUESTS_CA_BUNDLE=secrets/cert.pem{end_line}'
ADDITIONAL_ENV = f'env CUDA_VISIBLE_DEVICES="-1"&&env TF_CPP_MIN_LOG_LEVEL="3"{end_line}'
LOG_FILTER = f' | grep -v "I tensorflow/"'

# Main Command
PROCESS_COMMAND = 'python ./src/app.py ' if os.environ.get("FLASK_ENV") == 'development' else 'gunicorn '

# Parameters
PARAMS = '--cert=secrets/cert.pem --key=secrets/key.pem' if os.environ.get("FLASK_ENV") == 'development' else '--certfile ../secrets/cert.pem --keyfile ../secrets/key.pem --chdir ./src --bind 0.0.0.0:5000 -w 8 src.wsgi:app --timeout 10000'
PARAMS = PARAMS if re.match(r'^python', PROCESS_COMMAND) is not None else ''

# Execute Command
FLASK_COMMAND = f'{PROCESS_COMMAND}{PARAMS}'
TENSORFLOW_SERVER_COMMAND = 'tensorflow_model_server --model_base_path=/home/finaljtth/project/zenswebdev-service-flask/src/ml/model/my_image_classifier --rest_api_port=10000 --model_name=ImageClassifier'

env = os.environ.copy()

try:
  print(f'Subprocess : {TENSORFLOW_SERVER_COMMAND}')
  tf_ic_server = subprocess.Popen([TENSORFLOW_SERVER_COMMAND], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True, preexec_fn=os.setsid)
  print("Started TensorFlow Serving ImageClassifier server!")
  
  print(f'Subprocess : {FLASK_COMMAND}')
  flask_server = subprocess.Popen([FLASK_COMMAND], env=env, stdout=subprocess.PIPE, shell=True ,preexec_fn=os.setsid)
  print("Started Flask server!")

  while True:
    print("Type 'exit' and press 'enter' OR press CTRL+C to quit: ")
    in_str = input().strip().lower()
    if in_str == 'q' or in_str == 'exit':
      print('Shutting down all servers...')
      os.killpg(os.getpgid(tf_ic_server.pid), signal.SIGTERM)
      os.killpg(os.getpgid(flask_server.pid), signal.SIGTERM)
      print('Servers successfully shutdown!')
      break
    else:
      continue
except KeyboardInterrupt:
  print('Shutting down all servers...')
  os.killpg(os.getpgid(tf_ic_server.pid), signal.SIGTERM)
  os.killpg(os.getpgid(flask_server.pid), signal.SIGTERM)
  print('Servers successfully shutdown!')