# Initialization script for virtual machines

ubuntu:
   - sudo apt-get install git mercurial make cmake

redhat:
   - sudo yum install git mercurial make cmake 
   - sudo yum install redhat-lsb

default:
   - echo "foo"
