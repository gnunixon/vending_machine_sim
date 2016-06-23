# vending_machine_sim
Simulation of a simple vending machine. You can buy tea/coffee/juice, can change coins and try to frustrate the vending machine. 

VMS support multiple users and vending machines at the same time, and users from different computers and/or browsers can 

#Install
You need to get the code from repository on github:

  git clone https://github.com/gnunixon/vending_machine_sim.git vms

After that, install in the directory of project a new virtualenv:

  cd vms
  virtualenv venv
  . venv/bin/activate
  
Now you are in a new virtual environement, and you need to install all dependencies for the project:

  pip install -r requirements.txt
  
Create a new database for the project (we will use Postgresql, but, with small modifications, you can use any DB you want), and modify after that in models.py the

  app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/vms'

with your settings.

Now you are ready to start:

  python app.py
  
The project will be accessible on port 5000 (you can change this in app.py).

