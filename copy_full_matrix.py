import shutil
import os

# Copy full matrix image to dashboard
shutil.copy2(
    r'D:\ICON+\cvo_dual_matrix_full.png',
    r'D:\ICON+\cvo-dashboard\public\images\cvo_dual_matrix.png'
)

print("[OK] Full matrix image (all 57,856 customers) copied to dashboard!")
