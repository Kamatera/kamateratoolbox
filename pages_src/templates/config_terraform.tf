terraform {
  required_providers {
    kamatera = {
      source = "Kamatera/kamatera"
    }
  }
}

provider "kamatera" {
}

resource "kamatera_server" "my_server" {
  name = "my_server"
  datacenter_id = "${c.datacenter}"
  image_id = "${c.imageId}"
  cpu_type = "${c.cpuType}"
  cpu_cores = ${c.cpuCores}
  ram_mb = ${c.ram}
  disk_sizes_gb = [${c.diskSizes.join(",")}]
  billing_cycle = "${c.billing}"${c.billing === "monthly" ? "\n  monthly_traffic_package = \""+c.netpack+"\"" : ""}
}
