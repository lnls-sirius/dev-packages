#/bin/bash

function save_pid {
  echo $! >> 'logs/ioc_pids.txt'
  sleep 1
}

function exec_ioc {
  python-sirius as-ma.py "$1" "$2" "$3" "$4" "$5" 1>"logs/$6_stdout.txt" 2>"logs/$6_stderror.txt" &
  save_pid
  echo "Created $6 IOC [$!]"
}

# TB
if [ "$1" = "tb" -o "$1" = "all" -o "$1" = "lt" ]; then
  exec_ioc "TB-" "TB" ".*" "MA" "B.*" "tb_dipole"
  exec_ioc "TB-" "TB" ".*" "MA" "(Q|S|CH|CV|FCH|FCV).*" "1_tb"
fi
# BO
if [ "$1" = "bo" -o "$1" = "all" ]; then
  exec_ioc "BO-" "BO" ".*" "MA" "B.*" "bo_dipole"
  exec_ioc "BO-" "BO" ".*" "MA" "(Q|CH|CV|FCH|FCV).*" "2_bo" # missing sextupoles
fi
# TS
if [ "$1" = "ts" -o "$1" = "all" -o "$1" = "lt" ]; then
  exec_ioc "TS-" "TS" ".*" "MA" "B.*" "ts_dipole"
  exec_ioc "TS-" "TS" ".*" "MA" "(Q|S|CH|CV|FCH|FCV).*" "3_ts"
fi
# SI
# Sirius dipole
if [ "$1" = "si" -o "$1" = "all" -o "$1" = "si-dipole" ]; then
  exec_ioc "SI-" "SI" ".*" "MA" "B.*" "si_dipole"
fi
# Sirius quadrupole families
if [ "$1" = "si" -o "$1" = "all" -o "$1" = "si-quad-fam" ]; then
  exec_ioc "SI-" "SI" "Fam" "MA" "(QD|QF|Q\d).*" "4_si_quad_fam"
fi
# Sirius sextupole families
if [ "$1" = "si" -o "$1" = "all" -o "$1" = "si-sext-fam" ]; then
  exec_ioc "SI-" "SI" "Fam" "MA" "(SD|SF).*" "5_si_sext_fam"
fi
# Sirius trim quadrupoles
if [ "$1" = "si" -o "$1" = "all" -o "$1" = "6_si-quad-trim" ]; then
  for i in {1..20}; do
    if [ "$i" -lt "10" ]; then
      exec_ioc "SI-" "SI" "0$i\w\d" "MA" "(QD|QF|Q\d).*" "7_si_quad_trims_s0$i"
    else
      exec_ioc "SI-" "SI" "$i\w\d" "MA" "(QD|QF|Q\d).*" "8_si_quad_trims_s$i"
    fi
  done
fi
# Sirius correctors
if [ "$1" = "si" -o "$1" = "all" -o "$1" = "si-corr" ]; then
  for i in {1..20}; do
    if [ "$i" -lt "10" ]; then
      exec_ioc "SI-" "SI" "0$i\w\d" "MA" "(CH|CV|FCH|FCV).*" "9_si_correctors_s0$i"
    else
      exec_ioc "SI-" "SI" "$i\w\d" "MA" "(CH|CV|FCH|FCV).*" "10_si_correctors_s$i"
    fi
  done
fi
# Sirius QS
if [ "$1" = "si" -o "$1" = "all" -o "$1" = "si-quad-skew" ]; then
  exec_ioc "SI-" "SI" "(0\d|10)\w\d" "MA" "QS" "11_si_quad_skew_s01-10"
  exec_ioc "SI-" "SI" "(1[1-9]|20)\w\d" "MA" "QS" "12_si_quad_skew_s11-20"
fi
