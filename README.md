# essnapshot

## purpose

This is a project to get me started with Python skills. I don't like projects with no use
so I thought of a simple project to learn the coding basics of python. 

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
repository_name: 'essnapshot'
# the hash must represent the JSON body sent to ES
# see https://www.elastic.co/guide/en/elasticsearch/reference/current/snapshots-register-repository.html
repository:
  type: 'fs'
  settings:
    location: '/mnt/snapshot'
    compress: 'true'
# retention time of 7 days
retention_time: '7d'
```

The parameters should be self explanatory (if you're familiar with ES).
Options for the connection settings will be implemented soon.

## development

- the feature set should be kept small
- the project should have a high test coverage. 
- tests hould be executed automatically
- try to hold on to styleguides and improve code quality

You need [poetry](https://python-poetry.org) and [docker](https://www.docker.com) (for tests) installed. 

Necessary improvements and development steps will be documentated as github issues.