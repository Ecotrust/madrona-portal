# Deploying Services

## Celery

### Requirements
- Redis (or RabbitMQ, but these configurations assume Redis)
    - installed via apt
- Celery
    - installed via pip

### Configure SystemD Service
1. add a celery user
    ```
    sudo useradd celery -d /home/celery -b /bin/bash
    ```
1. add the service file
    ```
    sudo cp ./celery.service /etc/systemd/system/
    ```
    - You will likely need to edit the `WorkingDirectory` setting to get to the core app in ocean_portal
1. add the celery config file
    ```
    sudo cp ./celery.conf /etc/conf.d/celery
    ```
    - You may need to create the directory /etc/conf.d
    - You may need to edit several of these configurations, namely:
        - `CELERYD_NODES`: "w1" will get you one worker, "w1 w2 w3" will get you three
        - `CELERY_BIN`: the location of your celery binary
        - `CELERYD_PID_FILE`: you may need to create `/var/run/celery` or point this somewhere where the celery user can write
            ```
            sudo mkdir /var/run/celery
            sudo chown celery:celery /var/run/celery
            ```
        - `CELERYD_LOG_FILE': you may need to create `/var/log/celery` or point this somewhere where the celery user can write
            ```
            sudo mkdir /var/log/celery
            sudo chown celery:celery /var/log/celery
            ```
1. enable the celery service to start on boot
    ```
    sudo systemctl enable celery.service
    ```
1. start the service
    ```
    sudo service celery start
    ```
