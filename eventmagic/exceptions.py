"""Exceptions module."""

import logging

logger = logging.getLogger(__name__)


class UnknownWhenType(Exception):
    """Exception class for When Type errors."""

    pass


class WhenValueInPast(Exception):
    """Exception class for When Value is in the past."""

    pass


class FailedToCreateDatetimeFromCronTab(Exception):
    """Exception class for Failed to create datetime from crontab."""

    pass


class FailedToReturnBooleanValue(Exception):
    """Exception class for when a method faisl to return boolean value."""

    pass


class JobIsNotAnEventObject(Exception):
    """Exception class for a job that is not an event object."""

    pass


class JobAssignmentFailed(Exception):
    """Exception class for a job that could not be assigned."""

    pass


class JobNotFound(Exception):
    """Exception for Job not found."""

    pass


class JobHasNoId(Exception):
    """Job has no ID."""

    def __init__(self, message):
        """General Events Error."""
        self.message = message
        logger.error(self.message)


class GeneralEventsException(Exception):
    """No Function Defined Error."""

    def __init__(self, message):
        """General Events Error."""
        self.message = message
        logger.warning(self.message)


class FailedToLoadSchedules(Exception):
    """Exception class for failure to laod schedules."""

    pass


class FailedToDeleteSchedule(Exception):
    """Exception class for failure to delete schedule."""

    pass


class FailedToDeleteEvent(Exception):
    """Exception class for failure to delete Event."""

    pass


class NoSchedulesToLoad(Exception):
    """Exception class for when there are no schedules to load."""

    pass


class NoSchedulesProvided(Exception):
    """Exception class for when there are no schedules to work through."""

    pass


class NoEventsToLoad(Exception):
    """Exception class for when there are no events to load."""

    pass


class FailedToLoadEvents(Exception):
    """Exception class for failure to laod Events."""

    pass
