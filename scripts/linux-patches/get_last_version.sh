#!/bin/bash
#

testing_filetype=$(ls -1 *_linux-*|sort|tail -1)
testing_file=${testing_filetype%.*}
testing_kernel_full_version=${testing_file#*-}
testing_gentoo_patch=${testing_file%_*}
echo "CKF=$testing_kernel_full_version"
testing_kernel_version=${testing_kernel_full_version%.*}
testing_kernel_patch=${testing_kernel_full_version##*.}
echo "CGP=$testing_gentoo_patch"
echo "CKP=$testing_kernel_patch"

echo $testing_kernel_version
echo $testing_kernel_patch

new_gentoo_patch=$(( $testing_gentoo_patch+1 ))
new_kernel_patch=$(( $testing_kernel_patch+1 ))
echo "new_file=$new_gentoo_patch $new_kernel_patch"

