#!/usr/bin/env bash

perl repos/genpatches-misc/web/email-announcement.pl 6.1-15 genpatches /tmp/ https://anongit.gentoo.org/git/proj/linux-patches.git Arisu Tachibana | ssh dev.gentoo.org /usr/sbin/sendmail -F \"Arisu Tachibana\" -f \"alicef@gentoo.org\" gentoo-kernel@lists.gentoo.org

