#!/bin/bash

cp com.nateswanberg.gmail-counter.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.nateswanberg.gmail-counter.plist

