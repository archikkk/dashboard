[app]
# (str) Title of your application
title = MovieSearch

# (str) Package name
package.name = moviesearch

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .
source.include_exts = py,kv

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
requirements = python3,kivy,requests,beautifulsoup4,lxml,cloudscraper

# (str) Entry point for the application
entrypoint = main.py