#!/bin/sh

cd `dirname $0`

java -mx1000m \
     -classpath stanford-ner.jar:./ \
     edu.stanford.nlp.ie.NERServer \
     -loadClassifier adept.ser.gz \
     -port 9191 \
     -outputFormat inlineXML

