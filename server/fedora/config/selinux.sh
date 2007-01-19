#!/bin/bash

SESTAT=`getenforce`
setenforce 0
semanage user -P user -R user_r -R afsagent_r -a afsagent_u
semanage login -s afsagent_u -a afsagent
setenforce $SESTAT
