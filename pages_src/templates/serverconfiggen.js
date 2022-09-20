window.serverconfiggeninit = function (calculator_js_php_url) {
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
    window.configTemplates = {{ config_templates_json }};
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
            window.images[image.id] = {
                description: getImageDescription(image),
                originalDescriptionHtml: image.description.replace(/\n/g, "<br/>"),
                imageSizeGB: image.imageSizeGB,
                minRamMB: image.minRamMB,
                name: image.name
            };
            if (window.imageCategories[image.category] === undefined) window.imageCategories[image.category] = [];
            window.imageCategories[image.category].push(image.id);
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
        updateImagesUi();
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
        var imageId = $("#image").val();
        if (!imageId) {
            return setConfigurationError("Please select an image");
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
        var configformat = $("#configformat").val();
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
    var setFromLocalstorage = function () {
        if (window.localStorage.getItem("datacenter")) $("#" + "datacenter").val(window.localStorage.getItem("datacenter") || "");
        if (window.localStorage.getItem("imagecategory")) $("#" + "imagecategory").val(window.localStorage.getItem("imagecategory") || "");
        if (window.localStorage.getItem("billing")) $("#" + "billing").val(window.localStorage.getItem("billing") || "");
        updateDatacenterUi()
        if (window.localStorage.getItem("image")) $("#" + "image").val(window.localStorage.getItem("image") || "");
        if (window.localStorage.getItem("cputype")) $("#" + "cputype").val(window.localStorage.getItem("cputype") || "");
        updateCpuTypeUi()
        if (window.localStorage.getItem("cpucores")) $("#" + "cpucores").val(window.localStorage.getItem("cpucores") || "");
        if (window.localStorage.getItem("ram")) $("#" + "ram").val(window.localStorage.getItem("ram") || "");
        if (window.localStorage.getItem("disk1")) $("#" + "disk1").val(window.localStorage.getItem("disk1") || "");
        updateDisksUi()
        if (window.localStorage.getItem("netpack")) $("#" + "netpack").val(window.localStorage.getItem("netpack") || "");
        if (window.localStorage.getItem("configformat")) $("#" + "configformat").val(window.localStorage.getItem("configformat") || "");
    }
    var initUi = function () {
        $.each(datacenters, function (datacenterId, datacenter) {
            $("#datacenter").append($("<option>").attr("value", datacenterId).text(datacenter.name));
        })
        $("#datacenter").change(updateDatacenterUi);
        $.each(imageCategories, function (imageCategory) {
            $("#imagecategory").append($("<option>").attr("value", imageCategory).text(imageCategory));
        })
        $("#imagecategory").change(updateImagesUi)
        $.each(cpuTypes, function (cpuTypeId, cpuType) {
            $("#cputype").append($("<option>").attr("value", cpuTypeId).text(cpuType.name));
        })
        $("#cputype").change(updateCpuTypeUi)
        $("#billing").change(updateBillingUi)
        $.each(diskSizesGB, function (i, diskSizeGB) {
            $("#disk1").append($("<option>").attr("value", diskSizeGB).text("" + diskSizeGB + " GB"));
        })
        $("#image").change(onImageChange);
        $("select").change(onAnyChange);
        $("#additionaldisk a").click(addAdditionalDisk);
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