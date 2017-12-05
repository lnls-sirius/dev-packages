#!/usr/bin/env bash

WEB_PATH=$LNLS_SIRIUS/control-system-constants
PS_PATH=$WEB_PATH/pwrsupply
MA_PATH=$WEB_PATH/magnet

# --- Power Supplies ---
cp -rf $PS_PATH/pstypes-names.txt ./
cp -rf $PS_PATH/pstypes-setpoint-limits.txt ./
cp -rf $PS_PATH/putypes-setpoint-limits.txt ./

# --- Magnets ---
cp -rf $MA_PATH/excitation-data/* ./
cp -rf $MA_PATH/magnet-excitation-ps.txt ./
cp -rf $MA_PATH/magnet-setpoint-limits.txt ./
cp -rf $MA_PATH/pulsed-magnet-setpoint-limits.txt ./
