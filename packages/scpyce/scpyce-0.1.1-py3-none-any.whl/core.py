"""
Console program for running solver.
"""
import time

from engine import lind_solver # pylint: disable=import-error
from src.database import model # pylint: disable=import-error

DB_PATH = input('Provide path to database model:')

if DB_PATH == '':
    DB_PATH = '/home/nicbencini/scpyce_solver/tests/test_files/database_1_model_test.db'

RUN_INPUT = None

while RUN_INPUT != 'n':

    RUN_INPUT = input('Run solver? (y/n)')

    if RUN_INPUT == 'y':

        startTime = time.time()
        print('Solver Initialized.....')

        structural_model = model.Model(DB_PATH)

        result = lind_solver.solve(structural_model)

        structural_model.close_connection()

        executionTime = time.time() - startTime
        print('Execution time in seconds: ' + str(executionTime))
