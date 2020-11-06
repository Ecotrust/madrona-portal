# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrant::Config.run do |config|
Vagrant.configure("2") do |config|
    # Base box to build off, and download URL for when it doesn't exist on the user's system already
    # config.vm.box = "marco-base-v0.4"
    # config.vm.box_url = "http://portal.midatlanticocean.org/static/vagrant_boxes/p97-base-v0.4.box"
    config.vm.box = "ubuntu/focal64"

    #Enforce provisioning of 5GB of RAM - required for running MARCO properly
    #If you don't have 5 GB, you can drop the memory value, or comment everything out completely.
    # config.vm.customize [
    #   "modifyvm", :id,
    #   "--memory", "5120"
    # ]
    config.vm.provider :virtualbox do |vb|
        vb.customize ["modifyvm", :id, "--memory", 2048]
    end

    # Forward a port from the guest to the host, which allows for outside
    # computers to access the VM, whereas host only networking does not.
    # config.vm.forward_port 8000, 8000
    # config.vm.forward_port 5432, 65432
    config.vm.network :forwarded_port, guest: 80, host: 8080  # nginx
    config.vm.network :forwarded_port, guest: 8000, host: 8000  # django dev server
    config.vm.network :forwarded_port, guest: 5432, host: 65432  # postgresql

    # config.ssh.forward_agent = true

    # Share an additional folder to the guest VM. The first argument is
    # an identifier, the second is the path on the guest to mount the
    # folder, and the third is the path on the host to the actual folder.
    # config.vm.share_folder "project", "/home/vagrant/marco_portal2", "."
    config.vm.synced_folder "./", "/usr/local/apps/ocean_portal"
    # config.vm.synced_folder "../mida-portal/", "/usr/local/apps/mida-portal"

    # Enable provisioning with a shell script.
    # config.vm.provision :shell, :path => "scripts/vagrant_provision.sh", :args => "'marco_portal2' 'marco' 'marco_portal'", :privileged => false

    # If a 'Vagrantfile.local' file exists, import any configuration settings
    # defined there into here. Vagrantfile.local is ignored in version control,
    # so this can be used to add configuration specific to this computer.

    # if File.exist? "Vagrantfile.local"
    #     instance_eval File.read("Vagrantfile.local"), "Vagrantfile.local"
    # end

end
