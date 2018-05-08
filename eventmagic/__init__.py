"""Event Magic Package."""

import logging
import pickle
import copy
import mysql.connector
from . import exceptions
from .schedule import Schedule
from .event import Event

logger = logging.getLogger(__name__)


HOST = ""
PORT = "3306"
USERNAME = ""
PASSWORD = ""
DATABASE = "eventmagic"


def db_connection(host, port, username, password, database):
    """Create a Connection to the DB.

    :param host: The Host address for the DB
    :param port: the Port for the DB conenction to use
    :param username: the username to connect with
    :param password: the password to authenticate with
    """
    logger.debug("Connecting to DB")
    cnx = mysql.connector.connect(
        user=username, password=password, host=host,
        port=port, database=database
    )
    return cnx


def function_to_bytecode(func):
    """Save a function.

    :param func: The function to save
    """
    if callable(func):
        logger.log(5, "Manipulate function to json")
        code = pickle.dumps(func, protocol=pickle.HIGHEST_PROTOCOL)
        return code
    else:
        logger.log(5, "Not a function")
        return None


def bytecode_to_function(bytes):
    """Convert json back to a function.

    :param json: the json object to convert back to a python function
    """
    logger.debug(
        "Converting bytes (type: {}) to function".format(
            type(bytes)
        )
    )
    if bytes:
        logger.debug("Creating Function from bytes")
        func = pickle.loads(bytes)
        return func
    else:
        return None


def event_to_tuple(e):
    """Convert an event in to a tuple."""
    if isinstance(e, Event):
        logger.debug("Job is Event Instance: {}".format(e))
        # By Setting the id field of the tuple to NONE we do not need
        # to name every field when inserting them all
        tmp_tup = (
            None,
            function_to_bytecode(e.execute_function),
            pickle.dumps(e.execute_params, protocol=pickle.HIGHEST_PROTOCOL),
            e.executed,
            e.executions,
            e.count,
            function_to_bytecode(e.start_function),
            pickle.dumps(e.start_params, protocol=pickle.HIGHEST_PROTOCOL),
            e.started,
            function_to_bytecode(e.complete_function),
            pickle.dumps(e.complete_params, protocol=pickle.HIGHEST_PROTOCOL),
            e.completed,
            e.until_success,
            e.uuid
        )
        logger.debug("TMP_TUP: {}".format(tmp_tup))
        return tmp_tup
    else:
        raise exceptions.JobIsNotAnEventObject


def get_schedules_from_db():
    """Get Schedules from DB."""
    schedule_query = "SELECT * FROM `schedules`;"
    schedules = list()
    logger.debug("Connecting to server: {}:{} with user {} using DB {}".format(
        HOST, PORT, USERNAME, DATABASE
    ))
    conn = db_connection(HOST, PORT, USERNAME, PASSWORD, DATABASE)
    cursor = conn.cursor()
    logger.debug("Get the schedules from the DB")
    try:
        logger.debug("executing query: {}".format(schedule_query))
        cursor.execute(schedule_query)
        rows = cursor.fetchall()
        logger.info("{} Schedules found".format(cursor.rowcount))
        if not cursor.rowcount:
            logger.warning("No schedules found")
            raise exceptions.NoSchedulesToLoad
        else:
            logger.debug("Schedules found, Creating schedule objects")
            for row in rows:
                # Create a schedule object
                logger.debug("Creating schedule from row {}".format(row))
                tmp_sched = Schedule(
                    id=row[0],
                    when=row[1],
                    cron=pickle.loads(row[2]),
                    uuid=row[3],
                    completed=row[4]
                )
                logger.debug("tmp_sched: {}".format(tmp_sched))
                logger.debug(
                    "created temp_sched {} adding to schedules list".format(
                        tmp_sched.id
                    )
                )
                schedules.append(tmp_sched)
    except Exception as e:
        logger.error("Failed to get schedules with error: {}".format(e))
        raise exceptions.FailedToLoadSchedules(e)
    logger.debug("Returning Schedules from DB: {}".format(schedules))
    return schedules


def get_events_from_db(schedule_id):
    """For a given schedule_id get the Events.

    :param schedule_id: The schedule id of the schedule in the DB
    """
    events_query = "SELECT event_id FROM jobs WHERE schedule_id = %s;"
    conn = db_connection(HOST, PORT, USERNAME, PASSWORD, DATABASE)
    cursor = conn.cursor()
    events = list()
    logger.debug("Getting Events from DB related to schedule: {}".format(
        schedule_id
    ))
    try:
        cursor.execute(events_query, (schedule_id,))
        rows = cursor.fetchall()
        if not cursor.rowcount:
            logger.warning("No Events found")
            raise exceptions.NoEventsToLoad
        else:
            for row in rows:
                # Create a schedule object
                logger.debug("Result row is: {}".format(row))
                events.append(get_event(row[0]))
    except Exception as e:
        logger.error("Failed to get Events from DB")
        raise exceptions.FailedToLoadEvents(e)
    return events


