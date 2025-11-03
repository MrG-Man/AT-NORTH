#!/usr/bin/env python3
"""
Diagnostic script to understand why tracker is not displaying selections.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import get_current_prediction_week, SELECTORS
from data_manager import data_manager

def main():
    print("=" * 80)
    print("BTTS TRACKER DIAGNOSTIC - SELECTION DISPLAY ISSUE")
    print("=" * 80)
    
    # 1. Check current date and calculated week
    now = datetime.now()
    current_day = now.weekday()
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    print(f"\n1. DATE CALCULATION:")
    print(f"   Current Date: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Current Day: {day_names[current_day]} (weekday={current_day})")
    
    calculated_week = get_current_prediction_week()
    print(f"   Calculated Week (next Saturday): {calculated_week}")
    
    # 2. Check what selections files exist
    print(f"\n2. SELECTIONS FILES:")
    selections_path = data_manager.selections_path
    print(f"   Selections directory: {selections_path}")
    
    if os.path.exists(selections_path):
        files = sorted(os.listdir(selections_path))
        print(f"   Found {len(files)} file(s):")
        for file in files:
            filepath = os.path.join(selections_path, file)
            size = os.path.getsize(filepath)
            modified = datetime.fromtimestamp(os.path.getmtime(filepath))
            print(f"     - {file} ({size} bytes, modified {modified.strftime('%Y-%m-%d %H:%M')})")
    else:
        print(f"   ERROR: Selections directory does not exist!")
    
    # 3. Try to load selections for calculated week
    print(f"\n3. LOADING SELECTIONS FOR {calculated_week}:")
    selections = data_manager.load_weekly_selections(calculated_week)
    
    if selections:
        print(f"   ✓ Successfully loaded selections")
        print(f"   Number of selections: {len(selections)}")
        print(f"   Selectors with assignments:")
        for selector, match_data in selections.items():
            home = match_data.get('home_team', 'Unknown')
            away = match_data.get('away_team', 'Unknown')
            print(f"     - {selector}: {home} vs {away}")
    else:
        print(f"   ✗ No selections found for {calculated_week}")
        print(f"   File would be: week_{calculated_week}.json")
    
    # 4. Check all available selections files
    print(f"\n4. CHECKING ALL AVAILABLE SELECTIONS:")
    if os.path.exists(selections_path):
        for file in sorted(os.listdir(selections_path)):
            if file.startswith('week_') and file.endswith('.json'):
                date = file.replace('week_', '').replace('.json', '')
                selections_for_date = data_manager.load_weekly_selections(date)
                if selections_for_date:
                    print(f"   {date}: {len(selections_for_date)} selection(s)")
                    for selector in selections_for_date.keys():
                        print(f"     - {selector}")
    
    # 5. Simulate tracker data endpoint
    print(f"\n5. SIMULATING /api/tracker-data ENDPOINT:")
    print(f"   Expected selectors: {SELECTORS}")
    print(f"   Total selectors: {len(SELECTORS)}")
    
    tracker_matches = []
    selected_count = 0
    placeholder_count = 0
    
    for selector in SELECTORS:
        if selections and selector in selections:
            match_data = selections[selector]
            print(f"   ✓ {selector}: ASSIGNED - {match_data.get('home_team')} vs {match_data.get('away_team')}")
            selected_count += 1
        else:
            print(f"   ✗ {selector}: PLACEHOLDER - No match assigned")
            placeholder_count += 1
    
    print(f"\n   Summary:")
    print(f"   - Selected: {selected_count}/{len(SELECTORS)}")
    print(f"   - Placeholders: {placeholder_count}/{len(SELECTORS)}")
    print(f"   - Completion: {int((selected_count / len(SELECTORS)) * 100)}%")
    
    # 6. Diagnosis
    print(f"\n6. DIAGNOSIS:")
    if selections and len(selections) > 0:
        if len(selections) == len(SELECTORS):
            print(f"   ✓ All selectors have assignments")
        else:
            print(f"   ⚠ Only {len(selections)}/{len(SELECTORS)} selectors have assignments")
            print(f"   Missing assignments for: {', '.join([s for s in SELECTORS if s not in selections])}")
    else:
        print(f"   ✗ NO SELECTIONS FOUND for week {calculated_week}")
        print(f"   ")
        print(f"   Possible causes:")
        print(f"   1. Selections were saved for a different week")
        print(f"   2. Selections file doesn't exist yet")
        print(f"   3. File path or permissions issue")
        print(f"   ")
        print(f"   Expected file: {os.path.join(selections_path, f'week_{calculated_week}.json')}")
        expected_file = os.path.join(selections_path, f'week_{calculated_week}.json')
        if os.path.exists(expected_file):
            print(f"   File EXISTS but failed to load - possible corruption")
        else:
            print(f"   File DOES NOT EXIST")
    
    print(f"\n" + "=" * 80)

if __name__ == "__main__":
    main()