import shutil
import os

source_dir = r'D:\ICON+\dashboard_data'
dest_dir = r'D:\ICON+\cvo-dashboard\public\data'

# Ensure destination exists
os.makedirs(dest_dir, exist_ok=True)

# Copy all JSON files
for filename in os.listdir(source_dir):
    if filename.endswith('.json'):
        src = os.path.join(source_dir, filename)
        dst = os.path.join(dest_dir, filename)
        shutil.copy2(src, dst)
        print(f'Copied: {filename}')

print('\nAll files copied successfully!')
