based on https://github.com/MaxHalford/flask-boilerplate

## Setup
- Install conda for package management and virtual environment

- Install ffmpeg

	`conda install -c conda-forge ffmpeg`

- Install OpenCV

	`conda install -c conda-forge opencv`

- Install Flask

	`conda install -c anaconda flask`

- Install the requirements and setup the development environment.

	`make install && make dev`

- Create the database.

	`python manage.py initdb`

- Run the application.

	`python manage.py runserver`

- Navigate to `localhost:5000`.
