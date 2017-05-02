import copy as _copy

_TRIGGERS= {
'SI-Glob:TI-Corrs:': {
    'events':('MigSI','Orbit','Study'),
    'trigger_type':'PSSI',
    'devices': (
        'SI-01M1:PS-CH:SRIO', 'SI-01M1:PS-CV:SRIO', 'SI-01M2:PS-CH:SRIO', 'SI-01M2:PS-CV:SRIO', 'SI-01C1:PS-CH:SRIO', 'SI-01C1:PS-CV:SRIO', 'SI-01C2:PS-CH:SRIO', 'SI-01C2:PS-CV-1', 'SI-01C2:PS-CV-2', 'SI-01C3:PS-CH:SRIO', 'SI-01C3:PS-CV-1', 'SI-01C3:PS-CV-2', 'SI-01C4:PS-CH:SRIO', 'SI-01C4:PS-CV:SRIO',
        'SI-02M1:PS-CH:SRIO', 'SI-02M1:PS-CV:SRIO', 'SI-02M2:PS-CH:SRIO', 'SI-02M2:PS-CV:SRIO', 'SI-02C1:PS-CH:SRIO', 'SI-02C1:PS-CV:SRIO', 'SI-02C2:PS-CH:SRIO', 'SI-02C2:PS-CV-1', 'SI-02C2:PS-CV-2', 'SI-02C3:PS-CH:SRIO', 'SI-02C3:PS-CV-1', 'SI-02C3:PS-CV-2', 'SI-02C4:PS-CH:SRIO', 'SI-02C4:PS-CV:SRIO',
        'SI-03M1:PS-CH:SRIO', 'SI-03M1:PS-CV:SRIO', 'SI-03M2:PS-CH:SRIO', 'SI-03M2:PS-CV:SRIO', 'SI-03C1:PS-CH:SRIO', 'SI-03C1:PS-CV:SRIO', 'SI-03C2:PS-CH:SRIO', 'SI-03C2:PS-CV-1', 'SI-03C2:PS-CV-2', 'SI-03C3:PS-CH:SRIO', 'SI-03C3:PS-CV-1', 'SI-03C3:PS-CV-2', 'SI-03C4:PS-CH:SRIO', 'SI-03C4:PS-CV:SRIO',
        'SI-04M1:PS-CH:SRIO', 'SI-04M1:PS-CV:SRIO', 'SI-04M2:PS-CH:SRIO', 'SI-04M2:PS-CV:SRIO', 'SI-04C1:PS-CH:SRIO', 'SI-04C1:PS-CV:SRIO', 'SI-04C2:PS-CH:SRIO', 'SI-04C2:PS-CV-1', 'SI-04C2:PS-CV-2', 'SI-04C3:PS-CH:SRIO', 'SI-04C3:PS-CV-1', 'SI-04C3:PS-CV-2', 'SI-04C4:PS-CH:SRIO', 'SI-04C4:PS-CV:SRIO',
        'SI-05M1:PS-CH:SRIO', 'SI-05M1:PS-CV:SRIO', 'SI-05M2:PS-CH:SRIO', 'SI-05M2:PS-CV:SRIO', 'SI-05C1:PS-CH:SRIO', 'SI-05C1:PS-CV:SRIO', 'SI-05C2:PS-CH:SRIO', 'SI-05C2:PS-CV-1', 'SI-05C2:PS-CV-2', 'SI-05C3:PS-CH:SRIO', 'SI-05C3:PS-CV-1', 'SI-05C3:PS-CV-2', 'SI-05C4:PS-CH:SRIO', 'SI-05C4:PS-CV:SRIO',
        'SI-06M1:PS-CH:SRIO', 'SI-06M1:PS-CV:SRIO', 'SI-06M2:PS-CH:SRIO', 'SI-06M2:PS-CV:SRIO', 'SI-06C1:PS-CH:SRIO', 'SI-06C1:PS-CV:SRIO', 'SI-06C2:PS-CH:SRIO', 'SI-06C2:PS-CV-1', 'SI-06C2:PS-CV-2', 'SI-06C3:PS-CH:SRIO', 'SI-06C3:PS-CV-1', 'SI-06C3:PS-CV-2', 'SI-06C4:PS-CH:SRIO', 'SI-06C4:PS-CV:SRIO',
        'SI-07M1:PS-CH:SRIO', 'SI-07M1:PS-CV:SRIO', 'SI-07M2:PS-CH:SRIO', 'SI-07M2:PS-CV:SRIO', 'SI-07C1:PS-CH:SRIO', 'SI-07C1:PS-CV:SRIO', 'SI-07C2:PS-CH:SRIO', 'SI-07C2:PS-CV-1', 'SI-07C2:PS-CV-2', 'SI-07C3:PS-CH:SRIO', 'SI-07C3:PS-CV-1', 'SI-07C3:PS-CV-2', 'SI-07C4:PS-CH:SRIO', 'SI-07C4:PS-CV:SRIO',
        'SI-08M1:PS-CH:SRIO', 'SI-08M1:PS-CV:SRIO', 'SI-08M2:PS-CH:SRIO', 'SI-08M2:PS-CV:SRIO', 'SI-08C1:PS-CH:SRIO', 'SI-08C1:PS-CV:SRIO', 'SI-08C2:PS-CH:SRIO', 'SI-08C2:PS-CV-1', 'SI-08C2:PS-CV-2', 'SI-08C3:PS-CH:SRIO', 'SI-08C3:PS-CV-1', 'SI-08C3:PS-CV-2', 'SI-08C4:PS-CH:SRIO', 'SI-08C4:PS-CV:SRIO',
        'SI-09M1:PS-CH:SRIO', 'SI-09M1:PS-CV:SRIO', 'SI-09M2:PS-CH:SRIO', 'SI-09M2:PS-CV:SRIO', 'SI-09C1:PS-CH:SRIO', 'SI-09C1:PS-CV:SRIO', 'SI-09C2:PS-CH:SRIO', 'SI-09C2:PS-CV-1', 'SI-09C2:PS-CV-2', 'SI-09C3:PS-CH:SRIO', 'SI-09C3:PS-CV-1', 'SI-09C3:PS-CV-2', 'SI-09C4:PS-CH:SRIO', 'SI-09C4:PS-CV:SRIO',
        'SI-10M1:PS-CH:SRIO', 'SI-10M1:PS-CV:SRIO', 'SI-10M2:PS-CH:SRIO', 'SI-10M2:PS-CV:SRIO', 'SI-10C1:PS-CH:SRIO', 'SI-10C1:PS-CV:SRIO', 'SI-10C2:PS-CH:SRIO', 'SI-10C2:PS-CV-1', 'SI-10C2:PS-CV-2', 'SI-10C3:PS-CH:SRIO', 'SI-10C3:PS-CV-1', 'SI-10C3:PS-CV-2', 'SI-10C4:PS-CH:SRIO', 'SI-10C4:PS-CV:SRIO',
        'SI-11M1:PS-CH:SRIO', 'SI-11M1:PS-CV:SRIO', 'SI-11M2:PS-CH:SRIO', 'SI-11M2:PS-CV:SRIO', 'SI-11C1:PS-CH:SRIO', 'SI-11C1:PS-CV:SRIO', 'SI-11C2:PS-CH:SRIO', 'SI-11C2:PS-CV-1', 'SI-11C2:PS-CV-2', 'SI-11C3:PS-CH:SRIO', 'SI-11C3:PS-CV-1', 'SI-11C3:PS-CV-2', 'SI-11C4:PS-CH:SRIO', 'SI-11C4:PS-CV:SRIO',
        'SI-12M1:PS-CH:SRIO', 'SI-12M1:PS-CV:SRIO', 'SI-12M2:PS-CH:SRIO', 'SI-12M2:PS-CV:SRIO', 'SI-12C1:PS-CH:SRIO', 'SI-12C1:PS-CV:SRIO', 'SI-12C2:PS-CH:SRIO', 'SI-12C2:PS-CV-1', 'SI-12C2:PS-CV-2', 'SI-12C3:PS-CH:SRIO', 'SI-12C3:PS-CV-1', 'SI-12C3:PS-CV-2', 'SI-12C4:PS-CH:SRIO', 'SI-12C4:PS-CV:SRIO',
        'SI-13M1:PS-CH:SRIO', 'SI-13M1:PS-CV:SRIO', 'SI-13M2:PS-CH:SRIO', 'SI-13M2:PS-CV:SRIO', 'SI-13C1:PS-CH:SRIO', 'SI-13C1:PS-CV:SRIO', 'SI-13C2:PS-CH:SRIO', 'SI-13C2:PS-CV-1', 'SI-13C2:PS-CV-2', 'SI-13C3:PS-CH:SRIO', 'SI-13C3:PS-CV-1', 'SI-13C3:PS-CV-2', 'SI-13C4:PS-CH:SRIO', 'SI-13C4:PS-CV:SRIO',
        'SI-14M1:PS-CH:SRIO', 'SI-14M1:PS-CV:SRIO', 'SI-14M2:PS-CH:SRIO', 'SI-14M2:PS-CV:SRIO', 'SI-14C1:PS-CH:SRIO', 'SI-14C1:PS-CV:SRIO', 'SI-14C2:PS-CH:SRIO', 'SI-14C2:PS-CV-1', 'SI-14C2:PS-CV-2', 'SI-14C3:PS-CH:SRIO', 'SI-14C3:PS-CV-1', 'SI-14C3:PS-CV-2', 'SI-14C4:PS-CH:SRIO', 'SI-14C4:PS-CV:SRIO',
        'SI-15M1:PS-CH:SRIO', 'SI-15M1:PS-CV:SRIO', 'SI-15M2:PS-CH:SRIO', 'SI-15M2:PS-CV:SRIO', 'SI-15C1:PS-CH:SRIO', 'SI-15C1:PS-CV:SRIO', 'SI-15C2:PS-CH:SRIO', 'SI-15C2:PS-CV-1', 'SI-15C2:PS-CV-2', 'SI-15C3:PS-CH:SRIO', 'SI-15C3:PS-CV-1', 'SI-15C3:PS-CV-2', 'SI-15C4:PS-CH:SRIO', 'SI-15C4:PS-CV:SRIO',
        'SI-16M1:PS-CH:SRIO', 'SI-16M1:PS-CV:SRIO', 'SI-16M2:PS-CH:SRIO', 'SI-16M2:PS-CV:SRIO', 'SI-16C1:PS-CH:SRIO', 'SI-16C1:PS-CV:SRIO', 'SI-16C2:PS-CH:SRIO', 'SI-16C2:PS-CV-1', 'SI-16C2:PS-CV-2', 'SI-16C3:PS-CH:SRIO', 'SI-16C3:PS-CV-1', 'SI-16C3:PS-CV-2', 'SI-16C4:PS-CH:SRIO', 'SI-16C4:PS-CV:SRIO',
        'SI-17M1:PS-CH:SRIO', 'SI-17M1:PS-CV:SRIO', 'SI-17M2:PS-CH:SRIO', 'SI-17M2:PS-CV:SRIO', 'SI-17C1:PS-CH:SRIO', 'SI-17C1:PS-CV:SRIO', 'SI-17C2:PS-CH:SRIO', 'SI-17C2:PS-CV-1', 'SI-17C2:PS-CV-2', 'SI-17C3:PS-CH:SRIO', 'SI-17C3:PS-CV-1', 'SI-17C3:PS-CV-2', 'SI-17C4:PS-CH:SRIO', 'SI-17C4:PS-CV:SRIO',
        'SI-18M1:PS-CH:SRIO', 'SI-18M1:PS-CV:SRIO', 'SI-18M2:PS-CH:SRIO', 'SI-18M2:PS-CV:SRIO', 'SI-18C1:PS-CH:SRIO', 'SI-18C1:PS-CV:SRIO', 'SI-18C2:PS-CH:SRIO', 'SI-18C2:PS-CV-1', 'SI-18C2:PS-CV-2', 'SI-18C3:PS-CH:SRIO', 'SI-18C3:PS-CV-1', 'SI-18C3:PS-CV-2', 'SI-18C4:PS-CH:SRIO', 'SI-18C4:PS-CV:SRIO',
        'SI-19M1:PS-CH:SRIO', 'SI-19M1:PS-CV:SRIO', 'SI-19M2:PS-CH:SRIO', 'SI-19M2:PS-CV:SRIO', 'SI-19C1:PS-CH:SRIO', 'SI-19C1:PS-CV:SRIO', 'SI-19C2:PS-CH:SRIO', 'SI-19C2:PS-CV-1', 'SI-19C2:PS-CV-2', 'SI-19C3:PS-CH:SRIO', 'SI-19C3:PS-CV-1', 'SI-19C3:PS-CV-2', 'SI-19C4:PS-CH:SRIO', 'SI-19C4:PS-CV:SRIO',
        'SI-20M1:PS-CH:SRIO', 'SI-20M1:PS-CV:SRIO', 'SI-20M2:PS-CH:SRIO', 'SI-20M2:PS-CV:SRIO', 'SI-20C1:PS-CH:SRIO', 'SI-20C1:PS-CV:SRIO', 'SI-20C2:PS-CH:SRIO', 'SI-20C2:PS-CV-1', 'SI-20C2:PS-CV-2', 'SI-20C3:PS-CH:SRIO', 'SI-20C3:PS-CV-1', 'SI-20C3:PS-CV-2', 'SI-20C4:PS-CH:SRIO', 'SI-20C4:PS-CV:SRIO',
        ),
    },
'SI-Glob:TI-Quads:': {
    'events':('MigSI','Tunes','Study'),
    'trigger_type':'PSSI',
    'devices': (
        'SI-Fam:PS-QFA:SRIO', 'SI-Fam:PS-QDA:SRIO', 'SI-Fam:PS-QFB:SRIO', 'SI-Fam:PS-QDB1:SRIO', 'SI-Fam:PS-QDB2:SRIO', 'SI-Fam:PS-QFP:SRIO', 'SI-Fam:PS-QDP1:SRIO', 'SI-Fam:PS-QDP2:SRIO', 'SI-Fam:PS-Q1:SRIO', 'SI-Fam:PS-Q2:SRIO', 'SI-Fam:PS-Q3:SRIO', 'SI-Fam:PS-Q4:SRIO',

        'SI-01C1:PS-Q1:SRIO', 'SI-01C1:PS-Q2:SRIO', 'SI-01C2:PS-Q3:SRIO', 'SI-01C2:PS-Q4:SRIO', 'SI-01C3:PS-Q1:SRIO', 'SI-01C3:PS-Q2:SRIO', 'SI-01C4:PS-Q3:SRIO', 'SI-01C4:PS-Q4:SRIO', 'SI-01M1:PS-QFA:SRIO', 'SI-01M1:PS-QDA:SRIO', 'SI-01M2:PS-QFA:SRIO', 'SI-01M2:PS-QDA:SRIO',
        'SI-05C1:PS-Q1:SRIO', 'SI-05C1:PS-Q2:SRIO', 'SI-05C2:PS-Q3:SRIO', 'SI-05C2:PS-Q4:SRIO', 'SI-05C3:PS-Q1:SRIO', 'SI-05C3:PS-Q2:SRIO', 'SI-05C4:PS-Q3:SRIO', 'SI-05C4:PS-Q4:SRIO', 'SI-05M1:PS-QFA:SRIO', 'SI-05M1:PS-QDA:SRIO', 'SI-05M2:PS-QFA:SRIO', 'SI-05M2:PS-QDA:SRIO',
        'SI-09C1:PS-Q1:SRIO', 'SI-09C1:PS-Q2:SRIO', 'SI-09C2:PS-Q3:SRIO', 'SI-09C2:PS-Q4:SRIO', 'SI-09C3:PS-Q1:SRIO', 'SI-09C3:PS-Q2:SRIO', 'SI-09C4:PS-Q3:SRIO', 'SI-09C4:PS-Q4:SRIO', 'SI-09M1:PS-QFA:SRIO', 'SI-09M1:PS-QDA:SRIO', 'SI-09M2:PS-QFA:SRIO', 'SI-09M2:PS-QDA:SRIO',
        'SI-13C1:PS-Q1:SRIO', 'SI-13C1:PS-Q2:SRIO', 'SI-13C2:PS-Q3:SRIO', 'SI-13C2:PS-Q4:SRIO', 'SI-13C3:PS-Q1:SRIO', 'SI-13C3:PS-Q2:SRIO', 'SI-13C4:PS-Q3:SRIO', 'SI-13C4:PS-Q4:SRIO', 'SI-13M1:PS-QFA:SRIO', 'SI-13M1:PS-QDA:SRIO', 'SI-13M2:PS-QFA:SRIO', 'SI-13M2:PS-QDA:SRIO',
        'SI-17C1:PS-Q1:SRIO', 'SI-17C1:PS-Q2:SRIO', 'SI-17C2:PS-Q3:SRIO', 'SI-17C2:PS-Q4:SRIO', 'SI-17C3:PS-Q1:SRIO', 'SI-17C3:PS-Q2:SRIO', 'SI-17C4:PS-Q3:SRIO', 'SI-17C4:PS-Q4:SRIO', 'SI-17M1:PS-QFA:SRIO', 'SI-17M1:PS-QDA:SRIO', 'SI-17M2:PS-QFA:SRIO', 'SI-17M2:PS-QDA:SRIO',

        'SI-02C1:PS-Q1:SRIO', 'SI-02C1:PS-Q2:SRIO', 'SI-02C2:PS-Q3:SRIO', 'SI-02C2:PS-Q4:SRIO', 'SI-02C3:PS-Q1:SRIO', 'SI-02C3:PS-Q2:SRIO', 'SI-02C4:PS-Q3:SRIO', 'SI-02C4:PS-Q4:SRIO', 'SI-02M1:PS-QFB:SRIO', 'SI-02M1:PS-QDB1:SRIO', 'SI-02M1:PS-QDB2:SRIO', 'SI-02M2:PS-QFB:SRIO', 'SI-02M2:PS-QDB1:SRIO', 'SI-02M2:PS-QDB1:SRIO',
        'SI-04C1:PS-Q1:SRIO', 'SI-04C1:PS-Q2:SRIO', 'SI-04C2:PS-Q3:SRIO', 'SI-04C2:PS-Q4:SRIO', 'SI-04C3:PS-Q1:SRIO', 'SI-04C3:PS-Q2:SRIO', 'SI-04C4:PS-Q3:SRIO', 'SI-04C4:PS-Q4:SRIO', 'SI-04M1:PS-QFB:SRIO', 'SI-04M1:PS-QDB1:SRIO', 'SI-04M1:PS-QDB2:SRIO', 'SI-04M2:PS-QFB:SRIO', 'SI-04M2:PS-QDB1:SRIO', 'SI-04M2:PS-QDB1:SRIO',
        'SI-06C1:PS-Q1:SRIO', 'SI-06C1:PS-Q2:SRIO', 'SI-06C2:PS-Q3:SRIO', 'SI-06C2:PS-Q4:SRIO', 'SI-06C3:PS-Q1:SRIO', 'SI-06C3:PS-Q2:SRIO', 'SI-06C4:PS-Q3:SRIO', 'SI-06C4:PS-Q4:SRIO', 'SI-06M1:PS-QFB:SRIO', 'SI-06M1:PS-QDB1:SRIO', 'SI-06M1:PS-QDB2:SRIO', 'SI-06M2:PS-QFB:SRIO', 'SI-06M2:PS-QDB1:SRIO', 'SI-06M2:PS-QDB1:SRIO',
        'SI-08C1:PS-Q1:SRIO', 'SI-08C1:PS-Q2:SRIO', 'SI-08C2:PS-Q3:SRIO', 'SI-08C2:PS-Q4:SRIO', 'SI-08C3:PS-Q1:SRIO', 'SI-08C3:PS-Q2:SRIO', 'SI-08C4:PS-Q3:SRIO', 'SI-08C4:PS-Q4:SRIO', 'SI-08M1:PS-QFB:SRIO', 'SI-08M1:PS-QDB1:SRIO', 'SI-08M1:PS-QDB2:SRIO', 'SI-08M2:PS-QFB:SRIO', 'SI-08M2:PS-QDB1:SRIO', 'SI-08M2:PS-QDB1:SRIO',
        'SI-10C1:PS-Q1:SRIO', 'SI-10C1:PS-Q2:SRIO', 'SI-10C2:PS-Q3:SRIO', 'SI-10C2:PS-Q4:SRIO', 'SI-10C3:PS-Q1:SRIO', 'SI-10C3:PS-Q2:SRIO', 'SI-10C4:PS-Q3:SRIO', 'SI-10C4:PS-Q4:SRIO', 'SI-10M1:PS-QFB:SRIO', 'SI-10M1:PS-QDB1:SRIO', 'SI-10M1:PS-QDB2:SRIO', 'SI-10M2:PS-QFB:SRIO', 'SI-10M2:PS-QDB1:SRIO', 'SI-10M2:PS-QDB1:SRIO',
        'SI-12C1:PS-Q1:SRIO', 'SI-12C1:PS-Q2:SRIO', 'SI-12C2:PS-Q3:SRIO', 'SI-12C2:PS-Q4:SRIO', 'SI-12C3:PS-Q1:SRIO', 'SI-12C3:PS-Q2:SRIO', 'SI-12C4:PS-Q3:SRIO', 'SI-12C4:PS-Q4:SRIO', 'SI-12M1:PS-QFB:SRIO', 'SI-12M1:PS-QDB1:SRIO', 'SI-12M1:PS-QDB2:SRIO', 'SI-12M2:PS-QFB:SRIO', 'SI-12M2:PS-QDB1:SRIO', 'SI-12M2:PS-QDB1:SRIO',
        'SI-14C1:PS-Q1:SRIO', 'SI-14C1:PS-Q2:SRIO', 'SI-14C2:PS-Q3:SRIO', 'SI-14C2:PS-Q4:SRIO', 'SI-14C3:PS-Q1:SRIO', 'SI-14C3:PS-Q2:SRIO', 'SI-14C4:PS-Q3:SRIO', 'SI-14C4:PS-Q4:SRIO', 'SI-14M1:PS-QFB:SRIO', 'SI-14M1:PS-QDB1:SRIO', 'SI-14M1:PS-QDB2:SRIO', 'SI-14M2:PS-QFB:SRIO', 'SI-14M2:PS-QDB1:SRIO', 'SI-14M2:PS-QDB1:SRIO',
        'SI-16C1:PS-Q1:SRIO', 'SI-16C1:PS-Q2:SRIO', 'SI-16C2:PS-Q3:SRIO', 'SI-16C2:PS-Q4:SRIO', 'SI-16C3:PS-Q1:SRIO', 'SI-16C3:PS-Q2:SRIO', 'SI-16C4:PS-Q3:SRIO', 'SI-16C4:PS-Q4:SRIO', 'SI-16M1:PS-QFB:SRIO', 'SI-16M1:PS-QDB1:SRIO', 'SI-16M1:PS-QDB2:SRIO', 'SI-16M2:PS-QFB:SRIO', 'SI-16M2:PS-QDB1:SRIO', 'SI-16M2:PS-QDB1:SRIO',
        'SI-18C1:PS-Q1:SRIO', 'SI-18C1:PS-Q2:SRIO', 'SI-18C2:PS-Q3:SRIO', 'SI-18C2:PS-Q4:SRIO', 'SI-18C3:PS-Q1:SRIO', 'SI-18C3:PS-Q2:SRIO', 'SI-18C4:PS-Q3:SRIO', 'SI-18C4:PS-Q4:SRIO', 'SI-18M1:PS-QFB:SRIO', 'SI-18M1:PS-QDB1:SRIO', 'SI-18M1:PS-QDB2:SRIO', 'SI-18M2:PS-QFB:SRIO', 'SI-18M2:PS-QDB1:SRIO', 'SI-18M2:PS-QDB1:SRIO',
        'SI-20C1:PS-Q1:SRIO', 'SI-20C1:PS-Q2:SRIO', 'SI-20C2:PS-Q3:SRIO', 'SI-20C2:PS-Q4:SRIO', 'SI-20C3:PS-Q1:SRIO', 'SI-20C3:PS-Q2:SRIO', 'SI-20C4:PS-Q3:SRIO', 'SI-20C4:PS-Q4:SRIO', 'SI-20M1:PS-QFB:SRIO', 'SI-20M1:PS-QDB1:SRIO', 'SI-20M1:PS-QDB2:SRIO', 'SI-20M2:PS-QFB:SRIO', 'SI-20M2:PS-QDB1:SRIO', 'SI-20M2:PS-QDB1:SRIO',

        'SI-03C1:PS-Q1:SRIO', 'SI-03C1:PS-Q2:SRIO', 'SI-03C2:PS-Q3:SRIO', 'SI-03C2:PS-Q4:SRIO', 'SI-03C3:PS-Q1:SRIO', 'SI-03C3:PS-Q2:SRIO', 'SI-03C4:PS-Q3:SRIO', 'SI-03C4:PS-Q4:SRIO', 'SI-03M1:PS-QFP:SRIO', 'SI-03M1:PS-QDP1:SRIO', 'SI-03M1:PS-QDP2:SRIO', 'SI-03M2:PS-QFP:SRIO', 'SI-03M2:PS-QDP1:SRIO', 'SI-03M2:PS-QDP1:SRIO',
        'SI-07C1:PS-Q1:SRIO', 'SI-07C1:PS-Q2:SRIO', 'SI-07C2:PS-Q3:SRIO', 'SI-07C2:PS-Q4:SRIO', 'SI-07C3:PS-Q1:SRIO', 'SI-07C3:PS-Q2:SRIO', 'SI-07C4:PS-Q3:SRIO', 'SI-07C4:PS-Q4:SRIO', 'SI-07M1:PS-QFP:SRIO', 'SI-07M1:PS-QDP1:SRIO', 'SI-07M1:PS-QDP2:SRIO', 'SI-07M2:PS-QFP:SRIO', 'SI-07M2:PS-QDP1:SRIO', 'SI-07M2:PS-QDP1:SRIO',
        'SI-11C1:PS-Q1:SRIO', 'SI-11C1:PS-Q2:SRIO', 'SI-11C2:PS-Q3:SRIO', 'SI-11C2:PS-Q4:SRIO', 'SI-11C3:PS-Q1:SRIO', 'SI-11C3:PS-Q2:SRIO', 'SI-11C4:PS-Q3:SRIO', 'SI-11C4:PS-Q4:SRIO', 'SI-11M1:PS-QFP:SRIO', 'SI-11M1:PS-QDP1:SRIO', 'SI-11M1:PS-QDP2:SRIO', 'SI-11M2:PS-QFP:SRIO', 'SI-11M2:PS-QDP1:SRIO', 'SI-11M2:PS-QDP1:SRIO',
        'SI-15C1:PS-Q1:SRIO', 'SI-15C1:PS-Q2:SRIO', 'SI-15C2:PS-Q3:SRIO', 'SI-15C2:PS-Q4:SRIO', 'SI-15C3:PS-Q1:SRIO', 'SI-15C3:PS-Q2:SRIO', 'SI-15C4:PS-Q3:SRIO', 'SI-15C4:PS-Q4:SRIO', 'SI-15M1:PS-QFP:SRIO', 'SI-15M1:PS-QDP1:SRIO', 'SI-15M1:PS-QDP2:SRIO', 'SI-15M2:PS-QFP:SRIO', 'SI-15M2:PS-QDP1:SRIO', 'SI-15M2:PS-QDP1:SRIO',
        'SI-19C1:PS-Q1:SRIO', 'SI-19C1:PS-Q2:SRIO', 'SI-19C2:PS-Q3:SRIO', 'SI-19C2:PS-Q4:SRIO', 'SI-19C3:PS-Q1:SRIO', 'SI-19C3:PS-Q2:SRIO', 'SI-19C4:PS-Q3:SRIO', 'SI-19C4:PS-Q4:SRIO', 'SI-19M1:PS-QFP:SRIO', 'SI-19M1:PS-QDP1:SRIO', 'SI-19M1:PS-QDP2:SRIO', 'SI-19M2:PS-QFP:SRIO', 'SI-19M2:PS-QDP1:SRIO', 'SI-19M2:PS-QDP1:SRIO',
        ),
    },
'SI-Glob:TI-Skews:': {
    'events':('MigSI','Coupl','Study'),
    'trigger_type':'PSSI',
    'devices': (
        'SI-01M1:PS-QS:SRIO', 'SI-01M2:PS-QS:SRIO', 'SI-01C1:PS-QS:SRIO', 'SI-01C2:PS-QS:SRIO', 'SI-01C3:PS-QS:SRIO',
        'SI-02M1:PS-QS:SRIO', 'SI-02M2:PS-QS:SRIO', 'SI-02C1:PS-QS:SRIO', 'SI-02C2:PS-QS:SRIO', 'SI-02C3:PS-QS:SRIO',
        'SI-03M1:PS-QS:SRIO', 'SI-03M2:PS-QS:SRIO', 'SI-03C1:PS-QS:SRIO', 'SI-03C2:PS-QS:SRIO', 'SI-03C3:PS-QS:SRIO',
        'SI-04M1:PS-QS:SRIO', 'SI-04M2:PS-QS:SRIO', 'SI-04C1:PS-QS:SRIO', 'SI-04C2:PS-QS:SRIO', 'SI-04C3:PS-QS:SRIO',
        'SI-05M1:PS-QS:SRIO', 'SI-05M2:PS-QS:SRIO', 'SI-05C1:PS-QS:SRIO', 'SI-05C2:PS-QS:SRIO', 'SI-05C3:PS-QS:SRIO',
        'SI-06M1:PS-QS:SRIO', 'SI-06M2:PS-QS:SRIO', 'SI-06C1:PS-QS:SRIO', 'SI-06C2:PS-QS:SRIO', 'SI-06C3:PS-QS:SRIO',
        'SI-07M1:PS-QS:SRIO', 'SI-07M2:PS-QS:SRIO', 'SI-07C1:PS-QS:SRIO', 'SI-07C2:PS-QS:SRIO', 'SI-07C3:PS-QS:SRIO',
        'SI-08M1:PS-QS:SRIO', 'SI-08M2:PS-QS:SRIO', 'SI-08C1:PS-QS:SRIO', 'SI-08C2:PS-QS:SRIO', 'SI-08C3:PS-QS:SRIO',
        'SI-09M1:PS-QS:SRIO', 'SI-09M2:PS-QS:SRIO', 'SI-09C1:PS-QS:SRIO', 'SI-09C2:PS-QS:SRIO', 'SI-09C3:PS-QS:SRIO',
        'SI-10M1:PS-QS:SRIO', 'SI-10M2:PS-QS:SRIO', 'SI-10C1:PS-QS:SRIO', 'SI-10C2:PS-QS:SRIO', 'SI-10C3:PS-QS:SRIO',
        'SI-11M1:PS-QS:SRIO', 'SI-11M2:PS-QS:SRIO', 'SI-11C1:PS-QS:SRIO', 'SI-11C2:PS-QS:SRIO', 'SI-11C3:PS-QS:SRIO',
        'SI-12M1:PS-QS:SRIO', 'SI-12M2:PS-QS:SRIO', 'SI-12C1:PS-QS:SRIO', 'SI-12C2:PS-QS:SRIO', 'SI-12C3:PS-QS:SRIO',
        'SI-13M1:PS-QS:SRIO', 'SI-13M2:PS-QS:SRIO', 'SI-13C1:PS-QS:SRIO', 'SI-13C2:PS-QS:SRIO', 'SI-13C3:PS-QS:SRIO',
        'SI-14M1:PS-QS:SRIO', 'SI-14M2:PS-QS:SRIO', 'SI-14C1:PS-QS:SRIO', 'SI-14C2:PS-QS:SRIO', 'SI-14C3:PS-QS:SRIO',
        'SI-15M1:PS-QS:SRIO', 'SI-15M2:PS-QS:SRIO', 'SI-15C1:PS-QS:SRIO', 'SI-15C2:PS-QS:SRIO', 'SI-15C3:PS-QS:SRIO',
        'SI-16M1:PS-QS:SRIO', 'SI-16M2:PS-QS:SRIO', 'SI-16C1:PS-QS:SRIO', 'SI-16C2:PS-QS:SRIO', 'SI-16C3:PS-QS:SRIO',
        'SI-17M1:PS-QS:SRIO', 'SI-17M2:PS-QS:SRIO', 'SI-17C1:PS-QS:SRIO', 'SI-17C2:PS-QS:SRIO', 'SI-17C3:PS-QS:SRIO',
        'SI-18M1:PS-QS:SRIO', 'SI-18M2:PS-QS:SRIO', 'SI-18C1:PS-QS:SRIO', 'SI-18C2:PS-QS:SRIO', 'SI-18C3:PS-QS:SRIO',
        'SI-19M1:PS-QS:SRIO', 'SI-19M2:PS-QS:SRIO', 'SI-19C1:PS-QS:SRIO', 'SI-19C2:PS-QS:SRIO', 'SI-19C3:PS-QS:SRIO',
        'SI-20M1:PS-QS:SRIO', 'SI-20M2:PS-QS:SRIO', 'SI-20C1:PS-QS:SRIO', 'SI-20C2:PS-QS:SRIO', 'SI-20C3:PS-QS:SRIO',
        ),
    },
'SI-Glob:TI-Dips:': {
    'events':('MigSI','Study'),
    'trigger_type':'PSSI',
    'devices': (
        'SI-Fam:PS-B1B2-1:SRIO', 'SI-Fam:PS-B1B2-2:SRIO',
        ),
    },
'SI-Glob:TI-Sexts:': {
    'events':('MigSI','Study'),
    'trigger_type':'PSSI',
    'devices': (
        'SI-Fam:PS-SFA0:SRIO', 'SI-Fam:PS-SFA1:SRIO', 'SI-Fam:PS-SFA2:SRIO', 'SI-Fam:PS-SDA0:SRIO', 'SI-Fam:PS-SDA1:SRIO', 'SI-Fam:PS-SDA2:SRIO', 'SI-Fam:PS-SDA3:SRIO',
        'SI-Fam:PS-SFB0:SRIO', 'SI-Fam:PS-SFB1:SRIO', 'SI-Fam:PS-SFB2:SRIO', 'SI-Fam:PS-SDB0:SRIO', 'SI-Fam:PS-SDB1:SRIO', 'SI-Fam:PS-SDB2:SRIO', 'SI-Fam:PS-SDB3:SRIO',
        'SI-Fam:PS-SFP0:SRIO', 'SI-Fam:PS-SFP1:SRIO', 'SI-Fam:PS-SFP2:SRIO', 'SI-Fam:PS-SDP0:SRIO', 'SI-Fam:PS-SDP1:SRIO', 'SI-Fam:PS-SDP2:SRIO', 'SI-Fam:PS-SDP3:SRIO',
        ),
    },
'BO-Glob:TI-Mags:': {
    'events':('RmpBO','Study'),
    'trigger_type':'rmpbo',
    'devices': (
        'BO-Fam:PS-B-1:SRIO', 'BO-Fam:PS-B-2:SRIO',
        'BO-Fam:PS-SQF:SRIO', 'BO-Fam:PS-SQD:SRIO',
        'BO-Fam:PS-SSF:SRIO', 'BO-Fam:PS-SSD:SRIO',
        'BO-01U:PS-CH:SRIO', 'BO-01U:PS-CV:SRIO', 'BO-03U:PS-CH:SRIO', 'BO-03U:PS-CV:SRIO', 'BO-05U:PS-CH:SRIO', 'BO-05U:PS-CV:SRIO', 'BO-07U:PS-CH:SRIO', 'BO-07U:PS-CV:SRIO', 'BO-09U:PS-CH:SRIO', 'BO-09U:PS-CV:SRIO',
        'BO-11U:PS-CH:SRIO', 'BO-11U:PS-CV:SRIO', 'BO-13U:PS-CH:SRIO', 'BO-13U:PS-CV:SRIO', 'BO-15U:PS-CH:SRIO', 'BO-15U:PS-CV:SRIO', 'BO-17U:PS-CH:SRIO', 'BO-17U:PS-CV:SRIO', 'BO-19U:PS-CH:SRIO', 'BO-19U:PS-CV:SRIO',
        'BO-21U:PS-CH:SRIO', 'BO-21U:PS-CV:SRIO', 'BO-23U:PS-CH:SRIO', 'BO-23U:PS-CV:SRIO', 'BO-25U:PS-CH:SRIO', 'BO-25U:PS-CV:SRIO', 'BO-27U:PS-CH:SRIO', 'BO-27U:PS-CV:SRIO', 'BO-29U:PS-CH:SRIO', 'BO-29U:PS-CV:SRIO',
        'BO-31U:PS-CH:SRIO', 'BO-31U:PS-CV:SRIO', 'BO-33U:PS-CH:SRIO', 'BO-33U:PS-CV:SRIO', 'BO-35U:PS-CH:SRIO', 'BO-35U:PS-CV:SRIO', 'BO-37U:PS-CH:SRIO', 'BO-37U:PS-CV:SRIO', 'BO-39U:PS-CH:SRIO', 'BO-39U:PS-CV:SRIO',
        'BO-41U:PS-CH:SRIO', 'BO-41U:PS-CV:SRIO', 'BO-43U:PS-CH:SRIO', 'BO-43U:PS-CV:SRIO', 'BO-45U:PS-CH:SRIO', 'BO-45U:PS-CV:SRIO', 'BO-47U:PS-CH:SRIO', 'BO-47U:PS-CV:SRIO', 'BO-49U:PS-CH:SRIO', 'BO-49U:PS-CV:SRIO',
        'BO-02D:PS-QS:SRIO',
        ),
    },
'LI-01:TI-EGun:MultBun':{
    'events':('Linac','Study'),
    'trigger_type':'simple',
    'devices':(
        'LI-01:EGun-Trig1',
        ),
    },
'LI-01:TI-EGun:SglBun':{
    'events':('Linac','Study'),
    'trigger_type':'simple',
    'devices':(
        'LI-01:EGun-Trig2',
        ),
    },
'LI-01:TI-Modltr-1:': {
    'events':('Linac','Study'),
    'trigger_type':'simple',
    'devices':(
        'LI-01:RF-Modltr-1',
        ),
    },
'LI-01:TI-Modltr-2:': {
    'events':('Linac','Study'),
    'trigger_type':'simple',
    'devices':(
        'LI-01:RF-Modltr-2',
        ),
    },
'LI-Glob:TI-SHAmp:': {
    'events':('Linac','Study'),
    'trigger_type':'simple',
    'devices':(
        'LI-Glob:RF-SHAmp',
        ),
    },
'LI-Glob:TI-RFAmp-1:': {
    'events':('Linac','Study'),
    'trigger_type':'simple',
    'devices':(
        'LI-Glob:RF-RFAmp-1',
        ),
    },
'LI-Glob:TI-RFAmp-2:': {
    'events':('Linac','Study'),
    'trigger_type':'simple',
    'devices':(
        'LI-Glob:RF-RFAmp-2',
        ),
    },
'LI-Glob:TI-LLRF-1:': {
    'events':('Linac','Study'),
    'trigger_type':'simple',
    'devices':(
        'LI-Glob:RF-LLRF-1',
        ),
    },
'LI-Glob:TI-LLRF-2:': {
    'events':('Linac','Study'),
    'trigger_type':'simple',
    'devices':(
        'LI-Glob:RF-LLRF-2',
        ),
    },
'LI-Glob:TI-LLRF-3:': {
    'events':('Linac','Study'),
    'trigger_type':'simple',
    'devices':(
        'LI-Glob:RF-LLRF-3',
        ),
    },
'TB-04:TI-InjS:': {
    'events':('InjBO','Study'),
    'trigger_type':'simple',
    'devices':(
        'TB-04:PU-InjS',
        ),
    },
'BO-01D:TI-InjK:': {
    'events':('InjBO','Study'),
    'trigger_type':'simple',
    'devices':(
        'BO-01D:PU-InjK',
        ),
    },
'BO-05D:TI-P5Cav:': {
    'events':('InjBO','RmpBO','Study'),
    'trigger_type':'cavity',
    'devices':(
        'BO-05D:RF-P5Cav',
        ),
    },
'BO-48D:TI-EjeK:': {
    'events':('InjSI','Study'),
    'trigger_type':'simple',
    'devices':(
        'BO-48D:PU-EjeK',
        ),
    },
'TS-01:TI-EjeSF:': {
    'events':('InjSI','Study'),
    'trigger_type':'simple',
    'devices':(
        'TS-01:PU-EjeSF',
        ),
    },
'TS-01:TI-EjeSG:': {
    'events':('InjSI','Study'),
    'trigger_type':'simple',
    'devices':(
        'TS-01:PU-EjeSG',
        ),
    },
'TS-Fam:TI-InjSG:': {
    'events':('InjSI','Study'),
    'trigger_type':'simple',
    'devices':(
        'TS-Fam:PU-InjSG',
        ),
    },
'TS-04:TI-InjSF:': {
    'events':('InjSI','Study'),
    'trigger_type':'simple',
    'devices':(
        'TS-04:PU-InjSF',
        ),
    },
'SI-01SA:TI-InjK:': {
    'events':('InjSI','Study'),
    'trigger_type':'simple',
    'devices':(
        'SI-01SA:PU-InjK',
        ),
    },
'LI-Fam:TI-BPM:': {
    'events':('DigLI','Study'),
    'trigger_type':'generic',
    'devices':(
        'LI-Fam:DI-BPM',
        ),
    },
'LI-Fam:TI-Scrn:': {
    'events':('DigLI','Study'),
    'trigger_type':'generic',
    'devices':(
        'LI-Fam:DI-Scrn',
        ),
    },
'LI-01:TI-ICT-1:': {
    'events':('DigLI','Study'),
    'trigger_type':'generic',
    'devices':(
        'LI-01:DI-ICT-1',
        ),
    },
'LI-01:TI-ICT-2:': {
    'events':('DigLI','Study'),
    'trigger_type':'generic',
    'devices':(
        'LI-01:DI-ICT-2',
        ),
    },
'TB-Fam:TI-BPM:': {
    'events':('DigTB','Study'),
    'trigger_type':'generic',
    'devices':(
        'TB-01:DI-BPM-1', 'TB-01:DI-BPM-2', 'TB-02:DI-BPM-1',  'TB-02:DI-BPM-2',  'TB-03:DI-BPM',  'TB-04:DI-BPM',
        ),
    },
'TB-Fam:TI-Scrn:': {
    'events':('DigTB','Study'),
    'trigger_type':'generic',
    'devices':(
        'TB-01:DI-Scrn-1', 'TB-01:DI-Scrn-2', 'TB-02:DI-Scrn-1',  'TB-02:DI-Scrn-2',  'TB-03:DI-Scrn',  'TB-04:DI-Scrn',
        ),
    },
'TB-02:TI-ICT:': {
    'events':('DigTB','Study'),
    'trigger_type':'generic',
    'devices':(
        'TB-02:DI-ICT',
        ),
    },
'TB-04:TI-ICT:': {
    'events':('DigTB','Study'),
    'trigger_type':'generic',
    'devices':(
        'TB-04:DI-ICT',
        ),
    },
'TB-04:TI-FCT:': {
    'events':('DigTB','Study'),
    'trigger_type':'generic',
    'devices':(
        'TB-04:DI-FCT',
        ),
    },
'BO-Fam:TI-BPM:': {
    'events':('DigBO','Study'),
    'trigger_type':'generic',
    'devices':(
        'BO-01U:DI-BPM', 'BO-02U:DI-BPM', 'BO-03U:DI-BPM', 'BO-04U:DI-BPM', 'BO-05U:DI-BPM', 'BO-06U:DI-BPM', 'BO-07U:DI-BPM', 'BO-08U:DI-BPM', 'BO-09U:DI-BPM', 'BO-10U:DI-BPM',
        'BO-11U:DI-BPM', 'BO-12U:DI-BPM', 'BO-13U:DI-BPM', 'BO-14U:DI-BPM', 'BO-15U:DI-BPM', 'BO-16U:DI-BPM', 'BO-17U:DI-BPM', 'BO-18U:DI-BPM', 'BO-19U:DI-BPM', 'BO-20U:DI-BPM',
        'BO-21U:DI-BPM', 'BO-22U:DI-BPM', 'BO-23U:DI-BPM', 'BO-24U:DI-BPM', 'BO-25U:DI-BPM', 'BO-26U:DI-BPM', 'BO-27U:DI-BPM', 'BO-28U:DI-BPM', 'BO-29U:DI-BPM', 'BO-30U:DI-BPM',
        'BO-31U:DI-BPM', 'BO-32U:DI-BPM', 'BO-33U:DI-BPM', 'BO-34U:DI-BPM', 'BO-35U:DI-BPM', 'BO-36U:DI-BPM', 'BO-37U:DI-BPM', 'BO-38U:DI-BPM', 'BO-39U:DI-BPM', 'BO-40U:DI-BPM',
        'BO-41U:DI-BPM', 'BO-42U:DI-BPM', 'BO-43U:DI-BPM', 'BO-44U:DI-BPM', 'BO-45U:DI-BPM', 'BO-46U:DI-BPM', 'BO-47U:DI-BPM', 'BO-48U:DI-BPM', 'BO-49U:DI-BPM', 'BO-50U:DI-BPM',
        ),
    },
'BO-Fam:TI-Scrn:': {
    'events':('DigBO','Study'),
    'trigger_type':'generic',
    'devices':(
        'BO-01D:DI-Scrn-1', 'BO-01D:DI-Scrn-2', 'BO-02U:DI-Scrn',
        ),
    },
'BO-04U:TI-GSL:': {
    'events':('DigBO','Study'),
    'trigger_type':'generic',
    'devices':(
        'BO-04U:DI-GSL',
        ),
    },
'BO-02D:TI-TuneS:': {
    'events':('DigBO','Study'),
    'trigger_type':'generic',
    'devices':(
        'BO-02D:DI-TuneS',
        ),
    },
'BO-04D:TI-TuneP:': {
    'events':('DigBO','Study'),
    'trigger_type':'generic',
    'devices':(
        'BO-04D:DI-TuneP',
        ),
    },
'BO-35D:TI-DCCT:': {
    'events':('DigBO','Study'),
    'trigger_type':'generic',
    'devices':(
        'BO-35D:DI-DCCT',
        ),
    },
'TS-Fam:TI-BPM:': {
    'events':('DigTS','Study'),
    'trigger_type':'generic',
    'devices':(
        'TS-01:DI-BPM', 'TS-02:DI-BPM',  'TS-03:DI-BPM',  'TS-04:DI-BPM-1', 'TS-04:DI-BPM-2',
        ),
    },
'TS-Fam:TI-Scrn:': {
    'events':('DigTS','Study'),
    'trigger_type':'generic',
    'devices':(
        'TS-01:DI-Scrn', 'TS-02:DI-Scrn',  'TS-03:DI-Scrn',  'TS-04:DI-Scrn-1', 'TS-04:DI-Scrn-2', 'TS-04:DI-Scrn-3',
        ),
    },
'TS-01:TI-ICT:': {
    'events':('DigTS','Study'),
    'trigger_type':'generic',
    'devices':(
        'TS-01:DI-ICT',
        ),
    },
'TS-04:TI-ICT:': {
    'events':('DigTS','Study'),
    'trigger_type':'generic',
    'devices':(
        'TS-04:DI-ICT',
        ),
    },
'TS-04:TI-FCT:': {
    'events':('DigTS','Study'),
    'trigger_type':'generic',
    'devices':(
        'TS-04:DI-FCT',
        ),
    },
'SI-19SP:TI-GSL15:': {
    'events':('DigSI','Study'),
    'trigger_type':'generic',
    'devices':(
        'SI-19SP:DI-GSL15',
        ),
    },
'SI-20SB:TI-GSL07:': {
    'events':('DigSI','Study'),
    'trigger_type':'generic',
    'devices':(
        'SI-20SB:DI-GSL07',
        ),
    },
'SI-13C4:TI-DCCT:': {
    'events':('DigSI','Study'),
    'trigger_type':'generic',
    'devices':(
        'SI-13C4:DI-DCCT',
        ),
    },
'SI-14C4:TI-DCCT:': {
    'events':('DigSI','Study'),
    'trigger_type':'generic',
    'devices':(
        'SI-14C4:DI-DCCT',
        ),
    },
'SI-01SA:TI-HTuneS:': {
    'events':('DigSI','Study'),
    'trigger_type':'generic',
    'devices':(
        'SI-01SA:DI-HTuneS',
        ),
    },
'SI-17SA:TI-HTuneP:': {
    'events':('DigSI','Study'),
    'trigger_type':'generic',
    'devices':(
        'SI-17SA:DI-HTuneP',
        ),
    },
'SI-18C4:TI-VTuneS:': {
    'events':('DigSI','Study'),
    'trigger_type':'generic',
    'devices':(
        'SI-18C4:DI-VTuneS',
        ),
    },
'SI-17C4:TI-VTuneP:': {
    'events':('DigSI','Study'),
    'trigger_type':'generic',
    'devices':(
        'SI-17C4:DI-VTuneP',
        ),
    },
'SI-19C4:TI-VPing:': {
    'events':('DigSI','Study'),
    'trigger_type':'generic',
    'devices':(
        'SI-19C4:PU-VPing',
        ),
    },
'SI-01SA:TI-HPing:': {
    'events':('DigSI','Study'),
    'trigger_type':'generic',
    'devices':(
        'SI-01SA:PU-HPing',
        ),
    },
'SI-16C4:TI-GBPM:': {
    'events':('DigSI','Study'),
    'trigger_type':'generic',
    'devices':(
        'SI-16C4:DI-GBPM',
        ),
    },
'SI-Fam:TI-BPM:': {
    'events':('DigSI','Study'),
    'trigger_type':'generic',
    'devices':(
        'SI-01M1:DI-BPM', 'SI-01M2:DI-BPM', 'SI-01C1:DI-BPM-1', 'SI-01C1:DI-BPM-2', 'SI-01C2:DI-BPM', 'SI-01C3:DI-BPM-1', 'SI-01C3:DI-BPM-2', 'SI-01C4:DI-BPM',
        'SI-02M1:DI-BPM', 'SI-02M2:DI-BPM', 'SI-02C1:DI-BPM-1', 'SI-02C1:DI-BPM-2', 'SI-02C2:DI-BPM', 'SI-02C3:DI-BPM-1', 'SI-02C3:DI-BPM-2', 'SI-02C4:DI-BPM',
        'SI-03M1:DI-BPM', 'SI-03M2:DI-BPM', 'SI-03C1:DI-BPM-1', 'SI-03C1:DI-BPM-2', 'SI-03C2:DI-BPM', 'SI-03C3:DI-BPM-1', 'SI-03C3:DI-BPM-2', 'SI-03C4:DI-BPM',
        'SI-04M1:DI-BPM', 'SI-04M2:DI-BPM', 'SI-04C1:DI-BPM-1', 'SI-04C1:DI-BPM-2', 'SI-04C2:DI-BPM', 'SI-04C3:DI-BPM-1', 'SI-04C3:DI-BPM-2', 'SI-04C4:DI-BPM',
        'SI-05M1:DI-BPM', 'SI-05M2:DI-BPM', 'SI-05C1:DI-BPM-1', 'SI-05C1:DI-BPM-2', 'SI-05C2:DI-BPM', 'SI-05C3:DI-BPM-1', 'SI-05C3:DI-BPM-2', 'SI-05C4:DI-BPM',
        'SI-06M1:DI-BPM', 'SI-06M2:DI-BPM', 'SI-06C1:DI-BPM-1', 'SI-06C1:DI-BPM-2', 'SI-06C2:DI-BPM', 'SI-06C3:DI-BPM-1', 'SI-06C3:DI-BPM-2', 'SI-06C4:DI-BPM',
        'SI-07M1:DI-BPM', 'SI-07M2:DI-BPM', 'SI-07C1:DI-BPM-1', 'SI-07C1:DI-BPM-2', 'SI-07C2:DI-BPM', 'SI-07C3:DI-BPM-1', 'SI-07C3:DI-BPM-2', 'SI-07C4:DI-BPM',
        'SI-08M1:DI-BPM', 'SI-08M2:DI-BPM', 'SI-08C1:DI-BPM-1', 'SI-08C1:DI-BPM-2', 'SI-08C2:DI-BPM', 'SI-08C3:DI-BPM-1', 'SI-08C3:DI-BPM-2', 'SI-08C4:DI-BPM',
        'SI-09M1:DI-BPM', 'SI-09M2:DI-BPM', 'SI-09C1:DI-BPM-1', 'SI-09C1:DI-BPM-2', 'SI-09C2:DI-BPM', 'SI-09C3:DI-BPM-1', 'SI-09C3:DI-BPM-2', 'SI-09C4:DI-BPM',
        'SI-10M1:DI-BPM', 'SI-10M2:DI-BPM', 'SI-10C1:DI-BPM-1', 'SI-10C1:DI-BPM-2', 'SI-10C2:DI-BPM', 'SI-10C3:DI-BPM-1', 'SI-10C3:DI-BPM-2', 'SI-10C4:DI-BPM',
        'SI-11M1:DI-BPM', 'SI-11M2:DI-BPM', 'SI-11C1:DI-BPM-1', 'SI-11C1:DI-BPM-2', 'SI-11C2:DI-BPM', 'SI-11C3:DI-BPM-1', 'SI-11C3:DI-BPM-2', 'SI-11C4:DI-BPM',
        'SI-12M1:DI-BPM', 'SI-12M2:DI-BPM', 'SI-12C1:DI-BPM-1', 'SI-12C1:DI-BPM-2', 'SI-12C2:DI-BPM', 'SI-12C3:DI-BPM-1', 'SI-12C3:DI-BPM-2', 'SI-12C4:DI-BPM',
        'SI-13M1:DI-BPM', 'SI-13M2:DI-BPM', 'SI-13C1:DI-BPM-1', 'SI-13C1:DI-BPM-2', 'SI-13C2:DI-BPM', 'SI-13C3:DI-BPM-1', 'SI-13C3:DI-BPM-2', 'SI-13C4:DI-BPM',
        'SI-14M1:DI-BPM', 'SI-14M2:DI-BPM', 'SI-14C1:DI-BPM-1', 'SI-14C1:DI-BPM-2', 'SI-14C2:DI-BPM', 'SI-14C3:DI-BPM-1', 'SI-14C3:DI-BPM-2', 'SI-14C4:DI-BPM',
        'SI-15M1:DI-BPM', 'SI-15M2:DI-BPM', 'SI-15C1:DI-BPM-1', 'SI-15C1:DI-BPM-2', 'SI-15C2:DI-BPM', 'SI-15C3:DI-BPM-1', 'SI-15C3:DI-BPM-2', 'SI-15C4:DI-BPM',
        'SI-16M1:DI-BPM', 'SI-16M2:DI-BPM', 'SI-16C1:DI-BPM-1', 'SI-16C1:DI-BPM-2', 'SI-16C2:DI-BPM', 'SI-16C3:DI-BPM-1', 'SI-16C3:DI-BPM-2', 'SI-16C4:DI-BPM',
        'SI-17M1:DI-BPM', 'SI-17M2:DI-BPM', 'SI-17C1:DI-BPM-1', 'SI-17C1:DI-BPM-2', 'SI-17C2:DI-BPM', 'SI-17C3:DI-BPM-1', 'SI-17C3:DI-BPM-2', 'SI-17C4:DI-BPM',
        'SI-18M1:DI-BPM', 'SI-18M2:DI-BPM', 'SI-18C1:DI-BPM-1', 'SI-18C1:DI-BPM-2', 'SI-18C2:DI-BPM', 'SI-18C3:DI-BPM-1', 'SI-18C3:DI-BPM-2', 'SI-18C4:DI-BPM',
        'SI-19M1:DI-BPM', 'SI-19M2:DI-BPM', 'SI-19C1:DI-BPM-1', 'SI-19C1:DI-BPM-2', 'SI-19C2:DI-BPM', 'SI-19C3:DI-BPM-1', 'SI-19C3:DI-BPM-2', 'SI-19C4:DI-BPM',
        'SI-20M1:DI-BPM', 'SI-20M2:DI-BPM', 'SI-20C1:DI-BPM-1', 'SI-20C1:DI-BPM-2', 'SI-20C2:DI-BPM', 'SI-20C3:DI-BPM-1', 'SI-20C3:DI-BPM-2', 'SI-20C4:DI-BPM',
        ),
    },
'SI-Glob:TI-BbB:': {
    'events':('DigSI','Study'),
    'trigger_type':'generic',
    'devices':(
        'SI-Glob:DI-BbB',
        ),
    },
}

def get_triggers():
    return _copy.deepcopy(_TRIGGERS)
