## Central Server for temporal script
This script will start a central sever to periodically download recent seen files on `ipfs-search`.
Then the script will filter all `fresh` files (files that first seen on the day the script is running) and collect these `cid`.
These `cid` will be sent to our preconfigured docker conatinaters to collect data.

