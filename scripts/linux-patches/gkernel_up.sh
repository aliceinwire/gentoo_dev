#!/bin/bash
#
# This file is used as main for automating gentoo_sources

SCRIPT_DIR=$(cd "$(dirname "$0")"|| exit;pwd)
ROOT_DIR=$(cd "$SCRIPT_DIR/../../"|| exit;pwd)
LINUX_PATCHES_DIR=$(cd "$ROOT_DIR/linux-patches/"||exit;pwd)


#echo "SCRIPT_DIR=$SCRIPT_DIR"
#echo "ROOT_DIR=$ROOT_DIR"
#echo "LINUX_PATCHES_DIR=$LINUX_PATCHES_DIR"

# get arguments
# kernel_version=$1

test_this() {
  #echo "test_this"
  branch_version=$(git branch --show)
}

# get kernel major minor and patch version
get_kernel_versions() {
  kernel_version=${testing_kernel_full_version}
  _kernel_major_1=${kernel_version%.*}
  kernel_major=${_kernel_major_1%.*}
  _kernel_minor_1=${kernel_version#*.}
  kernel_minor=${_kernel_minor_1%.*}
  kernel_patch=${_kernel_minor_1#*.}
  kernel_patch=$((kernel_patch+1))
  kernel_patch_old=$((kernel_patch-1))
  kernel_version="${kernel_major}.${kernel_minor}.${kernel_patch}"
}

print_versions() {
  echo "$kernel_version"
  echo "$kernel_major"
  echo "$kernel_minor"
  echo "$kernel_patch"
  echo "$kernel_patch_old"
}

is_root() {
  cd "$ROOT_DIR" || exit
}

is_linux_patches() {
  cd "$LINUX_PATCHES_DIR" || exit
}

update_repo() {
  is_linux_patches
  git pull
}
download_patch() {
  wget https://cdn.kernel.org/pub/linux/kernel/v\
"$kernel_major".x/patch-\
"$kernel_major".\
"$kernel_minor".\
"$kernel_patch_old"\
.xz || exit 1
  patch_file="patch-$kernel_major.$kernel_minor.$kernel_patch_old.xz"
  unxz "$patch_file"
  patch_file=${patch_file%.*}
  mv "$patch_file" "${new_gentoo_patch_file}"
}

download_incr_patch() {
  wget https://cdn.kernel.org/pub/linux/kernel/v\
"$kernel_major".x/incr/patch-\
"$kernel_major".\
"$kernel_minor".\
"$kernel_patch_old"-\
"$kernel_patch".xz || exit 1
  patch_file="patch-$kernel_major.$kernel_minor.$kernel_patch_old-$kernel_patch.xz"
  unxz "$patch_file"
  patch_file=${patch_file%.*}
  mv "$patch_file" "${new_gentoo_patch_file}"
}

get_versions() {
  is_linux_patches
  # need for making first kernel branch version
  ls -1 *_linux-* || test_this
  echo $branch_version
  if [ -n "$branch_version" ]; then
    branch_version="${branch_version}.1"
    testing_kernel_full_version=$branch_version
    new_gentoo_patch_file="1000_linux-${branch_version}.patch"
    #echo "$branch_version"
    get_kernel_versions
    #print_versions
    download_patch
  else
    testing_filetype=$(ls -1 *_linux-*|sort|tail -1)
    testing_file=${testing_filetype%.*}
    testing_kernel_full_version=${testing_file#*-}
    testing_gentoo_patch=${testing_file%_*}
    testing_kernel_version=${testing_kernel_full_version%.*}
    testing_kernel_patch=${testing_kernel_full_version##*.}
    #echo "CKF=$testing_kernel_full_version"
    #echo "CGP=$testing_gentoo_patch"
    #echo "CKP=$testing_kernel_patch"
    new_gentoo_patch=$(( testing_gentoo_patch+1 ))
    new_kernel_patch=$(( testing_kernel_patch+1 ))
    new_gentoo_patch_file="${new_gentoo_patch}_linux-${testing_kernel_version}.${new_kernel_patch}.patch"
    #echo "new_file=${new_gentoo_patch_file}"
    get_kernel_versions
    download_incr_patch
  fi
}

update_kernel() {
  is_linux_patches
  git add .
  GIT_COMMITTER_EMAIL=alicef@gentoo.org git commit \
    --author 'Arisu Tachibana <alicef@gentoo.org>' \
    -m "Linux patch $kernel_version" \
    -s \
    -S
}

# Main
#update_repo
get_versions
#echo "$ROOT_DIR"
#print_versions
test_this
echo "branch version: $branch_version"
python "$SCRIPT_DIR"/get_file_list.py
update_kernel
