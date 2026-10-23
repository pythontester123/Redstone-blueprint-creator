#!/bin/sh
# Fabrique RedstonePlanner.exe (Windows 64 bits) à partir de redstone-planner.html
set -e
cd "$(dirname "$0")"
cp ../redstone-planner.html .
[ -f go.mod ] || go mod init redstoneplanner >/dev/null 2>&1
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -ldflags "-s -w -H windowsgui" -o RedstonePlanner.exe .
rm redstone-planner.html
echo "RedstonePlanner.exe : $(du -h RedstonePlanner.exe | cut -f1)"
