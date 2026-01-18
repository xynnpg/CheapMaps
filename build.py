import PyInstaller.__main__
import os

# Define paths
# Note: Use separators that work on Windows; usually paths are fine but let's be safe.
# We are adding src/map_app.html to src/ inside the bundle
# And src/qwebchannel.js to src/ inside the bundle
# Format for add-data is "source;destination" on Windows

print("Starting Build Process...")

PyInstaller.__main__.run([
    'src/main.py',
    '--name=CheapMaps',
    '--noconsole',
    '--onefile',
    '--clean',
    '--hidden-import=PyQt5',
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtGui',
    '--hidden-import=PyQt5.QtWidgets',
    '--hidden-import=PyQt5.QtWebEngineWidgets',
    '--hidden-import=PyQt5.QtWebChannel',
    '--hidden-import=PyQt5.QtNetwork',
    # Add map_app.html to src/ folder in bundle
    '--add-data=src/map_app.html;src',
    # Add qwebchannel.js to src/ folder in bundle
    '--add-data=src/qwebchannel.js;src',
    # We might need to ensure src/ui and src/utils are dragged in if imports fail, 
    # but usually PyInstaller finds imports.
    # However, sometimes keeping the structure is needed if we do dynamic loading.
])

print("Build Complete! Check dist/CheapMaps.exe")
