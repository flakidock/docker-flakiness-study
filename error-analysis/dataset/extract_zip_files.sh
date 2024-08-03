# Extracts all .gz files in the current directory but don't delete the .gz files
for f in *.gz; do
    gunzip -c $f > ${f%.gz}
done
