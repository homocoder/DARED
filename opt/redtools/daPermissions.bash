#!/bin/bash
dir=$1
if [ -z $1 ]
then
	dir="."
fi

echo "This utility changes all permission recursively in a directory to make it shareable among science users."
echo $dir

chmod -R ug+rw,o+r,o-w $dir
find $dir -type d | xargs chmod ugo+x
chgrp -R $DA_GROUP $dir
