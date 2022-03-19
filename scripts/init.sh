cd /result
#mkdir -p $(date +%F)
mkdir -p $DIR_NAME
# start record hop information
cd $DIR_NAME
echo $(pwd)
~/ipfs_bin/ipfs config show
~/ipfs_bin/ipfs repo gc
#~/ipfs_bin/ipfs daemon --enable-gc > $(date +%F)_daemon.txt 2>&1 &
~/ipfs_bin/ipfs daemon --enable-gc > ${DIR_NAME}_daemon.txt 2>&1 &
sleep 600
~/ipfs_bin/ipfs log level dht warn
~/ipfs_bin/ipfs log level bitswap warn
python /scripts/record.py -d "${DIR_NAME}" -f "${FILE_NAME}" -s "${HOST_IP}" -p "${HOST_PORT}" -t "${TASK_NAME}"
killall ipfs