def get_event(event_id):
    """Get an Event from the DB by Event ID.

    :param event_id: The event to get
    """
    conn = db_connection(HOST, PORT, USERNAME, PASSWORD, DATABASE)
    cursor = conn.cursor()
    event_query = "SELECT * FROM events WHERE id = %s;"
    cursor.execute(event_query, (event_id, ))
    row = cursor.fetchone()
    if not cursor.rowcount:
        logger.warning("No Event found")
        raise exceptions.NoEventsToLoad
    else:
        tmp_event = Event(
            bytecode_to_function(row[1]),
            execute_params=pickle.loads(row[2]),
            executed=row[3],
            executions=row[4],
            count=row[5],
            start_function=bytecode_to_function(row[6]),
            start_params=pickle.loads(row[7]),
            started=row[8],
            complete_function=bytecode_to_function(row[9]),
            complete_params=pickle.loads(row[10]),
            completed=row[11],
            until_success=row[12],
            uuid=row[13],
            id=row[0]
        )
        return tmp_event


def update(schedule):
    """Update the Schedule."""
    logger.debug("Updating schedule rather than creating new")
    conn = db_connection(HOST, PORT, USERNAME, PASSWORD, DATABASE)
    cursor = conn.cursor()
    schedule_query = "UPDATE `schedules` SET `when`=%s, completed=%s \
WHERE id=%s;"
    schedule_params = (
        schedule.when,
        schedule.completed,
        schedule.id
    )
    try:
        logger.info("Updating schedule {}".format(schedule.uuid))
        cursor.execute(schedule_query, schedule_params)
    except Exception as e:
        logger.error("Updating schedule {} Failed. with error {}".format(
            schedule.uuid, e
        ))
    for job in schedule.jobs:
        # Test to make sure the job has an ID whcih it should
        logger.debug("Updating job: {}".format(job))
        if job.id:
            event_query = "UPDATE `events` SET executed=%s, executions=%s, \
count=%s, started=%s, stopped=%s where id = %s;"
            event_params = (
                job.executed,
                job.executions,
                job.count,
                job.started,
                job.completed,
                job.id
            )
            try:
                logger.debug("Updating event")
                cursor.execute(event_query, event_params)
            except Exception as e:
                logger.error("Updating event {} Failed. with error {}".format(
                    job.uuid, e
                ))
        else:
            raise exceptions.JobHasNoId(
                "Can't update Job as it has not been saved to the DB before"
            )
    logger.info("committing changes to DB")
    conn.commit()

    logger.debug("All Done with Updating schedules, closing connection.")
    # Now everything has been inserted save the changes
    # Close the specific query
    cursor.close()
    # Close the connection
    conn.close()
    return True


def save(schedules):
    """Save the schedules.

    :param schedules: A list of schedule objects
    """
    conn = db_connection(HOST, PORT, USERNAME, PASSWORD, DATABASE)
    cursor = conn.cursor()
    logger.debug("Saving Schedules: {}".format(schedules))
    for schedule in schedules:
        tmp_jobs = list()
        logger.info("Saving schedule:")
        logger.debug("UUID: {} TYPE: {}".format(
            schedule.uuid, type(schedule.uuid)
        ))
        if schedule.id:
            # Only has an schedule.id if it's been loaded from the DB
            update(schedule)
            continue
        else:
            schedule_query = "INSERT INTO `schedules` \
VALUES(%s, %s, %s, %s, %s);"
            schedule_params = (
                None,
                schedule.when,
                pickle.dumps(schedule.cron, protocol=pickle.HIGHEST_PROTOCOL),
                schedule.uuid,
                schedule.completed
            )
        try:
            logger.debug("Saving Schedule")
            logger.debug("Query: {}, Params: {}".format(
                schedule_query,
                schedule_params
            ))
            cursor.execute(schedule_query, schedule_params)
            schedule_id = cursor.lastrowid
        except Exception as e:
            logger.error("Failed to save Schedule with error: {}".format(e))
            logger.info("rolling back save")
            cursor.close()
            conn.close()
            return False

        logger.debug("Saving Jobs: {}".format(schedule.jobs))
        for job in schedule.jobs:
            # Package each job ready for saving
            logger.debug("Creating Temp job tuple for {}".format(job))
            logger.debug("Adding Job to tmp_jobs: {}".format(tmp_jobs))
            try:
                tmp_jobs.append(event_to_tuple(job))
            except exceptions.JobIsNotAnEventObject:
                logger.error("job is not an Event")

        logger.debug("Saving Events: {}".format(tmp_jobs))
        for row in tmp_jobs:
            logger.debug("Inserting event: {}".format(row))
            event_query = "INSERT INTO `events` VALUES(%s, %s, %s, %s, %s, \
%s, %s, %s, %s, %s, %s, %s, %s, %s);"
            job_query = "INSERT INTO `jobs` VALUES(%s, %s);"
            try:
                logger.debug("Inserting {} of type {} into events with query \
{}".format(row, type(row), event_query))
                cursor.execute(event_query, row)
            except Exception as e:
                logger.error(
                    "Failed to insert event with error: {}".format(e)
                )
                logger.warning("rolling back save")
                cursor.close()
                conn.close()
                return False
            try:
                # Sets the event_id to the last row inserti id
                logger.debug("Save the Job")
                cursor.execute(job_query, (cursor.lastrowid, schedule_id))
            except Exception as e:
                logger.error(
                    "Failed to insert job with error: {}".format(e)
                )
                logger.warning("rolling back save")
                cursor.close()
                conn.close()
                return False
        logger.debug("Schedule Saved")
        # Commit the result (if it was a data change)
        logger.info("committing changes to DB")
        conn.commit()

    logger.debug("All Done with Saving schedules, closing connection.")
    # Now everything has been inserted save the changes
    # Close the specific query
    cursor.close()
    # Close the connection
    conn.close()
    return True


