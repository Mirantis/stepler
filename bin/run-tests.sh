#!/bin/bash -xe

test ! -f $SOURCE_FILE && \
    echo "Your keystonerc file should be mounted to $SOURCE_FILE" && \
    exit 1

source $SOURCE_FILE

if [ ! -d $LOG_DIR ]
then
    echo "------------WARNING------------"
    echo "-----Your log_dir is not mounted to $LOG_DIR-----"
    echo "-----$LOG_DIR will be created-----"
    echo "-----Be attention: if you've run the container with '--rm' key-----"
    echo "-----All reports will be erased-----"
    echo "-------------------------------"
    mkdir -p $LOG_DIR
fi

datetime=`date +%F_%H-%M`
report="report_stepler_$datetime"

log_dir="${LOG_DIR:-/root/stepler_reports/}"

if [ ! -z "$SKIP_LIST" ]
then
    if [ -f "stepler/$SKIP_LIST" ]
    then
        SKIP_LIST="--skip-file stepler/$SKIP_LIST"
    elif [ -f $SKIP_LIST ]
    then
        SKIP_LIST="--skip-file $SKIP_LIST"
    else
        echo "Path to skip list doesn't correct."
    fi
fi

if [ -n "${SPECIFIC_TEST}" ]
then
    SPECIFIC_TEST="-k ${SPECIFIC_TEST}"
fi

if [ -n "${SET}" ]
then
    SET="-m ${SET}"
fi

OPENRC_ACTIVATE_CMD=$(echo $OPENRC_ACTIVATE_CMD |sed 's/\//\\\//g')
sed -i "s/source \/root\/openrc/$OPENRC_ACTIVATE_CMD/g" stepler/config.py

if [[ ! -z ${ARGS+x} || ! -z ${SPECIFIC_TEST+x} ]]
then
    py.test stepler/$ARGS $SPECIFIC_TEST \
    $SKIP_LIST \
    $SET -v \
    --junit-xml=$log_dir$report.xml \
    --html=$log_dir$report.html \
    --self-contained-html \
    --force-destructive || true
else
    py.test stepler/ \
    $SKIP_LIST \
    $SET -v \
    --junit-xml=$log_dir$report.xml \
    --html=$log_dir$report.html \
    --self-contained-html \
    --force-destructive || true
fi