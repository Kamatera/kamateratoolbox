packer {
  required_plugins {
    kamatera = {
      version = ">= 0.5.0"
      source  = "github.com/kamatera/kamatera"
    }
  }
}

source "kamatera" "my_source" {
  datacenter = "${c.datacenter}"
  ssh_username = "root"
  cpu = "${c.cpuCores}${c.cpuType}"
  ram = "${c.ram}"
  image = "${c.datacenter}:${c.imageId}"
  disk = "${c.diskSizes[0]}"
}

build {
  sources = [
    "source.kamatera.my_source"
  ]
}
