window.serverconfiggeninit = function (calculator_js_php_url, k8s) {
    var datacenterNames = {
        "AS": "Asia: China, Hong Kong",
        "CA-TR": "North America: Canada, Toronto",
        "EU": "Europe: The Netherlands, Amsterdam",
        "EU-FR": "Europe: Germany, Frankfurt",
        "EU-LO": "Europe: United Kingdom, London",
        "IL-RH": "Middle East: Israel, Rosh Haayin",
        "IL": "Middle East: Israel, Rosh Haayin (2)",
        "IL-HA": "Middle East: Israel, Haifa",
        "IL-PT": "Middle East: Israel, Petach Tikva",
        "IL-TA": "Middle East: Israel, Tel Aviv",
        "US-NY2": "North America: United States, New York, New York",
        "US-SC": "North America: United States, California, Santa Clara",
        "US-TX": "North America: United States, Texas, Dallas"
    }
    var cpuTypeNames = {
        A: "Availability",
        B: "General Purpose",
        D: "Dedicated",
        T: "Burstable"
    };
    if (k8s) {
        window.configTemplates = {"default": "`cluster:\n  name: \"...\"  # required, used as a prefix for all resources\n  datacenter: \"${c.datacenter}\"  # required, will be the same for all nodes in the cluster\n  ssh-key:  # required, fill in the private and public keys for the cluster, will be used for ssh access to all nodes\n    private: |\n      -----BEGIN OPENSSH PRIVATE KEY-----\n      ...\n      -----END OPENSSH PRIVATE KEY-----\n    public: |\n      ssh-...\n  private-network:\n    name: \"lan-...\"  # required, lan network name, must be created in advance with enough ips for all the nodes in the cluster\n  default-node-config:  # default values for all nodes in the cluster\n    # following values were filled in from the selected configurations\n    cpu: \"${c.cpuCores}${c.cpuType}\"\n    ram: \"${c.ram}\"\n    disk: \"${c.diskSizes.join(\",\")}\"\n    billingcycle: \"${c.billing}\"\n    monthlypackage: \"${c.billing === \"monthly\" ? c.netpack : \"\"}\"\n    # dailybackup: \"yes\"\n    # managed: \"yes\"\n\n  # server: \"https://1.2.3.4:9345\"  # optional, in case you want to use a specific server as the main cluster server\n  # token: \"...\" # optional, to use as the cluster join token, if not provided will try to get it from controlplane-1 node\n  # controlplane-server-name: \"..\"  # optional, if you want to specify the primary controlplane node name\n  # allow-high-availability: true  # optional, if you want to enable high availability for the controlplane\n  #                                # requires some work to setup, see https://docs.rke2.io/install/ha for details\n  # default-rke2-server-config:  # optional, rke2 config which will be merged into the rke2 config for all server nodes (controlplane)\n  #                              # see https://docs.rke2.io/reference/server_config for details\n  # default-rke2-agent-config:  # optional, rke2 config which will be merged into the rke2 config for all nodes except the controlplane nodes\n  #                             # see https://docs.rke2.io/reference/linux_agent_config for details\n\n\n# modify the node pools as needed, following are some examples\nnode-pools:\n  # controlplane:  # optional, the controlplane node pool is created anyway with 1 node\n  #   nodes: 1  # only if allow-high-availability is true you can set to 3 / 5 / 7 for HA cluster\n  #   node-config:  # optional, default values for all nodes in this pool\n  #   rke2-config:  # optional, rke2 config which will be merged into the rke2 config for all nodes in this pool\n  workers:\n    nodes: 3\n    node-config:  # optional, default values for all nodes in this pool override the cluster default-node-config\n      cpu: 4B\n      memory: 2048\n    # rke2-config:  # optional, rke2 config which will be merged into the rke2 config for all nodes in this pool\n  worker2:\n    nodes: [5, 6]  # nodes can also be specified like this to keep specific node numbers\n`"};
    } else {
        window.configTemplates = {"default": "`datacenter=${c.datacenter}\nimage=${c.datacenter}:${c.imageId}\ncpu=${c.cpuCores}${c.cpuType}\nramMB=${c.ram}\ndiskSizesGB=${c.diskSizes.join(\",\")}\nbilling=${c.billing}\n${c.billing === \"monthly\" ? (\"trafficPackage=\"+c.netpack) : \"\"}\n`", "cloudcli": "`cloudcli server create \\\\\n  --name SERVER_NAME \\\\\n  --datacenter ${c.datacenter} \\\\\n  --image ${c.datacenter}:${c.imageId} \\\\\n  --cpu ${c.cpuCores}${c.cpuType} \\\\\n  --ram ${c.ram} \\\\\n  ${c.diskSizes.map(d => \"--disk size=\"+d).join(\" \")} \\\\\n  --billingcycle ${c.billing} ${c.billing === \"monthly\" ? (\"\\\\\\n  --monthlypackage \"+c.netpack) : \"\"}\n`", "terraform": "`terraform {\n  required_providers {\n    kamatera = {\n      source = \"Kamatera/kamatera\"\n    }\n  }\n}\n\nprovider \"kamatera\" {\n}\n\nresource \"kamatera_server\" \"my_server\" {\n  name = \"my_server\"\n  datacenter_id = \"${c.datacenter}\"\n  image_id = \"${c.imageId}\"\n  cpu_type = \"${c.cpuType}\"\n  cpu_cores = ${c.cpuCores}\n  ram_mb = ${c.ram}\n  disk_sizes_gb = [${c.diskSizes.join(\",\")}]\n  billing_cycle = \"${c.billing}\"${c.billing === \"monthly\" ? \"\\n  monthly_traffic_package = \\\"\"+c.netpack+\"\\\"\" : \"\"}\n}\n`", "packer": "`packer {\n  required_plugins {\n    kamatera = {\n      version = \">= 0.5.0\"\n      source  = \"github.com/kamatera/kamatera\"\n    }\n  }\n}\n\nsource \"kamatera\" \"my_source\" {\n  datacenter = \"${c.datacenter}\"\n  ssh_username = \"root\"\n  cpu = \"${c.cpuCores}${c.cpuType}\"\n  ram = \"${c.ram}\"\n  image = \"${c.datacenter}:${c.imageId}\"\n  disk = \"${c.diskSizes[0]}\"\n}\n\nbuild {\n  sources = [\n    \"source.kamatera.my_source\"\n  ]\n}\n`"};
    }
    window.datacenters = {};
    window.images = {};
    window.imageCategories = {};
    window.cpuTypes = {};
    window.diskSizesGB = [];
    var getImageDescription = function (image) {
        var description = image.description.trim();
        if (description) {
            description = description.replace(/, /, " (" + image.name + "), ")
            if (description.indexOf(image.name) < 0) {
                description = description.replace(/\.\n/, " (" + image.name + ").\n")
                if (description.indexOf(image.name) < 0) {
                    description = description.replace(/\n\n/, " (" + image.name + ")\n\n")
                    if (description.indexOf(image.name) < 0) {
                        description = description + " (" + image.name + ")";
                    }
                }
            }
        } else {
            description = image.name;
        }
        if (description.startsWith("service_")) description = description.substring(8);
        else if (description.startsWith("apps_")) description = description.substring(5);
        return description.replace(/\n\n/g, " - ").replace(/\n/g, " ");
    }
    var initData = function (d) {
        $.each(d.os.sort(function (a, b) {
            var da = getImageDescription(a).toLowerCase();
            var db = getImageDescription(b).toLowerCase();
            return da < db ? -1 : (da === db ? 0 : 1)
        }), function (i, image) {
            if (!k8s) {
                window.images[image.id] = {
                    description: getImageDescription(image),
                    originalDescriptionHtml: image.description.replace(/\n/g, "<br/>"),
                    imageSizeGB: image.imageSizeGB,
                    minRamMB: image.minRamMB,
                    name: image.name
                };
                if (window.imageCategories[image.category] === undefined) window.imageCategories[image.category] = [];
                window.imageCategories[image.category].push(image.id);
            }
            $.each(image.datacenters, function (i, dc) {
                if (window.datacenters[dc] === undefined) window.datacenters[dc] = {
                    name: datacenterNames[dc] === undefined ? dc : datacenterNames[dc],
                    images: []
                };
                window.datacenters[dc].images.push(image.id);
            });
        });
        $.each(d.cpu[0].options, function (i, cpu) {
            var cpuType = cpu.value.slice(-1);
            var cpuCores = cpu.value.slice(0, -1);
            if (window.cpuTypes[cpuType] === undefined) window.cpuTypes[cpuType] = {
                name: cpuTypeNames[cpuType] === undefined ? cpuType : cpuTypeNames[cpuType],
                cores: []
            };
            window.cpuTypes[cpuType].cores.push(cpuCores);
        })
        $.each(d.diskGB[0].options, function (i, disk) {
            window.diskSizesGB.push(disk.value);
        })
        $.each(d, function (key, value) {
            if (key.slice(0, 7) === "netPck.") {
                var dc = key.slice(7);
                $.each(value[0].options, function (i, netpack) {
                    if (window.datacenters[dc] !== undefined) {
                        if (window.datacenters[dc].netpacks === undefined) window.datacenters[dc].netpacks = {};
                        window.datacenters[dc].netpacks[netpack.value] = netpack.description;
                    }
                })
            }
            if (key.slice(0, 6) === "ramMB.") {
                var cpuType = key.slice(6);
                $.each(value[0].options, function (i, ram) {
                    if (window.cpuTypes[cpuType] !== undefined) {
                        if (window.cpuTypes[cpuType].ramMB === undefined) window.cpuTypes[cpuType].ramMB = [];
                        window.cpuTypes[cpuType].ramMB.push(ram.value);
                    }
                })
            }
        })
    };
    var updateDatacenterUi = function () {
        if (!k8s) updateImagesUi();
        updateNetPacksUi();
    }
    var updateImagesUi = function () {
        var $image = $("#image");
        var lastSelectedImageId = $image.val();
        $image.empty()
        var imageCategory = $("#imagecategory").val();
        var datacenterId = $("#datacenter").val();
        if (!imageCategory) {
            $image.append($("<option>").attr("value", "").text("Choose an image category to see available images"))
        } else if (!datacenterId) {
            $image.append($("<option>").attr("value", "").text("Choose a datacenter to see available images"))
        } else {
            $image.append($("<option>").attr("value", "").text("Choose an image"))
            $.each(imageCategories[imageCategory], function (i, imageId) {
                var description = images[imageId].description.trim().split("\n")[0];
                if (!description) description = images[imageId].name;
                var option = $("<option>").attr("value", imageId).text(description);
                if (datacenters[datacenterId].images.indexOf(imageId) === -1) {
                    option.attr("disabled", "disabled")
                } else if (lastSelectedImageId === imageId) {
                    option.attr("selected", "selected");
                }
                $("#image").append(option)
            })
        }
        updateSelectedImageUi();
    }
    var updateCpuCoresUi = function () {
        var $cpucores = $("#cpucores");
        var lastSelectedCpuCores = $cpucores.val();
        $cpucores.empty()
        var selectedCpuTypeId = $("#cputype").val();
        if (!selectedCpuTypeId) {
            $cpucores.append($("<option>").attr("value", "").text("Choose a CPU type to see available CPU cores"))
        } else {
            $cpucores.append($("<option>").attr("value", "").text("Choose CPU cores"))
            $.each(cpuTypes[selectedCpuTypeId].cores, function (i, cpuCores) {
                var option = $("<option>").attr("value", cpuCores).text("" + cpuCores + " " + cpuTypes[selectedCpuTypeId].name + " CPU cores");
                if (lastSelectedCpuCores === cpuCores) {
                    option.attr("selected", "selected");
                }
                $cpucores.append(option)
            })
        }
    }
    var updateRamUi = function () {
        var $ram = $("#ram");
        var lastSelectedRam = $ram.val();
        $ram.empty()
        var selectedCpuTypeId = $("#cputype").val();
        var selectedImageId = $("#image").val();
        var minRamMB = selectedImageId ? images[selectedImageId].minRamMB : 0;
        if (!selectedCpuTypeId) {
            $ram.append($("<option>").attr("value", "").text("Choose a CPU type to see available RAM options"))
        } else {
            $ram.append($("<option>").attr("value", "").text("Choose RAM option"))
            $.each(cpuTypes[selectedCpuTypeId].ramMB, function (i, ramMB) {
                var option = $("<option>").attr("value", ramMB).text("" + ramMB + " MB");
                if (parseInt(ramMB) < minRamMB) {
                    option.attr("disabled", "disabled")
                } else if (lastSelectedRam === ramMB) {
                    option.attr("selected", "selected");
                }
                $ram.append(option)
            })
        }
    }
    var updateCpuTypeUi = function () {
        updateCpuCoresUi();
        updateRamUi();
    }
    var updateNetPacksUi = function () {
        var $netpack = $("#netpack");
        var lastSelectedNetPack = $netpack.val();
        $netpack.empty()
        var datacenterId = $("#datacenter").val();
        var billing = $("#billing").val();
        if (!datacenterId) {
            $netpack.append($("<option>").attr("value", "").text("Choose a datacenter to see available network traffic packages"))
        } else if (!billing) {
            $netpack.append($("<option>").attr("value", "").text("Choose a billing option to see available network traffic packages"))
        } else if (billing !== "monthly") {
            $netpack.append($("<option>").attr("value", "").text("Network traffic packages are only relevant for monthly billing option"))
        } else {
            $netpack.append($("<option>").attr("value", "").text("Choose a network traffic package"))
            $.each(datacenters[datacenterId].netpacks, function (netpackId, netpackDescription) {
                var option = $("<option>").attr("value", netpackId).text(netpackDescription);
                if (lastSelectedNetPack === netpackId) {
                    option.attr("selected", "selected");
                }
                $netpack.append(option)
            })
        }
    }
    var updateBillingUi = function () {
        updateNetPacksUi()
    }
    var addAdditionalDisk = function () {
        $diskscontainer = $("#diskscontainer");
        var numDisks = $diskscontainer.children().length;
        if (numDisks < 4) {
            var nextDiskNum = numDisks + 1
            var additionalDisk = $("<select>").attr("aria-label", "Disk " + nextDiskNum).attr("id", "disk" + nextDiskNum).addClass("form-select");
            additionalDisk.append($("<option>").attr("value", "").text("Choose additional disk size or keep this option to not add additional disk"));
            $.each(diskSizesGB, function (i, diskSizeGB) {
                additionalDisk.append($("<option>").attr("value", diskSizeGB).text(diskSizeGB + " GB"));
            })
            $diskscontainer.append(additionalDisk)
            $(additionalDisk).change(onAnyChange);
            if (nextDiskNum === 4) {
                $("#additionaldisk").hide();
            }
            updateDisksUi();
        }
    }
    var updateDisksUi = function () {
        var $diskscontainer = $("#diskscontainer");
        var selectedImageId = $("#image").val();
        var imageSizeGB = selectedImageId ? images[selectedImageId].imageSizeGB : 0;
        var $disk = $($diskscontainer.children()[0]);
        var selectedDiskSizeGB = $disk.val();
        if (selectedDiskSizeGB !== "" && parseInt(selectedDiskSizeGB) < imageSizeGB) {
            $disk.val("")
        }
        $.each($disk.children(), function (i, option) {
            if (option.value !== "") {
                if (parseInt(option.value) < imageSizeGB) {
                    $(option).attr("disabled", "disabled")
                } else {
                    $(option).removeAttr("disabled")
                }
            }
        })
    }
    var updateSelectedImageUi = function() {
        var selectedImageId = $("#image").val();
        $("#imageDescription").html(selectedImageId ? images[selectedImageId].originalDescriptionHtml : "")
    }
    var onImageChange = function () {
        updateRamUi()
        updateDisksUi()
        updateSelectedImageUi()
    }
    var allStorageIds = [
        "datacenter", "imagecategory", "image", "cputype", "cpucores", "ram", "disk1",
        "disk2", "disk3", "disk4", "billing", "netpack", "configformat"
    ]
    var setConfigurationError = function(err) {
        $("#configuration").val("")
        if (err) {
            err = "Failed to generate configuration: <b>" + err+"</b>";
        }
        $("#configurationError").html(err)
    }
    var updateConfiguration = function () {
        $configuration = $("#configuration")
        var datacenter = $("#datacenter").val();
        if (!datacenter) {
            return setConfigurationError("Please select a datacenter");
        }
        if (!k8s) {
            var imageId = $("#image").val();
            if (!imageId) {
                return setConfigurationError("Please select an image");
            }
        }
        var cpuType = $("#cputype").val();
        if (!cpuType) {
            return setConfigurationError("Please select a CPU type");
        }
        var cpuCores = $("#cpucores").val();
        if (!cpuCores) {
            return setConfigurationError("Please select CPU cores");
        }
        var gotFirstDiskSize = false;
        var diskSizes = [];
        $("#diskscontainer").children().each(function () {
            var $this = $(this);
            var diskSize = $(this).val();
            if (diskSize) {
                if ($this.attr("id") === "disk1") gotFirstDiskSize = true;
                diskSizes.push(diskSize);
            }
        })
        if (!gotFirstDiskSize) {
            return setConfigurationError("Please select the primary disk size");
        }
        var ram = $("#ram").val();
        if (!ram) {
            return setConfigurationError("Please select RAM option");
        }
        var billing = $("#billing").val();
        if (!billing) {
            return setConfigurationError("Please select a billing option");
        }
        var netpack = $("#netpack").val();
        if (billing === "monthly" && !netpack) {
            return setConfigurationError("Please select a network traffic package");
        }
        var configformat = forceConfigFormat || $("#configformat").val();
        var c = {
            datacenter, imageId, cpuType, cpuCores, diskSizes, ram, billing, netpack
        }
        setConfigurationError("");
        $configuration.val(eval(configTemplates[configformat] ? configTemplates[configformat] : configTemplates["default"]))
    }
    var pauseStorage = true;
    var onAnyChange = function () {
        if (!pauseStorage) {
            $.each(allStorageIds, function (i, key) {
                window.localStorage.setItem(key, $("#" + key).val() || "");
            })
        }
        updateConfiguration()
    }
    var clearLocalStorage = function() {
        window.localStorage.clear();
        window.location.reload();
    }
    var setFromLocalstorage = function () {
        if (window.localStorage.getItem("datacenter")) $("#" + "datacenter").val(window.localStorage.getItem("datacenter") || "");
        if (!k8s && window.localStorage.getItem("imagecategory")) $("#" + "imagecategory").val(window.localStorage.getItem("imagecategory") || "");
        if (window.localStorage.getItem("billing")) $("#" + "billing").val(window.localStorage.getItem("billing") || "");
        updateDatacenterUi()
        if (!k8s && window.localStorage.getItem("image")) $("#" + "image").val(window.localStorage.getItem("image") || "");
        if (window.localStorage.getItem("cputype")) $("#" + "cputype").val(window.localStorage.getItem("cputype") || "");
        updateCpuTypeUi()
        if (window.localStorage.getItem("cpucores")) $("#" + "cpucores").val(window.localStorage.getItem("cpucores") || "");
        if (window.localStorage.getItem("ram")) $("#" + "ram").val(window.localStorage.getItem("ram") || "");
        if (window.localStorage.getItem("disk1")) $("#" + "disk1").val(window.localStorage.getItem("disk1") || "");
        $.each([2, 3, 4], function(i, diskNum) {
            if (window.localStorage.getItem(`disk${diskNum}`)) {
                addAdditionalDisk();
                var lastDiskNum = $("#diskscontainer").children().length;
                $(`#disk${lastDiskNum}`).val(window.localStorage.getItem(`disk${diskNum}`) || "");
            }
        })
        updateDisksUi()
        if (window.localStorage.getItem("netpack")) $("#" + "netpack").val(window.localStorage.getItem("netpack") || "");
        if (window.localStorage.getItem("configformat")) $("#" + "configformat").val(window.localStorage.getItem("configformat") || "");
    }
    var forceConfigFormat = "";
    var initUi = function () {
        $.each(datacenters, function (datacenterId, datacenter) {
            $("#datacenter").append($("<option>").attr("value", datacenterId).text(datacenter.name));
        })
        $("#datacenter").change(updateDatacenterUi);
        if (!k8s) {
            $.each(imageCategories, function (imageCategory) {
                $("#imagecategory").append($("<option>").attr("value", imageCategory).text(imageCategory));
            })
            $("#imagecategory").change(updateImagesUi)
        }
        $.each(cpuTypes, function (cpuTypeId, cpuType) {
            $("#cputype").append($("<option>").attr("value", cpuTypeId).text(cpuType.name));
        })
        $("#cputype").change(updateCpuTypeUi)
        $("#billing").change(updateBillingUi)
        $.each(diskSizesGB, function (i, diskSizeGB) {
            $("#disk1").append($("<option>").attr("value", diskSizeGB).text("" + diskSizeGB + " GB"));
        })
        $.each(configTemplates, function(configFormat) {
            if (window.location.href.indexOf("configformat=" + configFormat) !== -1) {
                forceConfigFormat = configFormat;
            }
        })
        if (forceConfigFormat !== "") {
            $("#forceConfigFormat").html(`<h4 style="color:black;">${forceConfigFormat}</h4> <a href="javascript:">Change configuration format</a>`).removeClass("invisible");
            $("#configformatcontainer").hide();
            $("#forceConfigFormat a").click(function() {
                window.location.href = window.location.href.replace("configformat=" + forceConfigFormat, "configformat=");
            })
        } else {
            $.each(configTemplates, function(configFormat) {
                if (configFormat === "default") return;
                $("#configformat").append($("<option>").attr("value", configFormat).text(configFormat));
            })
        }
        if (!k8s) {
            $("#image").change(onImageChange);
        }
        $("select").change(onAnyChange);
        $("#additionaldisk a").click(addAdditionalDisk);
        $("#clearConfigurations a").click(clearLocalStorage);
        setFromLocalstorage()
        pauseStorage = false;
        onAnyChange();
        $("#mainloader").hide();
        $("form").removeClass("invisible")
    }
    $(function() {
        $.ajax({
            url: calculator_js_php_url,
            type: "GET",
            dataType: "text",
            success: function (data) {
                initData($.parseJSON("{" + data.split("'{")[1].split("}'")[0] + "}"));
                initUi();
            }
        });
    })
}