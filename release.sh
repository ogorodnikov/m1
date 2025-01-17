#!/bin/sh

echo 'Removing release-folder'

rm -rf ~/environment/release-folder/


echo 'Creating release-folder'

mkdir ~/environment/release-folder/


echo 'Cloning empty Codecommit repository'

cd ~/environment/release-folder/
git clone --no-checkout https://git-codecommit.us-east-1.amazonaws.com/v1/repos/m1-core-codecommit-repository ~/environment/release-folder/


echo 'Copying app to release-folder'

cp -r ~/environment/m1/app/* ~/environment/release-folder/


echo 'Checking Donenv config'

ENV_PATH=~/environment/m1/app/core-service/core/.env
VERSION=$(cat $ENV_PATH | grep -o -P '(?<=VERSION = ).*')
echo 'Donenv file path:' $ENV_PATH
echo 'Release VERSION:' $VERSION


echo 'Pushing to AWS CodeCommit'

cd ~/environment/release-folder/

git checkout -b main
git add .
git commit -m "M1 Core $VERSION"
git push --set-upstream origin main


echo 'Pushing Version tag to Github'

cd ~/environment/m1/

git tag --delete $VERSION
git tag $VERSION

git push --delete origin $VERSION
git push origin tag $VERSION


echo 'Removing release-folder'

rm -rf ~/environment/release-folder/