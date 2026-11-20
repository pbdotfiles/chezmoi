-- WirePlumber 0.4 only. 0.5 ignores main.lua.d: port to wireplumber.conf.d/*.conf when upgrading.
table.insert(alsa_monitor.rules, {
  matches = {
    {
      { "device.name", "matches", "alsa_card.usb-bestechnic_EDIFIER_M60*" },
    },
  },
  apply_properties = {
    -- Only offer the stereo PCM profile; drops the fake S/PDIF and AC3 profiles
    ["device.profile-set"] = "analog-only.conf",
    -- Do volume in PipeWire (fine-grained) instead of the M60's coarse 49-step control
    ["api.alsa.soft-mixer"] = true,
    ["device.profile"] = "output:analog-stereo",
  },
})
