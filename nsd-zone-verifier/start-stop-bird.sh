#!/usr/bin/bash

(
	SERIAL=`drill -Q -p $VERIFY_PORT @$VERIFY_IP_ADDRESS $VERIFY_ZONE SOA | awk '{print $3}'`
	MOD3=`expr $SERIAL % 3`
	if [ "x$MOD3" = "x2" ]
	then
		echo `date` serial: $SERIAL - start bird
		service bird start || true
		service bird6 start || true
	else
		echo `date` serial: $SERIAL - stop bird
		service bird stop || true
		service bird6 stop || true
	fi
) >>/tmp/start-stop-bird.log 2>&1

