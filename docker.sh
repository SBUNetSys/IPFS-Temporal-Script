mkdir -p result
docker build -t ipfs-temporal-script .
sudo sysctl -w net.core.rmem_max=2500000
docker run -d --name $(date +%F-%H)-ipfs-temporal\
       -v $(pwd)/result:/result \
       -v $(pwd)/scripts:/scripts \
       -v $(pwd)/data:/data \
       --cap-add=NET_ADMIN \
       ipfs-temporal-script

