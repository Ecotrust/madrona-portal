# MARCO Portal Redesign

### This is the top level project for the Mid-Atlantic Ocean Data Portal

#### ~Development Installation

##### Initial Setup using Vagrant:
The following is the **_recommended_** folder structure for the **entire** MARCO project and the customized provisioning script is inherently dependent on it. Altering the folder and naming structure will require modifications to the provisioning script, so please be aware! The provisioning script is designed to be a **one-step** install after initial setup. 

```
  -- marco-portal2
    -- apps (all remaining repositories within MidAtlanticPortal) 
      -- mardona-analysistools
      -- madrona-features
      -- etc.
```


1.  Clone [marco-portal2](https://github.com/MidAtlanticPortal/marco-portal2.git) at the top level and the remaining repositories within a subfolder named `apps`
    * To quickly clone all the repositiories from [MidAtlanticPortal](https://github.com/MidAtlanticPortal), run one of the following curl commands with Ruby/Perl. In doing so, this will clone all of the respositories at the same level and will require you to move all the non `marco-portal2` repositories to a subfolder - called `apps`
      * RUBY:
      ```
      curl -s https://api.github.com/orgs/MidAtlanticPortal/repos?per_page=200 | ruby -rubygems -e 'require "json"; JSON.load(STDIN.read).each { |repo| %x[git clone #{repo["ssh_url"]} ]}'
      ```
      * PERL:
      ```
      curl -s https://api.github.com/orgs/MidAtlanticPortal/repos\?per_page\=200 | perl -ne 'print "$1\n" if (/"ssh_url": "([^"]+)/)' | xargs -n 1 git clone
      ```

2.  Once your folder structure is setup, create a *config.ini* file by following the general outline in `config.ini.template` and modify the following for use with vagrant
      * **MEDIA_URL:** /home/vagrant/marco_portal2/media
      * **STATIC_URL:** /home/vagrant/marco_porta2/static
      * **[DATABASE] USER:** vagrant
      * **[DATABASE] PASSWORD:** [remove entirely]

3. Download and install the neccessary [bower_components](http://portal.midatlanticocean.org/static/bower_components.tar.gz) within your `/static/` directory

4. Retrieve the media folder via ssh at `/webapps/marco_portal_media/` and add it to your `/media/` path defined in `config.ini` 
    * Of note - you may want to exclude the data_manager folder unless you're interested in several GBs of utfgrid layers. 

5. Retrieve the data & content fixture from `/fixture/dev_fixture.json` via ssh and place it at the root level of `marco-portal2`

6. Download and install [vagrant](https://www.vagrantup.com/downloads.html) and [virtual box](https://www.virtualbox.org/wiki/Downloads) (if you haven't already done so already)

7. Install the vagrant-faster plugin
   ```
   vagrant plugin install vagrant-faster
   ```

8. At the root of `marco-portal2`, run `vagrant up` and let it install ALL of dependencies MARCO relies upon

9. At this point, you should be completely setup!

##### Using Vagrant
* Access your VM by running `vagrant ssh`. This will automatically log you into your virtual machine with your virtual environment activated at the project root level.


* **Shortcuts**
  * To use `/manage.py` with normal django administrative tasks , use the keyword `dj` 

      ```
      dj makemigrations
      dj migrate
      dj dumpdata
      etc.
      ```
      
  * Typing `djrun` will run your dev server - remember to add your sample data first (see #5):
  

*  **NOTE:** The provisioning script is designed for a fresh install and will completely wipe the database and any associated content - IF you decide to shutdown/halt your VM! Anytime `vagrant up` or `vagrant provision` is run, the provisioning script will re-run. Adding the flag `--no-provision` to `vagrant up` will ignore the script.

##### OPTIONAL
If you decide to use pgAdmin3 for database management rather than using the command line, you'll need to allow/enable access to your virtual machine.
*  Enter into `postgres.conf` and change `listen_addresses`:
  ```
  sudo nano /etc/postgresql/9.3/main/postgresql.conf
  listen_addresses = '*'
  ```      

* Enter into `pg_hba.conf` and add the `host` line:
  ```
   sudo nano /etc/postgresql/9.3/main/pg_hba.conf 
   host    all    all    10.0.0.0/16     md5
  ```

* Restart postgresql
  ```
  sudo /etc/init.d/postgresql restart
  ```

* Within pgAdmin3, modify your settings:
     *  **Name:** marco_portal
     *  **Host:** localhost
     *  **Port:** 65432
     *  **Username:** vagrant


## Production Setup


### Putting site into maintenance mode

In the webfaction interface, remove the 'marco_portal2' app at `/` and replace 
with the maintenance page. Takes about 60 seconds to activate. Test out (http://midatlantic.point97.io)[http://midatlantic.point97.io]
to confirm. 

### Dependencies

 - Elasticsearch
 - Redis
 - Postgresql DB

### Configuration

 - Clone the repo
 - Copy `marco_config/settings/local.template.py` as `local.py` and customize.
 - `pip install --src ./deps -r requirements.txt`
 - createsuperuser
 - `DJANGO_SETTINGS_MODULE="marco_config.settings.production" ./manage.py migrate update_index createsuperuser`

#### Static assets

 - **for now**, rsync marco_site/static/ from your development instance (or run gulp from that dir on the server, if node is available)
 - Run `DJANGO_SETTINGS_MODULE="marco_config.settings.production" ./manage.py compress collectstatic`

## Getting production data

`pg_dump -U marco_portal marco_portal > dump.pg` (password from local.py)

`rsync -avz point97@midatlantic.point97.io:webapps/marco_portal2/site/dump.pg ./`

drop/create

`psql -U postgres marco_portal < dump.pg`

## Used technologies

  * [Openlayers 3](http://openlayers.org/)
  * [Bootstrap 3](http://getbootstrap.com/)
  * [Wagtail](http://wagtail.io/)
  * [Django 1.7](https://docs.djangoproject.com/en/1.7/)

## Candidate Technologies

#### Animation

 - http://greensock.com/tweenlite/

#### Icons

 - https://icomoon.io
 - https://www.npmjs.org/package/icomoon-build

