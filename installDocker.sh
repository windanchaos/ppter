#/bin/bash
mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.backup
wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
yum clean all
yum makecache
yum remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine
# Install required packages
yum install -y yum-utils device-mapper-persistent-data lvm2
# add stable repository
yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
# install
yum install -y docker-ce docker-ce-cli containerd.io

mkdir -p /etc/docker
tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["http://ef017c13.m.daocloud.io"]
}
#EOF
# 添加 docker 用户组
groupadd docker
# 把需要执行的 docker 用户添加进该组，这里是 user
gpasswd -a $1 docker
# 重启 docker
systemctl start docker