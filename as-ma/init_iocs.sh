#/bin/bash

function save_pid {
  echo $! >> 'logs/ioc_pids.txt'
  sleep 1
}

function exec_ioc {
  python3.6 as-ma.py "$1" "$2" "$3" "$4" "$5" 1>"logs/$6_stdout.txt" 2>"logs/$6_stderror.txt" &
  # python3.6 as-ma.py "$1" "$2" "$3" "$4" "$5" &
  save_pid
  echo "Created $6 IOC [$!]"
}

# TB
if [ "$1" = "tb" -o "$1" = "all" -o "$1" = "lt" ]; then
  exec_ioc "TB-" "TB" ".*" "MA" "B.*" "1_tb_dipole"
  exec_ioc "TB-" "TB" ".*" "MA" "(Q|S|CH|CV|FCH|FCV).*" "2_tb"
fi
# BO
if [ "$1" = "bo" -o "$1" = "all" ]; then
  exec_ioc "BO-" "BO" ".*" "MA" "B.*" "3_bo_dipole"
  exec_ioc "BO-" "BO" ".*" "MA" "(Q|S|CH|CV|FCH|FCV).*" "4_bo" # missing sextupoles
fi
# TS
if [ "$1" = "ts" -o "$1" = "all" -o "$1" = "lt" ]; then
  exec_ioc "TS-" "TS" ".*" "MA" "B.*" "5_ts_dipole"
  exec_ioc "TS-" "TS" ".*" "MA" "(Q|S|CH|CV|FCH|FCV).*" "6_ts"
fi
# SI
# Sirius dipole
if [ "$1" = "si" -o "$1" = "all" -o "$1" = "si-dipole" ]; then
  exec_ioc "SI-" "SI" ".*" "MA" "B.*" "7_si_dipole"
fi
# Sirius quadrupole families
if [ "$1" = "si" -o "$1" = "all" -o "$1" = "si-quad-fam" ]; then
  exec_ioc "SI-" "SI" "Fam" "MA" "(QD|QF|Q\d).*" "8_si_quad_fam"
fi
# Sirius sextupole families
if [ "$1" = "si" -o "$1" = "all" -o "$1" = "si-sext-fam" ]; then
  exec_ioc "SI-" "SI" "Fam" "MA" "(SD|SF).*" "9_si_sext_fam"
fi
# Sirius trim quadrupoles
if [ "$1" = "si" -o "$1" = "all" -o "$1" = "10_si-quad-trim" ]; then
  for i in {1..20}; do
    if [ "$i" -lt "10" ]; then
      exec_ioc "SI-" "SI" "0$i\w\d" "MA" "(QD|QF|Q\d).*" "11_si_quad_trims_s0$i"
    else
      exec_ioc "SI-" "SI" "$i\w\d" "MA" "(QD|QF|Q\d).*" "12_si_quad_trims_s$i"
    fi
  done
fi
# Sirius correctors
if [ "$1" = "si" -o "$1" = "all" -o "$1" = "si-corr" ]; then
  for i in {1..20}; do
    if [ "$i" -lt "10" ]; then
      exec_ioc "SI-" "SI" "0$i\w\d" "MA" "(CH|CV|FCH|FCV).*" "13_si_correctors_s0$i"
    else
      exec_ioc "SI-" "SI" "$i\w\d" "MA" "(CH|CV|FCH|FCV).*" "14_si_correctors_s$i"
    fi
  done
fi
# Sirius QS
if [ "$1" = "si" -o "$1" = "all" -o "$1" = "si-quad-skew" ]; then
  exec_ioc "SI-" "SI" "(0\d|10)\w\d" "MA" "QS" "15_si_quad_skew_s01-10"
  exec_ioc "SI-" "SI" "(1[1-9]|20)\w\d" "MA" "QS" "16_si_quad_skew_s11-20"
fi
