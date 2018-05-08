"""Schedule Module."""

import logging
import datetime
import uuid as pyuuid
from .. import exceptions
from crontab import CronTab
from ..event import Event

logger = logging.getLogger(__name__)


class Schedule(object):
    """Schedule class Stores a list of Jobs for a given schedule."""

    def __init__(self, **kwargs):
        """Create the jobs list.

        :param when: When as a datetime object or a crontab string
        :param cron: The corn string used if one was
        :param id: The id from the DB
        :param uuid: The uuid of the schedule obj
        :param completed: Boolean value fro all jobs completed
        """
        logger.debug("Creating Schedule")
        self._jobs = []
        self._when = kwargs.get("when")
        self._cron = kwargs.get("cron")
        self._id = kwargs.get("id")
        self._uuid = kwargs.get("uuid", pyuuid.uuid4().hex)
        self._completed = kwargs.get("completed", False)

    def __str__(self):
        """Create a printed string."""
        return "UUID: {}, ID: {}, WHEN: {}, CRON: {}, JOBS: {}".format(
            self._uuid, self._id, self._when, self._cron, self._jobs
        )

    @property
    def completed(self):
        """Return the UUID."""
        return self._completed

    @completed.setter
    def completed(self, completed):
        """Set the completed status.

        Raise NotImplementedError to stop it being used
        """
        raise NotImplementedError

    @property
    def uuid(self):
        """Return the UUID."""
        return self._uuid

    @uuid.setter
    def uuid(self, uuid):
        """Set the uuid.

        Raise NotImplementedError to stop it being used
        """
        raise NotImplementedError

    @property
    def id(self):
        """Return the jobs."""
        return self._id

    @id.setter
    def id(self, id):
        """ID Setter."""
        self._id = id

    @property
    def cron(self):
        """Return the jobs."""
        return self._cron

    @cron.setter
    def cron(self, cron):
        """Cron Setter."""
        raise NotImplementedError

    @property
    def jobs(self):
        """Return the jobs."""
        return self._jobs

    @jobs.setter
    def jobs(self, jobs):
        try:
            for job in jobs:
                if isinstance(job, Event):
                    logger.debug("Event Insstance")
                    self._jobs.append(job)
                else:
                    self._jobs.append(Event(job))
        except TypeError:
            logger.debug("Jobs not itterable so trying as individual item")
            if isinstance(jobs, Event):
                logger.debug("Event Insstance")
                self._jobs.append(jobs)
            else:
                self._jobs.append(Event(jobs, until_success=True))
        except Exception as e:
            logger.error("Could not assign Job with error: {}".format(e))
            raise exceptions.JobAssignmentFailed

    @property
    def when(self):
        """Return When a schedule should trigger."""
        return self._when

    @when.setter
    def when(self, value):
        """Given a value work out when it will next be executed.

        :param value: can be datetime (in the future) or a crontab
        """
        if isinstance(value, datetime.date):
            logger.debug("When is a datetime: {}".format(value))
            if value <= datetime.datetime.now():
                logger.error("When is older than now.")
                raise exceptions.WhenValueInPast
            self._when = value
        elif isinstance(value, str):
            logger.debug("When is a string: {}".format(value))
            try:
                entry = CronTab(value)
                self._cron = entry
                # Use the new behaviour, unsure how this breaks things...
                # It all seems overly complicated this time milarky
                next = entry.next(default_utc=False)
                if next > 0:
                    self._when = datetime.datetime.now() + \
                        datetime.timedelta(0, next)
                else:
                    logger.error("When is older than now.")
                    raise exceptions.WhenValueInPast
            except Exception as e:
                logger.error("Exception creating crontab from Value: {} with \
exception {}".format(value, e))
                raise exceptions.FailedToCreateDatetimeFromCronTab

        else:
            logger.error("When is of unknown type")
            raise exceptions.UnknownWhenType

    def remove_job(self, job_uuid):
        """Remove a job from the jobs list.

        :param job_uuid: The job UUID to remove from the list.
        """
        found = False
        new_jobs = list()
        for job in self._jobs:
            if job.uuid != job_uuid:
                new_jobs.append(job)
            else:
                found = True
        if not found:
            logger.info("No job found with uuid: {}".format(job_uuid))
            raise exceptions.JobNotFound
        else:
            logger.debug("Replacing Jobs with new jobs")
            self._jobs = new_jobs

    def execute(self):
        """Execute the jobs.

        :return: True if executed, False if not everything else raises an error
        """
        logger.info("Executing Jobs ({})".format(len(self._jobs)))
        logger.debug("WHEN: {}".format(self._when))
        logger.debug("NOW : {}".format(datetime.datetime.now()))
        # Execute ONLY if When is older than Now.
        if isinstance(self._when, datetime.date)\
                and self._when <= datetime.datetime.now()\
                and not self._completed:
            for job in self._jobs:
                if isinstance(job, Event):
                    logger.debug("Executing event, Job number {}".format(
                        job.uuid
                    ))
                    if not job.completed:
                        try:
                            job.execute()
                        except exceptions.FailedToReturnBooleanValue:
                            return False
                        except exceptions.GeneralEventsException as e:
                            logger.debug("Caught General exception: {}".format(
                                e
                            ))
                            return False
                        except exceptions.EventAlreadyCompleted:
                            logger.info("Event completed between executions")
                    else:
                        logger.debug(
                            "Skipping already completed Job {}".format(
                                job.uuid
                            )
                        )
                else:
                    raise exceptions.JobIsNotAnEventObject
            if all(event.completed for event in self._jobs):
                logger.info("All jobs in a completed condition")
                self._completed = True
                return True
            else:
                logger.info("Rescheduling jobs")
                logger.debug("Checking if cron is an isntance of Crontab")
                if isinstance(self._cron, CronTab):
                    logger.info("Scheduling Next run")
                    self._when = datetime.datetime.now() + datetime.timedelta(
                        seconds=self._cron.next(default_utc=False)
                    )
                    return True
                elif self._cron is None:
                    msg = "Jobs are not 'completed' but no crontab provided. \
For one off tasks set until_success=True on the job(s), set a \
complete_function or provide a crontab"
                    logger.error(msg)
                    raise exceptions.GeneralEventsException(msg)
        else:
            logger.debug("Jobs not executed")
            return False
