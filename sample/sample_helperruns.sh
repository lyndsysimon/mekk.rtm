#!/bin/sh

rtmtag --add=baduk --add=komputer --add=go --filter='list:"Go - różne" and status:incomplete' --verbose 

rtmmove --list='Rozrywka' --filter='list:"Go - różne" and status:incomplete' --verbose 
