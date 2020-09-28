
for file in *.1
do
	manpage=${file%.1*}
	cat ${manpage}".1" | groff -mandoc -Thtml > ${manpage}".html"
done

