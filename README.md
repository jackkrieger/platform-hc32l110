# HUADA HC32L110 Series development platform for [PlatformIO](https://platformio.org)

The HC32L110 Series of MCUs is a 32-bit MCU based on the ARM Cortex-M0+ processor.
It integrates up to 32 KB of Flash memory, and up to 4 KB of SRAM.


## Getting Started

to get started using the HC32L110 platform, use the following in your [`platformio.ini`](https://docs.platformio.org/page/projectconf.html) file:

current *development* version:
```ini
[env:my_env]
platform = https://github.com/jackkrieger/platform-hc32l110.git
framework = ddl
board = generic_hc32l110x4
```

latest release versions:
```ini
[env:my_env]
platform = https://github.com/jackkrieger/platform-hc32l110.git#release
platform_packages =
  framework-hc32l110-ddl @ https://github.com/jackkrieger/framework-hc32l110-ddl#release
framework = ddl
board = generic_hc32l110x4
```

## Configuration

the platform itself contains basically no configuration options.
everything is configured in the framework packages.

please refer to [framework-hc32l110-ddl](https://github.com/jackkrieger/framework-hc32l110-ddl) for more information.


## Uploading & Debugging

please refer to [HOW_TO_UPLOAD](./docs/HOW_TO_UPLOAD.md) and [HOW_TO_DEBUG](./docs/HOW_TO_DEBUG.md) for information on how to upload and debug your code on the HC32L110 platform.

## License

this project is licensed under the [GPL-3.0](./LICENSE) license.
