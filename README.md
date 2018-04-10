# Event Magic

Event magic is a simple scheduling / event management package aimed at services like AWS Lambda.
Typically, Event scheduling applications rely on you creating objects and then running those in a loop, so a long running process. The issue then appears with Lambda that you need to be idempotent so you need to reload the events and make sure they executed losing any data like number of executions.

To solve this, event magic can be run entirely in memory and has additional functionality to simply store and load the events from a mysql DB.

Additionally event magic allows you to specify a function to execute before the main event and provides a range of 'complete' criteria tests, such as:
* Until_success (Run for ever until it is successful),
* Until X count of successful executions
* Until a completed function returns True

Events can be broken down as follows:
Event - The thing you want to do
Schedule - When you want to do it.

The challenge is knowing when the event executed, Did it succeed or fail? Should the event repeat?
Should it repeat X times or forever? What If it needs to repeat forever but only until a certain state is reach?

This module was written specifically to work (agnostically) on a FaaS platform (AWS Lambda for example).

# Should I use Event Magic?

Yes, If you have Lambdas in AWS and you need scheduling but do not want to set up Redis or create more lambdas and you already have a mysql DB then this is good.

# Current State of Development

Currently in alpha as it does not have all of the features I originally intended and there's some areas that need a drastic rework, such as the database interactions. Once all of the features are in place and I have implemented it fully in a.n.other product it will move to Beta. Production will be decided on usage. i.e. I don't wont to say it's production ready until it stops having odd issues. So either a period of time or a number of implementations (Please let me know if you are using it / need help just raise a ticket)

# Setup

## DB

Not finished on this needs a total re-write but... pragmatism.

However for now, simply copy the [db_setup.sql](db_setup.sql) and run it against your DB.
To set your DB credentials do the following:

```python
import eventmagic

eventmagic.HOST = "localhost"
eventmagic.PORT = "3306"
eventmagic.USERNAME = "root"
eventmagic.PASSWORD = "thisisroot"
eventmagic.DATABASE = "eventmagic"
```



## Creating an event

```python
from eventmagic.schedule import Schedule
from eventmagic.event import Event
# import datetime
# import time

def oneOffFunc():
  """My One off Func."""
  print("Hello world!")
  return True

# This event completed as soon as oneOffFunc returns true
event = Event(oneOffFunc, until_success=True)
schedule1 = Schedule()
schedule1.job(event)
# Below is how you would set it with a datetime object
# schedule1.when(datetime.datetime.now() + datetime.timedelta(seconds=2)
# Sleep for 5 seconds so When is no longer in the future...
# time.sleep(5)
# Standard Crontab
schedule1.when("* * * * *")

# If it is only a one off you can simply do this and an Event object will be
# created for you:
schedule2 = Schedule()
schedule2.job(oneOffFunc)
# Extended Crontab
schedule2.when("* * * * * * *")

# Execute once (NB This won't execute as when is set 1 min in the future)
schedule1.execute()

# Execute until successful
while not schedule2.completed:
  schedule2.execute()
```
see [parse-crontab](https://github.com/josiahcarlson/parse-crontab) for more info on what is accepted as a crontab

Recurring events:
```python
from eventmagic.schedule import Schedule
from eventmagic.event import Event


def runForEver():
  """Run for ever"""
  print("Hello World")
  return True

  event = Event(oneOffFunc, count=10)
  schedule1 = Schedule()
  schedule1.job(event)
  schedule1.when("* * * * * * *")
  while not schedule1.completed:
    schedule1.execute()
```

see [example.py](example.py) for more info
