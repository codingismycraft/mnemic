$script = <<SCRIPT
sudo apt update
sudo apt install python3-pip -y
sudo pip3 install nose
sudo pip3 install jupyter
sudo pip3 install numpy
sudo pip3 install scipy
sudo pip3 install matplotlib 
sudo pip3 install ipython 
sudo pip3 install pandas
sudo apt-get install zip unzip -y
sudo pip3 install sqlalchemy==1.3.23
sudo apt-get install dos2unix
sudo apt-get install libpq-dev python-dev -y
sudo pip3 install psycopg2
sudo pip3 install asyncpg
sudo apt install python3-sklearn -y
sudo pip3 install seaborn
sudo pip3 install --upgrade tensorflow
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-20.04"

  # require plugin https://github.com/leighmcculloch/vagrant-docker-compose
  config.vagrant.plugins = "vagrant-docker-compose"

  # install docker and docker-compose
  config.vm.provision :docker
  config.vm.provision :docker_compose

  config.vm.provision "shell", inline: $script
  config.vm.provision "shell", path: "install-psql.sh"
  for i in 8888..8900
    config.vm.network :forwarded_port, guest: i, host: i-2000
  end
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2000"
    vb.name = "mnemonic"
  end
end
