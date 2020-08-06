# essnapshot

## current state

Alpha.

The goal is to deliver a snapshot rotation tool for elasticsearch snapshots. 
The functionality should be rather simple as most of it is already implemented in ES.

So I just stick to creating a repository, create snapshots within it and delete old ones.
I assume that most people will use `cron` to call this script, so no daemon functionality 
or similar will be implemented. 

## usage configuration

At the moment the tool supports only one parameter (excecpt for help):

````
Usage: essnapshot [options]

Options:
  -h, --help            show this help message and exit
  -c FILE, --config=FILE
                        Path to configuration file
````

You must provide a `yaml`configuration file like this:

```
---
es_connections:
  - host: 'localhost'
    port: 9200
repository_name: 'essnapshot'
repository:
  type: 'fs'
  settings:
    location: '/mnt/snapshot'
    compress: 'true'
retention_time: '7d'
```

The parameters should be self explanatory (if you're familiar with ES).

A short help to get you started with the main parameters:

### es_connections

A list(array) of hashes(dictionaries) to which ES can connect to.
To understand how this works see the [Elasticsearch API documentation](https://elasticsearch-py.readthedocs.io/en/master/api.html#elasticsearch).
Each Host is a `Dictionary` in the `List`.
The Options per Host are the ones for `Urllib3HttpConnection`s.
See [Connection](https://elasticsearch-py.readthedocs.io/en/master/connection.html#elasticsearch.Urllib3HttpConnection) in the API documentation.
Here you can configre authentication too.

Please ensure that this configuration file can only be read by the user/container
designated for the backup if you put any credentials in this configuration file
(and please don't put it into a public git repository).

### repository_name

This is the name of the repository which will be created and the snapshots created in.

### repository

This represents the configuration of the ES repository. It's a representation of the JSON sent to ES
and is described in the ES documentation in [Register a snapshot repository](https://www.elastic.co/guide/en/elasticsearch/reference/current/snapshots-register-repository.html).

### retention_time

The maximum backup age before snapshots will be deleted.

## development

- the feature set should be kept small
- the project should have a high test coverage (there is still room to improve it!)
- tests hould be executed automatically
- try to hold on to styleguides and improve code quality

You need [poetry](https://python-poetry.org) and [docker](https://www.docker.com) (for tests) installed. 

Necessary improvements and development steps will be documentated as github issues.
