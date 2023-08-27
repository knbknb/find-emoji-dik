#!/usr/bin/perl
# transform text to lowercase, leave CHAPTER lines as-is
# one-off task
use strict;
use warnings;

open(my $fh, '<', 'data/moby-dick.txt') or die "Can't open file: $!";
while (my $line = <$fh>) {
    if ($line =~ /^CHAPTER/) {
        print $line;
    } else {
        print lc($line);
    }
}
close($fh);