"""Example of using event magic."""


from eventmagic.schedule import Schedule
from eventmagic.event import Event
import eventmagic
import datetime
import logging
import time

# Set up the root logger
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


fh = logging.FileHandler('example.log')
fh.setLevel(logging.DEBUG)
logging.getLogger().addHandler(fh)

if __name__ == '__main__':
    logger = logging.getLogger('example')
else:
    logger = logging.getLogger(__name__)

logger.debug(
    "Simple example of an event / action with the schedule / evnents"
)

logger.debug("Set up the DB connection")
eventmagic.HOST = "localhost"
eventmagic.USERNAME = "root"
eventmagic.PASSWORD = "thisisroot"


def action():
    """Run in the event."""
    print("I'm Running! {}".format(datetime.datetime.now()))
    # Event must return bool for success / failure
    return True


# Creates a single schedulable item
sched = Schedule()
event = Event(action, until_success=True)

logger.debug("Event: {}".format(event))
logger.debug("execute_funtion: {}\nCode: {}\nName: {}\nGlobals: {}".format(
    event.execute_function, event.execute_function.__code__,
    event.execute_function.__name__, event.execute_function.__globals__
))

sched.jobs = event
# If it's not an event object it becomes one but will have until_success=True
# Set so it will only execute Once.
sched.jobs = action
# Never execute as When is always 10 mins in the future
# sched.when = datetime.datetime.now() + datetime.timedelta(minutes=10)
# Also Never runs as it always gets "next" as "now" has been missed
# sched.when = "* * * * * *"
# Force this in the furture by 1 day so it passes the setter condition
# Of not being in the past and by the time it is checked it is now or the past
sched.when = datetime.datetime.now() + datetime.timedelta(1)


logger.debug("Event object: {}".format(event))
logger.debug("Schedule Object: {}".format(sched))

logger.debug("Execute schedule, Nothing happens as it is in the future")
try:
    if sched.execute():
        logger.info("Jobs Executed!!!")
    else:
        logger.info("No Jobs Run!")
except Exception as e:
    logger.error("jobs failed with: {}".format(e))
logger.debug("Set for 5 seconds away and sleep...")
sched.when = datetime.datetime.now() + datetime.timedelta(seconds=3)
time.sleep(5)
logger.debug("Executing again....")
sched.execute()
logger.debug(
    "Now it is exeuted (we added an event and a function directly so there's \
2 executions)"
)


# Reset When so it will run when it is next executed
sched.when = datetime.datetime.now() + datetime.timedelta(seconds=1)
logging.debug(
    "Now Store the data into the DB and, create new objects from the data in \
the db and then execute"
)

eventmagic.save([sched])

logger.debug("Sleep between save and load")
time.sleep(2)
# Returns a list of each scheduled item
logger.debug("Load the events!")
schedules = eventmagic.load()
logger.debug("Loop over each schedule and execute")
for schedule in schedules:
    logger.debug("Executing schedule {}".format(schedule.id))
    schedule.execute()

logger.debug("Schedule completed? {}".format(schedule.completed))
