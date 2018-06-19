#!/usr/bin/env bash

WEB_PATH=$LNLS_SIRIUS/control-system-constants
PS_PATH=$WEB_PATH/pwrsupply
MA_PATH=$WEB_PATH/magnet

rm -rf ./pwrsupply
rm -rf ./magnet
rm -rf ./beaglebone

cp -rf $WEB_PATH/pwrsupply ./
cp -rf $WEB_PATH/magnet ./
cp -rf $WEB_PATH/beaglebone ./

