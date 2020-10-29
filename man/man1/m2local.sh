LOCAL_MAN1_DIR=/usr/local/man/man1
sudo mkdir -p ${LOCAL_MAN1_DIR}

for file in *.1
do
	sudo cp $file ${LOCAL_MAN1_DIR}
done
