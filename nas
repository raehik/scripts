#!/usr/bin/env bash
#
# Short description of the program/script's operation/function.
#

mount_cmd="sudo mount -t cifs -o uid=$(id -u),gid=$(id -g)"
mount_dir="$HOME/media/nas"
nas_server="192.168.1.11"
nas_share="Ben"
nas_user="ben"

mount_nas() {
    read -s -p "NAS user password: " nas_password
    echo
    $mount_cmd -o user="$nas_user" -o password="$nas_password" \
        "//$nas_server/$nas_share" "$mount_dir"
}

umount_nas() {
    sudo umount "$mount_dir"
}

case "$1" in
    mount) mount_nas ;;
    umount) umount_nas ;;
    *) echo "commands are mount and umount" ; exit 1 ;;
esac
