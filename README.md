# IP Info 
collect data for public IPS and get all possible data from `ipinfo.io`
## How it works
based on web sockets to achieve real time data , list of ips send to server  after validation against json schema and list include valid ips and all ips are public them create a background task to get ip info , if task fails for any reason their is max tries up to 3 tries which mean automatically task will try to run again up to 3 tries,  after each task finish task itself sends data to client in json format , data being collected from `ipinfo.io`

### Validation 
   - support both types `IPv4` and `IPv6`
   - parsed text data must be in form of 
   ```json 
   {
   "ips":[{LIST_OF_PUBLIC_IPS}]
   }
   ```
   - the list of ip must include at least one valid ip 
   - reserved, private or loopback ips not allowed as these ips don't have public info 
   - the allowed is public ips which can be route over internet 
 ### Usage Example 
 - screen recorder for application usage 
 - URL 
### Application Logging

   - logging are allowed to application logging messages via stream handler 
   - default logging level is `DEBUG` 
   - custom logger used for all application parts 

### Libraries and packages 
| Package  | Usage  |
|--|--|
| `poetry` | python package for project management dependencies |
| `Django` | python framework for backend |
| `Channels` | websockets allow web sockets communication|
| `redis` | python library for redis db communication  |
| `celery` | create and fire background tasks in separate process |
| `jsonschema` | used as validation layer against schema|
| `daphne`| for running server to support websockets|
| `python-dotenv` | used to manage secrets with python project|
| `httpx`| python library support sync and async requests|


### operate the project 
- install Redis as it's used for channel layer and message broker 
  - `sudo apt install redis-server -y`
- install git version control 
  - `sudo apt install git -y`
- python run time environment and pip `python package index` 
	 -  for this project `python >= 3.10`
	 - `sudo apt install python3 python3-pip`
- install poetry for project management
	- `pip3 install poetry` 
- clone the project 
	- `git clone {project_url}`   
- move to project director 
	- cd `IP-Info`
- create `.env` file and set the blow secret keys on it 

| ENV Variable | Description  |
|--|--|
| `REDIS_HOST` |  redis hot ip |
| `REDIS_PASSWORD` | redis password |
| `REDIS_PORT` | running port services for redis|
| `REDIS_DB_INDEX` | redis db index|
|  `SECRET` | represents `django secret key` you can use [djsecret](https://djecrety.ir/) to get secret key for django |

- activate python shell 
    - `poetry shell`
 - install dependencies in `pyproject.toml` 
		  -  `poetry install`
- now project are ready to operate and access via local 
  - move to django project `cd ip_info`
  - open 3 terminal 
  - one to run websockets on your local `daphne -b 127.0.0.1 -p 8000 ip_info.asgi:application` this will up project in your local and you can stream logging into terminal 
  - one to run celery worker and listen to message tasks on queue `celery -A ip_info worker --loglevel=debug
`
  - Optional to run flower `python library allow monitor and visual background tasks on web browser` `celery -A ip_info flower --port=3000
`
- now project are running and up over url `ws://127.0.0.1:8000/ws/ip/`

### How to test 
there is some tools and some of them are online hosted can be used via web browser 
- [WebSocketing](https://websocketking.com/) used online and do a great job i used it to test this project, allow access to localhost  
- [hoppscotch](https://hoppscotch.io/) supports also real time like SSE and web sockets , not allow  locahhost connection , you can expose local using services like ngrok 
- tools like postman now allow test web sockets 