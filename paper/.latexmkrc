# Prefer the unmodified ALT class and its bundled JMLR dependencies.
$ENV{'TEXINPUTS'} = './vendor/alt2027//:' . ($ENV{'TEXINPUTS'} // '');