def load():
    """Load the Schedules from the DB."""
    try:
        schedules = get_schedules_from_db()
    except exceptions.NoSchedulesToLoad:
        logger.warning("No Schedules found")

    for schedule in schedules:
        logger.debug("Get the Events / Jobs for the schedule")
        try:
            events = get_events_from_db(schedule.id)
            logger.debug("Adding events ({}) to schedule {} jobs list".format(
                events, schedule.id
            ))
            schedule.jobs = events
            logger.debug("Schedule jobs is now: {}".format(schedule.jobs))
        except exceptions.NoEventsToLoad:
            logger.warning("No Events in schedule")
        logger.debug("Schedule is: {}".format(schedule))
        logger.debug("Schedule.id is: {}".format(schedule.id))
        logger.debug("Schedule.jobs: {}".format(schedule.jobs))
        logger.debug("EVENT: {}".format(schedule.jobs[0]))
    logger.debug("Returning schedules: {}".format(schedules))
    return schedules


def remove_schedule(schedules, schedule_uuid):
    """Remove the Schedule.

    :param schedules: A list of schedules
    :param schedule_uuid: The schedule to remove
    """
    if not isinstance(schedules, list):
        msg = "Provide a list of scheduled items"
        logger.error(msg)
        raise exceptions.NoSchedulesProvided(msg)
    dupe_schedules = copy.deepcopy(schedules)
    logger.debug("Created deep copy of schedules: {} and {}".format(
        schedules, dupe_schedules
    ))
    for schedule in dupe_schedules:
        logger.debug("Checking Schedule {} for uuid: {}".format(
            schedule, schedule_uuid
        ))
        if schedule.uuid == schedule_uuid:
            logger.info("Found Schedule in EventMagic")
            try:
                schedules.remove(schedule)
            except ValueError as e:
                logger.error(
                    "This should not happen, tried to remove {} from ".format(
                        schedule
                    )
                )
                logger.debug(
                    "By catching this error, the schedule can be removed from \
the database so on the next run it won't run multiple times. If this is an \
in-memory invocation it should not even have this issue..."
                )
                for i in schedules:
                    logger.debug("Schedule: {}".format(i))
            if schedule.id:
                # Has an Entry in the DB
                for event in schedule.jobs:
                    if event.id:
                        # If the event has an id it is also from the db
                        # NB May not want to do this later if an event is
                        # used by multiple schedules
                        remove_event_from_db(event.id)
                conn = db_connection(HOST, PORT, USERNAME, PASSWORD, DATABASE)
                cursor = conn.cursor()
                delete_query = "DELETE FROM `scedules` WHERE id=%s;"
                delete_params = (schedule.id,)
                try:
                    logger.info("Removing schedule id: {}".format(schedule.id))
                    cursor.execute(delete_query, delete_params)
                    logger.debug("Deleted {} Rows".format(cursor.rowcount))
                except Exception as e:
                    logger.error(
                        "Deleting Schedule failed with error: {}".format(e)
                    )
                    raise exceptions.FailedToDeleteSchedule(e)


def remove_event_from_db(event_id):
    """Remove event from the DB.

    :param event_id: The event to remove
    """
    conn = db_connection(HOST, PORT, USERNAME, PASSWORD, DATABASE)
    cursor = conn.cursor()
    delete_query = "DELETE FROM `events` WHERE id=%s;"
    delete_params = (event_id,)
    try:
        logger.info("Removing event id: {}".format(event_id))
        cursor.execute(delete_query, delete_params)
        # Good chance this doesn't work...
        logger.debug("Deleted {} Rows".format(cursor.rowcount))
    except Exception as e:
        logger.error(
            "Deleting Schedule failed with error: {}".format(e)
        )
        raise exceptions.FailedToDeleteEvent(e)
