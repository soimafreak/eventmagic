create database `eventmagic`;
use `eventmagic`;

/* A store specifically for the Events that make up a schedule */
CREATE TABLE `events` (
  `id` INT NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (id),
  `execute_function` BLOB,
  `execute_params` BLOB,
  `executed` BOOLEAN,
  `executions` INT,
  `count` INT,
  `start_function` BLOB,
  `start_params` BLOB,
  `started` BOOLEAN,
  `complete_function` BLOB,
  `complete_params` BLOB,
  `completed` BOOLEAN,
  `until_success` BOOLEAN,
  `uuid` CHAR(32)
);


/* Store each Schedule */
CREATE TABLE `schedules` (
  `id` INT NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (id),
  `when` DATETIME,
  `cron` BLOB,
  `uuid` CHAR(32),
  `completed` BOOLEAN
);

/* A look up table for events to schedule jobs */
CREATE TABLE `jobs` (
  `event_id` INT NOT NULL,
  `schedule_id` INT NOT NULL,
  FOREIGN KEY (event_id) REFERENCES events (id),
  FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE CASCADE
);
