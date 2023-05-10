# Wiki-Search

To run this program, you need to have virtual machine containing the wiki.py file.
To access this file the machine must allow SSH connections on port 2233.

You must then have a second VM with Docker installed, which can be done using the following terminal commands:
    - sudo apt install apt-transport-https curl gnupg-agent ca-certificates software-properties-common –y
    - curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    - sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    - sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

With Docker installed you must create a container for MySQL which can be done with the following command:
    - sudo docker run --name "mysqlcontainer1" -e
      MYSQL_ROOT_HOST=% -e MYSQL_ROOT_PASSWORD=mypassword -d -p
      6603:3306 mysql/mysql-server:latest

Then connect to the container:
    - sudo docker exec -it mysqlcontainer1 /bin/sh
    - mysql -u root -p (the password will be mypassword)


Once in the MySQL client, you must create the database we'll be using for the application, which is called 'wikipedia'.
    - CREATE DATABASE wikipedia;
    - USE wikipedia;

With the database created the application will need a table to hold the cached data, which is called 'wikis'.
    - CREATE TABLE wikis (
            title VARCHAR(255),
            article MEDIUMTEXT,
      );

To connect to the database, the machine must allow MySQL connections on port 7888
The application can then be started by running main.py and connecting to http://127.0.0.1:5000/ in the browser where
the searches can then be made
