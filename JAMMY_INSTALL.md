# Madrona Portal Development Installation on JAMMY VM

### Django web application and Wagtail CMS for the Madrona Data Portal.

## Local Vagrant Development Env
### ~Development Installation

requirements:
  - git
  - vagrant

1. Choose a working project directory that will be referred to from here has PROJDIR (i.e. /home/username/src/ ). It is best if it’s a directory you use to hold all of your dev projects.
  ```
  cd PROJDIR
  mkdir Madrona
  cd Madrona
  mkdir apps
  git clone https://github.com/Ecotrust/marco-portal2.git
  mv marco-portal2 madrona_portal
  cd apps
  ```
  if you are installing a version of the Mid-Atlantic Ocean Data Portal:
  ```
  git clone https://github.com/Ecotrust/mida-portal.git
  ```
  if you are installing a version of the West Coast Ocean Data Portal
  ```
  git clone https://github.com/Ecotrust/wcoa.git
  ```
  if you are installing a version of the Oregon Offshore Wind Energy Data Portal
  ```
  git clone https://github.com/Ecotrust/wc-offshore-portal.git
  ```
  Finally, for all installations:
  ```
  git clone https://github.com/Ecotrust/madrona-analysistools.git
  git clone https://github.com/Ecotrust/madrona-features.git
  git clone https://github.com/Ecotrust/madrona-manipulators.git
  git clone https://github.com/Ecotrust/madrona-scenarios.git
  git clone https://github.com/Ecotrust/marco-map_groups.git
  git clone https://github.com/Ecotrust/mp-accounts.git
  git clone https://github.com/Ecotrust/mp-data-manager.git
  git clone https://github.com/Ecotrust/mp-drawing.git
  git clone https://github.com/Ecotrust/mp-explore.git
  git clone https://github.com/Ecotrust/mp-proxy.git
  git clone https://github.com/Ecotrust/mp-visualize.git
  git clone https://github.com/Ecotrust/p97-nursery.git
  cd ../madrona_portal
  vagrant up
  vagrant ssh
  ```

2. Install dependencies
  ```
  sudo apt update
  sudo apt upgrade -y
  sudo apt install git python3 python3-dev python3-virtualenv python3-pip postgresql postgresql-contrib postgis postgresql-server-dev-14 libjpeg-dev gdal-bin python3-gdal libgdal-dev redis -y
  ```

3. Set up virtualenv
  ```
  python3 -m pip install --user virtualenv
  cd /usr/local/apps/
  sudo chown vagrant ./
  python3 -m virtualenv env
  source /usr/local/apps/env/bin/activate
  pip3 install -r /usr/local/apps/madrona_portal/requirements.txt
  pip uninstall numpy
  gdal-config --version
  pip3 install "pygdal<3.4.2"
  pip3 install -e /usr/local/apps/madrona_portal/apps/madrona-analysistools
  pip3 install -e /usr/local/apps/madrona_portal/apps/madrona-features
  pip3 install -e /usr/local/apps/madrona_portal/apps/madrona-manipulators
  pip3 install -e /usr/local/apps/madrona_portal/apps/madrona-scenarios
  pip3 install -e /usr/local/apps/madrona_portal/apps/marco-map_groups
  pip3 install -e /usr/local/apps/madrona_portal/apps/mp-accounts
  pip3 install -e /usr/local/apps/madrona_portal/apps/mp-data-manager
  pip3 install -e /usr/local/apps/madrona_portal/apps/mp-drawing
  pip3 install -e /usr/local/apps/madrona_portal/apps/mp-explore
  pip3 install -e /usr/local/apps/madrona_portal/apps/mp-proxy
  pip3 install -e /usr/local/apps/madrona_portal/apps/mp-visualize
  pip3 install -e /usr/local/apps/madrona_portal/apps/p97-nursery
  pip3 install -r /usr/local/apps/madrona_portal/apps/madrona-scenarios/requirements.txt
  pip3 install -r /usr/local/apps/madrona_portal/apps/marco-map_groups/requirements.txt
  pip3 install -r /usr/local/apps/madrona_portal/apps/mp-accounts/requirements.txt
  pip3 install -r /usr/local/apps/madrona_portal/apps/mp-data-manager/data_manager/requirements.txt
  pip3 install -r /usr/local/apps/madrona_portal/apps/mp-visualize/requirements.txt
  ```
  Also be sure to install the correct module for which tool you're building:
  * Mid-Atlantic:
  ```
  pip3 install -e /usr/local/apps/madrona_portal/apps/mida-portal
  ```
  * West Coast:
  ```
  pip3 install -e /usr/local/apps/madrona_portal/apps/wcoa
  pip3 install -r /usr/local/apps/madrona_portal/apps/wcoa/wcoa/requirements.txt
  ```
  * OROWindMap:
  ```
  pip3 install -e /usr/local/apps/madrona_portal/apps/wc-offshore-portal
  pip3 install -r /usr/local/apps/madrona_portal/apps/wc-offshore-portal/offshore/requirements.txt
  ```

4. Install database
  ```
  sudo -u postgres createdb -O postgres madrona_portal
  sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;" madrona_portal
  sudo vim /etc/postgresql/14/main/pg_hba.conf
  ```
   --------
  	<update line near bottom regarding ‘local   all   postgres’
  		Change ‘peer’ to ‘trust’ >
   ---------
  ```
  sudo service postgresql restart
  ```

5. Configure project
  ```
  cd /usr/local/apps/madrona_portal/marco
  mkdir media
  mkdir static
  cp config.ini.template config.ini
  vim config.ini
  ```

6. Edit config.ini
  - Use the appropriate `PROJECT_APP` value based on which project you are installing:
    * Mid-Atlantic: mida
    * West Coast: wcoa
    * OROWindMap: offshore
  - Add the following lines under `[App]`:
    ```
      PROJECT_APP = {{ YOUR PROJECT APP FROM ABOVE }}
      PROJECT_SETTINGS_FILE = True
      MEDIA_ROOT = /usr/local/apps/madrona_portal/marco/media
  	  STATIC_ROOT = /usr/local/apps/madrona_portal/marco/static
    ```
  - Add the following under [DATABASE]:
    ```
      USER = postgres
  	  NAME = madrona_portal
    ```

7. Add shortcuts
  ```
  vim ~/.bashrc
  #----------
  alias dj="/usr/local/apps/env/bin/python3 /usr/local/apps/madrona_portal/marco/manage.py"

  alias djrun="dj runserver 0:8000"
  #----------
  ```

8. Exit ssh session and re-ssh in
  ```
  crtl+d
  vagrant ssh
  ```

9. Set up Django
  ```
  dj migrate
  dj compress
  dj collectstatic
  dj loaddata /usr/local/apps/madrona_portal/marco/marco_site/fixtures/content.json
  djrun
  ```

10. Open http://localhost:8000 in your browser

11. Create super user
  ```
  dj createsuperuser
  ```

12. Open http://localhost:8000/django-admin and http://localhost:8000/admin in your browser to administer the site
