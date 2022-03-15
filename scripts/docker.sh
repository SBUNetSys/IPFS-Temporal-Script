# $1 = dir_name $2 = file_name
DIR_NAME=$1
FILE_NAME=$2
TASK_NAME=$3
HOST_IP=$4
HOST_PORT=$5
echo "DIR_NAME = ${DIR_NAME},FILE_NAME = ${FILE_NAME}, TASK_NAME = ${TASK_NAME}, HOST_IP = ${HOST_IP}, HOST_PORT = ${HOST_PORT}"
mkdir -p result
docker build -t ipfs-temporal-script ./docker/
sudo sysctl -w net.core.rmem_max=2500000
docker run -d --name ${DIR_NAME}-ipfs-temporal\
       -v $(pwd)/result:/result \
       -v $(pwd)/scripts:/scripts \
       -v $(pwd)/data:/data \
       -e DIR_NAME=$DIR_NAME \
       -e FILE_NAME=$FILE_NAME \
       -e TASK_NAME=$TASK_NAME \
       -e HOST_IP=${HOST_IP} \
       -e HOST_PORT=${HOST_PORT} \
       --cap-add=NET_ADMIN \
       ipfs-temporal-script

