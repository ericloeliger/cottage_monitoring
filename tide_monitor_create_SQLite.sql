CREATE TABLE IF NOT EXISTS "tide_events" (
	"id" INTEGER NOT NULL,
	"type" VARCHAR(50) NOT NULL,
	"occurrence_count" INTEGER NOT NULL,
	"start_timestamp" INTEGER NOT NULL,
	"end_timestamp" INTEGER NOT NULL
)
;

CREATE TABLE IF NOT EXISTS "tide_events" ("id" INTEGER NOT NULL,"type" VARCHAR(50) NOT NULL,"occurrence_count" INTEGER NOT NULL,"start_timestamp" INTEGER NOT NULL,"end_timestamp" INTEGER NOT NULL);


CREATE TABLE IF NOT EXISTS "tide_events" (
	"type" VARCHAR(50) NOT NULL,
	"occurrence_count" INTEGER NOT NULL,
	"start_timestamp" INTEGER NOT NULL PRIMARY KEY,
	"end_timestamp" INTEGER NULL
)
;


## for inserting dummy row
INSERT INTO tide_events (id, "type", occurrence_count, start_timestamp, end_timestamp) VALUES((SELECT strftime('%s','now')), 'LOW', 1, (SELECT strftime('%s','now')), (SELECT strftime('%s','now')))