This an example Python/Django web site for management of projects/accounts on a cluster.

It is very simple, but it has been very useful for me.

## Installation and running

It can be run by:

```bash
$ git clone https://github.com/isilanes/django-projects
$ cd django-projects/
$ git checkout -b v0.2
$ python -m manage runserver localhost:8081
```

The required python modules can be installed by:

```bash
$ pip install -r conf/requirements.txt
```

The server can be run with Gunicorn:

```bash
$ bash gunicorn.sh
```

or even in Docker:

```bash
$ bash docker/build
$ bash docker/run $PWD/WebProjects.db
```

## Example functionality

List and detail views of projects and IPs (main researchers), such as:

```
http://localhost:8081/
http://localhost:8081/projects/
http://localhost:8081/ip/1/
http://localhost:8081/project/1/
```

List and visual representation of active node reservations:

```bash
http://localhost:8081/reservations
```

Bulk information retrieval via GET. For accounting purposes:

```
http://localhost:8081/disk_accounting/<year>/<month>/
```

for example:

```
http://localhost:8081/disk_accounting/2017/12/
```

Also to check whether an account or an IP exists with a given name:

```
http://localhost:8081/account_exists/<name>/
http://localhost:8081/ip_exists/<name>/
```

Account names are checked for a perfect match, whereas IP names are checked for substring matching. For example:

```
http://localhost:8081/account_exists/pep/
http://localhost:8081/ip_exists/Rossum/
```

Manipulating the database via GET, for example to create an account:

```
http://localhost:8081/create_account/<token>/<end>/<projname>/<accname>/<projid>/<diskquota>/
```

## Administrative view

The administrative view can be accessed at:

```
http://localhost:8081/admin
```

The dummy database provided with this repository can be manipulated there, the user/password being admin/admin.

