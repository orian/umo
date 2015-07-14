#!/usr/bin/python

import argparse
import json
import psycopg2

def test_db():
  try:
    conn = psycopg2.connect("dbname='bip' user='bip_ro' host='localhost' password='bipro'")
  except:
    print "I am unable to connect to the database"

if __name__=='__main__':
  parser = argparse.ArgumentParser(description='Exports item to DB.')
  parser.add_argument('--db_config', type=str, help='file with json encoded config of db connection')
  #parser.add_argument('--city', type=str, help='')
  parser.add_argument('--city_id', type=str, help='id of city (in DB)')
  parser.add_argument('--data_file', type=str, help='json file with data')
  args = parser.parse_args()

  print('done')
