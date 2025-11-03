#!/usr/bin/env python3
"""
Debug script to test DataManager BBC fixtures retrieval
"""
from data_manager import data_manager
import json
import os

print('Testing DataManager.get_bbc_fixtures() for 2025-10-25...')
result = data_manager.get_bbc_fixtures('2025-10-25')
print(f'Result: {result}')
print(f'Result type: {type(result)}')
print(f'Result length: {len(result) if result else 0}')

# Also check what files exist in fixtures directory
fixtures_path = data_manager.fixtures_path
print(f'\nFixtures path: {fixtures_path}')
if os.path.exists(fixtures_path):
    files = os.listdir(fixtures_path)
    print(f'Files in fixtures directory: {files}')
else:
    print('Fixtures directory does not exist')

# Check if directories exist
print(f'\nDataManager paths:')
print(f'Base path: {data_manager.base_path}')
print(f'Selections path: {data_manager.selections_path}')
print(f'Fixtures path: {data_manager.fixtures_path}')
print(f'Backups path: {data_manager.backups_path}')

# Check initialization errors
print(f'\nInitialization errors: {data_manager.initialization_errors}')