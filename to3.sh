#!/bin/sh
mkdir python3
for i in BeautifulSoupTests.py builder.py element.py dammit.py
do
    cp $i python3/
    2to3-3.0 -x next $i | patch -p0 python3/$i
    cp python3/$i python3/$i.orig
    patch -p0 python3/$i < $i.3.diff
done