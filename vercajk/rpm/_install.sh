#!/bin/bash


set -e

# mock
cp -f ./mock/del.sh $HOME/Documents/mock_results
cp -f ./mock/del.sh ./mockdel
install -p -m 0755 ./mockdel $HOME/.local/bin
rm ./mockdel
