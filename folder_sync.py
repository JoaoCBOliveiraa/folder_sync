import argparse
import os
import shutil
import logging
import filecmp

def path_select():
  # this function creates an object with all the parameters needed for the script
  parser = argparse.ArgumentParser(prog='folder_sync', description='This script synchronizes 2 folders so that the changes in the original folder get replicated in a second folder')
  parser.add_argument('source', type='str', help='File path for the source folder')
  parser.add_argument('replica', type='str', help='File path for the replica folder')
  parser.add_argument('logs', type='str', help='File path for the logging folder')
  parser.add_argument('interval', type='int', help='loop interval for script in seconds')
  return parser.parse_args

def logging(logs):
  # This function logs changes to a new or existing log file
  logger = logging.getLogger()
  logger.setLevel(logging.INFO) # Logging config

  # Handler creation
  f_handler = logging.FileHandler('logs') # Write to file
  f_handler.setLevel(logging.INFO)

  c_handler = logging.StreamHandler() # Send to console
  c_handler.setLevel(logging.INFO)

  # Format setup
  c_format = logging.Formater('%(levelname)s : %(message)s')
  f_format = logging.Formater('%(asctime)s - %(levelname)s : %(message)s')

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
  logger.info(f'Files/directories found in source folder: {os.listdir(source)} \nFiles/directories found in replica folder: {os.listdir(replica)}')
  report = compare_obj.report()
  logger.info(f'This is the result of the file comparison: \n\n{report}')

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
     shutil.rmtree(item_replica)
     logger.info(f'Directory and content successfully removed from {replica}')

  else:
     os.remove(item_replica)
     logger.info(f'File successfully removed from {replica}')

     