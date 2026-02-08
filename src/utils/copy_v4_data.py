import shutil
import os

# Copy v4 data to dashboard
source_dir = r'D:\ICON+\cvo_v4_results\dashboard_data'
dest_dir = r'D:\ICON+\cvo-dashboard\public\data'

# Ensure destination exists
os.makedirs(dest_dir, exist_ok=True)

# Copy all v4 JSON files
if os.path.exists(source_dir):
    for filename in os.listdir(source_dir):
        if filename.endswith('.json'):
            src = os.path.join(source_dir, filename)
            dst = os.path.join(dest_dir, filename)
            shutil.copy2(src, dst)
            print(f'Copied v4: {filename}')
    print('\nCVO v4 data copied successfully!')
else:
    print(f'Source dir not found: {source_dir}')
