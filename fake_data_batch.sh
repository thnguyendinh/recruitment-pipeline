#!/bin/bash
BATCH_SIZE=$((RANDOM % 10 + 5))
for i in $(seq 1 $BATCH_SIZE); do
  TS=$(date '+%Y-%m-%d %H:%M:%S').$(printf "%03d" $((RANDOM % 1000)))
  JOB_ID=$(shuf -e 1531 1527 1530 98 187 258 2 188 273 1529 -n 1)
  CUSTOM_TRACK=$(shuf -e click conversion qualified unqualified -n 1)
  BID=$(($RANDOM % 6))
  CAMPAIGN_ID=$(shuf -e 222 1 48 93 4 57 -n 1)
  GROUP_ID=$(shuf -e 30 10 25 41 48 -n 1)
  PUBLISHER_ID=$(shuf -e 1 3 9 22 -n 1)
  docker exec mongodb mongosh -u admin -p admin123 --authenticationDatabase admin --eval "use recruitment; db.tracking.insertOne({ts: \"$TS\", job_id: $JOB_ID, custom_track: \"$CUSTOM_TRACK\", bid: $BID, campaign_id: $CAMPAIGN_ID, group_id: $GROUP_ID, publisher_id: $PUBLISHER_ID})" > /dev/null 2>&1
done
echo "[$(date)] Inserted $BATCH_SIZE logs"
