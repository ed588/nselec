#!/bin/bash

usage ()
{
  echo "Usage: $0 <projname> [ -v ] [ -d ] [ -b ]" 1>&2
  echo "  -v : virtualenv override   - disable checking for virtualenv" 1>&2
  echo "  -d : dry-run               - don't actually do anything" 1>&2
  echo "  -b : branch                - don't check if we're on the master branch" 1>&2
  exit 1;
}

[[ $# -eq 0 ]] && usage 

proj=$1
shift

dr=
forcevenv=
nocheckbranch=

while getopts ":vdb" i; do
  case $i in
    v) forcevenv=y ;;
    d) dr=echo ;;
    b) nocheckbranch=y ;;
    *) usage ;;
  esac
done

currentbranch=$(git symbolic-ref --short HEAD)
if [[ "$currentbranch" != "master" && "$nocheckbranch" != "y" ]]; then
  echo "Fatal: you do not appear to be on master" 1>&2
  echo "(Use -b to override)" 1>&2
  exit 1
fi

if [[ -z ${VIRTUAL_ENV+x} && "$forcevenv" != y ]]; then
  echo "Fatal: you do not appear to be in a virtualenv." 1>&2
  echo "(Use -v to override)" 1>&2
  exit 1
fi

ver=$(python -c "from $proj import __version__ as v;print(v)")
if [[ $? -ne 0 ]]; then
  echo "Python error - aborting" 1>&2
  exit 1
fi
read -p "Building $proj v$ver - continue? [y/n] " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
  $dr git tag -s -a "v$ver"
  $dr git push origin "v$ver"
  $dr python setup.py sdist bdist_wheel
  $dr twine upload dist/${proj}-${ver}-*.whl dist/${proj}-${ver}.*
  echo "Done!"
else
  echo "Ok, have a nice day"
fi
exit 0

