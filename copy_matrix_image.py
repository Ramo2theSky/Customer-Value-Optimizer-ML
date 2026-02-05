import shutil
import os

# Create images directory
os.makedirs(r'D:\ICON+\cvo-dashboard\public\images', exist_ok=True)

# Copy matrix image
shutil.copy2(
    r'D:\ICON+\cvo_dual_matrix.png',
    r'D:\ICON+\cvo-dashboard\public\images\cvo_dual_matrix.png'
)

print("[OK] Matrix image copied to dashboard!")
