sudo su -
wget -nv http://public-repo-1.hortonworks.com/ambari/ubuntu14/2.x/updates/2.4.1.0/ambari.list -O /etc/apt/sources.list.d/ambari.list
apt-key adv --recv-keys --keyserver keyserver.ubuntu.com B9733A7A07513CAD
apt-get update
apt-get install ambari-server -y

echo "127.0.0.1 $(hostname)" >> /etc/hosts

ambari-server setup -s
ambari-server start
