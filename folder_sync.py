import argparse
import os
import shutil
import logging
import filecmp
from time import sleep
from shutil import copy2

def path_select():
  # this function creates an object with all the parameters needed for the script
  parser = argparse.ArgumentParser(prog='folder_sync', description='This script synchronizes 2 folders so that the changes in the original folder get replicated in a second folder')
  parser.add_argument('source', type=str, help='File path for the source folder')
  parser.add_argument('replica', type=str, help='File path for the replica folder')
  parser.add_argument('logs', type=str, help='File path for the logging folder')
  parser.add_argument('interval', type=int, help='loop interval for script in seconds')
  return parser.parse_args()

def log_set(logs_path):
  # This function logs changes to a new or existing log file
  dir_logs = os.path.dirname(logs_path)
  if not os.path.exists(dir_logs):
     os.makedirs(dir_logs)
     logger.info(f'Created a logs directory at {dir_logs}')

  logger = logging.getLogger()
  logger.setLevel(logging.INFO) # Logging config

  # Handler creation
  f_handler = logging.FileHandler(logs_path) # Write to file
  f_handler.setLevel(logging.INFO)

  c_handler = logging.StreamHandler() # Send to console
  c_handler.setLevel(logging.INFO)

  # Format setup
  c_format = logging.Formatter('%(levelname)s : %(message)s')
  f_format = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')

  c_handler.setFormatter(c_format)
  f_handler.setFormatter(f_format)

  # Handler enabling
  logger.addHandler(c_handler)
  logger.addHandler(f_handler)

  return logger

def file_sync(source, replica, logger):
  logger.info(f'Started synchronization from {source} to {replica}')

  if not os.path.exists(source):
    logger.error('Cannot find source folder! Make sure you are providing a correct path to the source file next time.')
    quit()

  if not os.path.exists(replica):
    os.makedirs(replica)
    logger.info('Replica folder was created.')

  compare_obj = filecmp.dircmp(source, replica)
  logger.info('----------------------------------------------')
     
  for _, dir_s, _ in os.walk(source):
     logger.info(f'Directory found in source folder: {dir_s}')

  for _, _, file_s in os.walk(source):
     logger.info(f'File found in source folder: {file_s}')
     
  logger.info('----------------------------------------------')

  for _, dir_r, _ in os.walk(replica):
     logger.info(f'Directory found in replica folder: {dir_r}')

  for _, _, file_r in os.walk(replica):
     logger.info(f'File found in replica folder: {file_r}')
  logger.info('----------------------------------------------')

  # Missing files logic
  for files in compare_obj.left_only:
    item_source = os.path.join(source, files)
    item_replica = os.path.join(replica, files)

    if os.path.isdir(item_source):
        logger.info(f'Copying directory: {item_replica}')
        shutil.copytree(item_source, item_replica)
        logger.info(f'Directory and content successfully copied from {source} to {replica}')

    else:
        logger.info(f'Copying file: {item_replica}')
        shutil.copy2(item_source, item_replica)
        logger.info(f'File successfully copied from {source} to {replica}')

  # Deleting files present in replica and not in source
  for files in compare_obj.right_only:
     item_replica = os.path.join(replica, files)

     if os.path.isdir(item_replica):
        shutil.rmtree(item_replica)
        logger.info(f'Directory and content successfully removed from {replica}')

     else:
        os.remove(item_replica)
        logger.info(f'File successfully removed from {replica}')

  # if common files were found, execute update logic
    
  for files in compare_obj.common_files:
     item_source = os.path.join(source, files)
     item_replica = os.path.join(replica, files)

     if not filecmp.cmp(item_source, item_replica):
        if os.path.isdir(item_source):
           shutil.copytree(item_source, item_replica, copy_function=copy2, dirs_exist_ok=True)
           logger.info(f'Detected a folder with changes in {item_replica} and copied from {item_source}')

        else:
           shutil.copy2(item_source, item_replica)
           logger.info(f'Detected a file with changes in {item_replica} and copied from {item_source}')

filecmp.clear_cache()
        
def sync_loop(source, replica, interval, logger):
   try:
      while True:
         file_sync(source, replica, logger)  # Change: Call file_sync instead of sync_loop
         logger.info(f'Waiting for {interval} seconds before the next sync...')
         print('Press CTRL+C to exit the script')
         sleep(interval)

   except KeyboardInterrupt:
      logger.info('Synchronization stopped by user.')


if __name__ == "__main__":
   args = path_select()
   logger = log_set(args.logs)
   logger.info('Initiating file/folder sync')

   source_folder = args.source
   replica_folder = args.replica
   interval = args.interval

   sync_loop(source_folder, replica_folder, interval, logger)