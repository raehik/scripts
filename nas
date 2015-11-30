#!/usr/bin/env bash
#
# Short description of the program/script's operation/function.
#

mount_cmd="sudo mount -t cifs -o uid=$(id -u),gid=$(id -g)"
mount_dir="$HOME/media/nas"
nas_server="NAS"
nas_share="Ben"
nas_user="ben"

mount_nas() {
    nas_ip="$(nmblookup "$nas_server" 2>&1 | tail -n1 | cut -d ' ' -f 1)"
    read -s -p "NAS user password: " nas_password
    echo
    $mount_cmd -o user="$nas_user" -o password="$nas_password" \
        "//$nas_ip/$nas_share" "$mount_dir"
}

umount_nas() {
    sudo umount "$mount_dir"
}

case "$1" in
    mount) mount_nas ;;
    umount) umount_nas ;;
    *) echo "commands are mount and umount" ; exit 1 ;;
esac
