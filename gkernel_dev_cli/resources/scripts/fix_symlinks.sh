#!/usr/bin/env bash

#sudo unlink /usr/local/bin/email-announcement.pl
#sudo unlink /usr/local/bin/get-patch
#sudo unlink /usr/local/bin/gpcreatebranch
#sudo unlink /usr/local/bin/gpdoemail
#sudo unlink /usr/local/bin/gpdorelease
#sudo unlink /usr/local/bin/gpdoweb
#sudo unlink /usr/local/bin/gpmultipatch
#sudo unlink /usr/local/bin/gpmvhistorical
#sudo unlink /usr/local/bin/gppatch

sudo ln -s /opt/gentoo_dev/repos/genpatches-misc/web/email-announcement.pl /usr/local/bin/email-announcement.pl 
sudo ln -s /opt/gentoo_dev/repos/genpatches-misc/scripts/get-patch /usr/local/bin/get-patch 
sudo ln -s /opt/gentoo_dev/repos/genpatches-misc/scripts/gpcreatebranch /usr/local/bin/gpcreatebranch 
sudo ln -s /opt/gentoo_dev/repos/genpatches-misc/scripts/gpdoemail /usr/local/bin/gpdoemail 
sudo ln -s /opt/gentoo_dev/repos/genpatches-misc/scripts/gpdorelease /usr/local/bin/gpdorelease 
sudo ln -s /opt/gentoo_dev/repos/genpatches-misc/scripts/gpdoweb /usr/local/bin/gpdoweb 
sudo ln -s /opt/gentoo_dev/repos/genpatches-misc/scripts/gpmultipatch /usr/local/bin/gpmultipatch
sudo ln -s /opt/gentoo_dev/repos/genpatches-misc/scripts/gpmvhistorical /usr/local/bin/gpmvhistorical 
sudo ln -s /opt/gentoo_dev/repos/genpatches-misc/scripts/gppatch /usr/local/bin/gppatch 
