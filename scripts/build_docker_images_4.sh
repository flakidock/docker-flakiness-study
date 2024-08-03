#set -x

path_prefix='/home/contextml/temporal-study-docker/temporal-study' # your working directory

run_docker_build() {
  screen_name=$1
  general_conf_file=$2
  config_file=$3

  screen -dm -S $screen_name python $path_prefix/docker-utils/docker_build.py -g $general_conf_file -c $config_file &
}

# run on a single process
run_docker_build build15-17 $path_prefix/configs/docker_build/general-build.yaml $path_prefix/configs/docker_build/single-process-vm4.yaml