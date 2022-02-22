cd /result
mkdir -p $(date +%F)
# start record hop information
cd $(date +%F)
echo $(pwd)
~/ipfs_bin/ipfs repo gc
~/ipfs_bin/ipfs daemon --enable-gc > $(date +%F)_daemon.txt 2>&1 &
sleep 600
~/ipfs_bin/ipfs log level dht warn
~/ipfs_bin/ipfs log level bitswap warn
python /scripts/record.py
killall ipfs
