# -*- mode: ruby -*-
# vi: set ft=ruby :

# Function to dynamically get the host IP
# Used for setting the `smb_host` in config.vm.synced_folder
def get_host_ip
    # This example uses `ifconfig` and `grep` to find inet interface and host IP address
    host_ip = `ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}'`.strip
    return host_ip
end

# Vagrant::Config.run do |config|
Vagrant.configure("2") do |config|

    # Define host machine operating system variables
    # source: https://stackoverflow.com/questions/26811089/vagrant-how-to-have-host-platform-specific-provisioning-steps/26889312#26889312
    module OS
        def OS.windows?
            (/cygwin|mswin|mingw|bccwin|wince|emx/ =~ RUBY_PLATFORM) != nil
        end
        def OS.mac?
            (/darwin/ =~ RUBY_PLATFORM) != nil
        end
        def OS.unix?
            !OS.windows?
        end
        def OS.linux?
            OS.unix? and not OS.mac?
        end

    end

    if OS.mac?

        puts "- Mac OS detected"
        puts "  -- Provider: QEMU"
        
        config.vm.box = "perk/ubuntu-2204-arm64"

        config.vm.provider "qemu" do |qe|
            qe.memory = "4096" # 4GB
        end

        config.vm.network :forwarded_port, guest: 80, host: 8080  # nginx
        config.vm.network "forwarded_port", guest: 8000, host: 8000
        config.vm.network "forwarded_port", guest: 8001, host: 8001
        # config.vm.network "forwarded_port", guest: 8080, host: 8080
        # config.vm.network "forwarded_port", guest: 5432, host: 65432
        # config.vm.network "forwarded_port", id: "ssh", guest: 22, host: 1243

        config.ssh.insert_key = true
        config.ssh.forward_agent = true

        # Automatically detect the SMB host IP
        smb_host_ip = get_host_ip
        
        config.vm.synced_folder "./", "/usr/local/apps/madrona_portal",
        type: "smb",
        smb_host: smb_host_ip,
        mount_options: ["sec=ntlmssp", "nounix", "noperm", "vers=3.0"]

        config.vm.synced_folder "../madrona-apps", "/usr/local/apps/madrona_portal/apps",
        type: "smb",
        smb_host: smb_host_ip,
        mount_options: ["sec=ntlmssp", "nounix", "noperm", "vers=3.0"]

    elsif OS.linux?

        # Base box to build off, and download URL for when it doesn't exist on the user's system already
        # config.vm.box = "marco-base-v0.4"
        # config.vm.box_url = "http://portal.midatlanticocean.org/static/vagrant_boxes/p97-base-v0.4.box"
        #config.vm.box = "ubuntu/bionic64"
        # config.vm.box = "ubuntu/jammy64"
        config.vm.box = "bento/ubuntu-24.04"

        #Enforce provisioning of 5GB of RAM - required for running MARCO properly
        #If you don't have 5 GB, you can drop the memory value, or comment everything out completely.
        # config.vm.customize [
        #   "modifyvm", :id,
        #   "--memory", "5120"
        # ]
        config.vm.provider :virtualbox do |vb|
            vb.customize ["modifyvm", :id, "--memory", 4096]
        end

        if Vagrant.has_plugin?("vagrant-vbguest")
            config.vbguest.auto_update = false
        end

        # Forward a port from the guest to the host, which allows for outside
        # computers to access the VM, whereas host only networking does not.
        # config.vm.forward_port 8000, 8000
        # config.vm.forward_port 5432, 65432
        config.vm.network :forwarded_port, guest: 80, host: 8080  # nginx
        config.vm.network :forwarded_port, guest: 8000, host: 8000  # django dev server
        config.vm.network :forwarded_port, guest: 8001, host: 8001  # django dev server
        config.vm.network :forwarded_port, guest: 8002, host: 8002  # django dev server
        config.vm.network :forwarded_port, guest: 8003, host: 8003  # django dev server
        config.vm.network :forwarded_port, guest: 3000, host: 8300  # django dev server
        # config.vm.network :forwarded_port, guest: 5432, host: 65432  # postgresql

        # config.ssh.forward_agent = true

        # Share an additional folder to the guest VM. The first argument is
        # an identifier, the second is the path on the guest to mount the
        # folder, and the third is the path on the host to the actual folder.
        # config.vm.share_folder "project", "/home/vagrant/marco_portal2", "."
        config.vm.synced_folder "./", "/usr/local/apps/madrona_portal"
        config.vm.synced_folder "../madrona-apps/", "/usr/local/apps/madrona_portal/apps"

        # Enable provisioning with a shell script.
        # config.vm.provision :shell, :path => "scripts/vagrant_provision.sh", :args => "'marco_portal2' 'marco' 'marco_portal'", :privileged => false

        # If a 'Vagrantfile.local' file exists, import any configuration settings
        # defined there into here. Vagrantfile.local is ignored in version control,
        # so this can be used to add configuration specific to this computer.

        # if File.exist? "Vagrantfile.local"
        #     instance_eval File.read("Vagrantfile.local"), "Vagrantfile.local"
        # end

    elsif OS.windows?

        puts "Windows OS detected"
        puts "Applying default Windows configuration"

        # Default synced folder setup for Windows
        smb_host_ip = "192.168.1.1" # Fallback IP for Windows

        config.vm.synced_folder "./", "/usr/local/apps/madrona_portal",
        type: "smb",
        smb_host: smb_host_ip,
        mount_options: ["sec=ntlmssp", "nounix", "noperm", "vers=3.0"]

        config.vm.synced_folder "../madrona-apps", "/usr/local/apps/madrona_portal/apps",
        type: "smb",
        smb_host: smb_host_ip,
        mount_options: ["sec=ntlmssp", "nounix", "noperm", "vers=3.0"]

        config.ssh.insert_key = true
        config.ssh.forward_agent = true
    else
      
        puts "Unknown OS detected"
        puts "Please add configuration to VagrantFile"

    end

end
