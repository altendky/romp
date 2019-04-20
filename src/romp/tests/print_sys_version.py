import os
import sys

print('__file__:', __file__)
print('         ', sys.platform)
print('         ', sys.version)
print('\n'.join(sorted(os.listdir())))
