"""Event Class.

This is where an Event is defined ready to be used.
"""

from .. import exceptions
import logging
import functools
import uuid as pyuuid

logger = logging.getLogger(__name__)


class Event(object):
    """The Event class represents a singular Event."""

    def __init__(self, execute_function, **kwargs):
        """Instantiate the Event Object.

        :param execute_function: The function to execute, must return a boolean
        value for succes.
        :param execute_params: A Dictionary of key value pairs to pass into the
        *execute_function*
        :param count: How many times to execute the event, 0 is infinite
        *default=0*
        :param start_function: Optional function that returns a boolean value
        When this function returns True the job will execute
        :param start_params: A dictionary of key value pairs to pass into the
        *start_function*
        :param complete_function: Optional function that returns a boolean
        value when it is called to stop the event being scheduled again.
        :param complete_params: A dictionary of key value pairs to pass into
        the *complete_function*
        :param completed: A Bool for if the function completed
        :until_success: A Boolean value that ensures an event is re-scheduled
        until it passes successfully
        """
        self.execute_function = execute_function
        self.execute_params = kwargs.get("execute_params", {})
        self.executed = kwargs.get("executed")
        self.executions = kwargs.get("executions", 0)
        self.count = kwargs.get("count", 0)
        self.start_function = kwargs.get("start_function")
        self.start_params = kwargs.get("start_params", {})
        self.started = kwargs.get("started")
        self.complete_function = kwargs.get("complete_function")
        self.complete_params = kwargs.get("complete_params", {})
        self.completed = kwargs.get("completed", False)
        self.until_success = kwargs.get("until_success", False)
        self.uuid = kwargs.get("uuid", pyuuid.uuid4().hex)
        self._id = kwargs.get("id")

    def __str__(self):
        """Create a printed string."""
        return "<\"execute_function\": {}, \"execute_params\": {}, \
\"executed\": {}, \"executions\": {}, \"count\": {}, \"start_function\": {}, \
\"start_params\": {}, \"started\": {}, \"complete_function\": {}, \
\"complete_params\": {}, \"completed\": {}, \"until_success\": {}, \
\"uuid\": {}, \"id\": {}>".format(
            self.execute_function,
            self.execute_params,
            self.executed,
            self.executions,
            self.count,
            self.start_function,
            self.start_params,
            self.started,
            self.complete_function,
            self.complete_params,
            self.completed,
            self.until_success,
            self.uuid,
            self._id
        )

    @property
    def id(self):
        """Return the jobs."""
        return self._id

    @id.setter
    def id(self, id):
        """ID Setter."""
        return self._id

    def _run(self, function, params):
        """For a given function run it with the params.

        :param function: The function to run
        :param params: The key word params to pass in
        """
        logger.debug("Preparing to execute function: {}".format(
            function.__name__
        ))
        if isinstance(params, dict):
            tmp_func = functools.partial(function, **params)
            return tmp_func()
        else:
            msg = "Params must be a dictionary"
            logger.error(msg)
            raise exceptions.GeneralEventsException(msg)

    def execute(self):
        """Execute the event."""
        logger.info("Execute event")
        if self.completed:
            # This is not necessarily a bad thing. One event may complete
            # While another has not, so not all jobs in a schedule would have
            # Completed. This raises an error if a completed job is run as it
            # should be skipped
            msg = "Event completed on a previous run"
            logger.warning(msg)
            raise exceptions.GeneralEventsException(msg)
        if self.count == 0 or self.executions < self.count:
            # Count is unset (or unlimited) or executions is less than count
            logger.debug("Start function is TYPE: {}".format(
                type(self.start_function)
            ))
            if self.start_function is None or self.start():
                # Fail if start condition is set and returning false
                if self.execute_function:
                    try:
                        response = self._run(
                            self.execute_function, self.execute_params
                        )
                        logger.debug("RESPONSE is: {} of TYPE: {}".format(
                            response, type(response)
                        ))
                        self.executed = True
                        self.executions += 1
                    except Exception as e:
                        logger.error(
                            "Failed to execute event with error: {}".format(e)
                        )
                    if isinstance(response, bool):
                        if response:
                            if self.until_success:
                                self.completed = True
                    else:
                        logger.error("Failed to return Boolean value")
                        raise exceptions.FailedToReturnBooleanValue

                    # Test to see if it should run one more time
                    if self.complete_function is not None \
                            and self.complete():
                        self.completed = True
                    return response
                else:
                    msg = "No Execute function defined"
                    raise exceptions.GeneralEventsException(msg)
            else:
                if self.start_function is None:
                    logger.info("No Start function defined")
                else:
                    logger.warning("Start condition failed")
        else:
            logger.info("Count exceeded")
            self.completed = True

    def start(self):
        """Execute the start conditional function."""
        logger.debug("Run the start condition")
        if self.start_function:
            try:
                response = self._run(self.start_function, self.start_params)
            except Exception as e:
                logger.error(
                    "Error executing complete function: {} with the following \
error {}".format(
                        self.start_function.__name__, e
                    )
                )
            logger.debug("Start response is {}".format(response))
            if response:
                self.started = True
                return True
            else:
                self.started = False
                return False
        else:
            msg = "No Start function defined"
            raise exceptions.GeneralEventsException(msg)

    def complete(self):
        """Execute the stop conditional function."""
        logger.info("Run the complete condition")
        if self.complete_function:
            try:
                response = self._run(
                    self.complete_function, self.complete_params
                )
            except Exception as e:
                logger.error(
                    "Error executing complete function: {} with the following \
error {}".format(
                        self.complete_function.__name__, e
                    )
                )
            logger.debug("Complete response is {}".format(response))
            if response:
                self.completed = True
                return True
            else:
                self.completed = False
                return False
        else:
            msg = "No Complete function defined"
            raise exceptions.GeneralEventsException(msg)
