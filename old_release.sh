#!/bin/sh

echo  'Clearing release-folder'
echo
rm -r ~/environment/release-folder/*

echo  'Copying app to release-folder'
echo
cp -r ~/environment/m1/app/* ~/environment/release-folder/

ENV_PATH=~/environment/m1/app/core-service/core/.env
echo  'ENV file path:' $ENV_PATH
echo

VERSION=$(cat $ENV_PATH | grep -o -P '(?<=VERSION = ).*')
echo  'Release VERSION:' $VERSION
echo


# Push to AWS CodeCommit

cd ~/environment/release-folder/

git add .
git commit -m "M1 Core $VERSION"
git push --set-upstream origin main


# Push Version Tag to GitHub

cd ~/environment/m1/

git tag $VERSION
git push origin tag $VERSION