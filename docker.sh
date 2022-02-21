mkdir -p result
docker build -t dtube-script .
sudo sysctl -w net.core.rmem_max=2500000
docker run -d --name $(date +%F)-dtube\
       -v $(pwd)/result:/result \
       -v $(pwd)/scripts:/scripts \
       -v $(pwd)/data:/data \
       --cap-add=NET_ADMIN \
       dtube-script

