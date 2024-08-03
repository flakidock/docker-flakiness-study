output=$(cat /var/run/yum.pid)

# Check if the output is a number, i.e. the process id
if [[ $output =~ ^[0-9]+$ ]]; then
    # Output is a number, kill the process
    sudo kill -9 $output
fi