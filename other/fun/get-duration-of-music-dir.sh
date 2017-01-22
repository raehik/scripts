ts=0 ; for f in *.ogg(N) *.mp3(N) ; do ; ts=$((ts + $(soxi -D $f))) ; soxi -d $f ; done ; echo ---$n${ts}s ; printf %02dh:%02dm:%02dsn $(($ts/3600)) $(($ts%3600/60)) $(($ts%60))
