# RS2 Note App API

A small API that serves as the back-end service for RS2 Notes web application. To see more details regarding RS2 Notes web application, you may refer to its repository.
https://github.com/jd-camontoy/rs2-notes-app

Created using Python with Flask RESTful, MongoDB as the storage, and Docker as the environment provider and container


## Get Started

Please ensure that the local machine as Docker installed, and is connected to the internet.

To start, ensure that you are on the project's directory.
```
cd rs2-notes-api
```

Then run the following Docker command to install build the containers
```
docker-compose build
```

After successfully building the containers, you may start running the services
```
docker-compose up
```

If you wish to stop the services, you may opt to down the Docker containers
```
docker-compose down
```