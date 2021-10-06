gnome-terminal -x sh -c "python3 server.py 0 > A.txt; bash" &
gnome-terminal -x sh -c "python3 server.py 1 > B.txt; bash" &
gnome-terminal -x sh -c "python3 server.py 2 > C.txt; bash"