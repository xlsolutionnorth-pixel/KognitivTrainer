#!/usr/bin/env python3
"""Kleine Anpassungen am erzeugten Android-Projekt: Vibration erlauben, nur Hochformat."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "android", "app", "src", "main", "AndroidManifest.xml")
m = open(p, encoding="utf-8").read()
if "android.permission.VIBRATE" not in m:
    m = m.replace("</manifest>", '    <uses-permission android:name="android.permission.VIBRATE" />\n</manifest>')
if 'android:screenOrientation' not in m:
    m = m.replace('android:name=".MainActivity"', 'android:name=".MainActivity"\n            android:screenOrientation="portrait"', 1)
open(p, "w", encoding="utf-8").write(m)
print("Manifest angepasst")
