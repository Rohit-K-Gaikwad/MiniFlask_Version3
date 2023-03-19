## To find a running process by its port number

Step 1: Run flask application on port 5000 (in terminal 1)

Step 2: find process id that is attached to port `5000` (in terminal 2)
```bash
lsof -i -P -n | grep 5000
netstat -tulpn | grep 5000
```

Step 3: open another terminal and `kill 5000` (terminal 2)