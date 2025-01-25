LANGUAGES = ['en-US', 'en-GB', 'ru-RU', 'fr-FR']
TIMEZONES = [
    "Europe/Moscow",
    "Europe/Kiev",
    "Europe/Riga",
    "Europe/Vilnius",
    "Europe/Tallinn",
    "Europe/Warsaw",
    "Europe/Bucharest",
    "Europe/Sofia",
    "Europe/Istanbul",
    "Europe/Prague",
    "Europe/Budapest",
    "Europe/Belgrade",
    "Europe/Zagreb",
    "Europe/Ljubljana",
    "Europe/Bratislava",
    "Europe/Vienna",
    "Europe/Stockholm",
    "Europe/Oslo",
    "Europe/Copenhagen"
]
PLATFORMS = {
    "WINDOWS": ['Win32', 'Win64', 'Windows'],
    "ANDROID": ['Linux armv7l', 'Linux aarch64'],
    "LINUX": ['Linux', 'Linux i686', 'Linux x86_64'],
    "IOS": ['iPhone']
}
WEBGL_VENDORS = {
    "WINDOWS": [
        "Google Inc. (AMD)",
        "Google Inc. (Intel Inc.)",
        "Google Inc. (Intel Open Source Technology Center)",
        "Google Inc. (Intel)",
        "Google Inc. (Microsoft Corporation)",
        "Google Inc. (Microsoft)",
        "Google Inc. (NVIDIA Corporation)",
    ],
    "ANDROID": [
        "Google Inc. (AMD)",
        "Google Inc. (ARM)",
        "Google Inc. (Google)",
        "Google Inc. (Intel Inc.)",
        "Google Inc. (Intel Open Source Technology Center)",
        "Google Inc. (Intel)",
        "Google Inc. (Microsoft)",
        "Google Inc. (Qualcomm)",
    ],
    "LINUX": [
        "Google Inc. (AMD)",
        "Google Inc. (Intel Inc.)",
        "Google Inc. (Intel Open Source Technology Center)",
        "Google Inc. (Intel)",
        "Google Inc. (Microsoft Corporation)",
        "Google Inc. (Microsoft)",
        "Google Inc. (NVIDIA Corporation)",
    ],
    "IOS": [
        "Apple",
        "Apple Inc.",
        "Google Inc. (Apple)"
    ]
}

WEBGL_RENDERERS = {
    "WINDOWS": [
       "ANGLE (Intel Inc., Intel(R) Iris(TM) Plus Graphics OpenGL Engine, OpenGL 4.1)",
       "ANGLE (NVIDIA, NVIDIA GeForce RTX 3090 (0x00002204) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (Intel, Intel(R) UHD Graphics 620 (0x00003EA0) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (Intel, Intel(R) HD Graphics 400 Direct3D11 vs_5_0 ps_5_0), or similar",
       "ANGLE (Intel, Intel(R) UHD Graphics 630 (0x00003E9B) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (AMD, AMD Radeon R5 340 (0x00006611) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (NVIDIA, NVIDIA GeForce RTX 2070 with Max-Q Design (0x00001F10) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (Intel, Intel(R) HD Graphics Direct3D11 vs_5_0 ps_5_0), or similar",
       "ANGLE (AMD, AMD Radeon(TM) Graphics (0x00001681) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics (0x00009A40) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Laptop GPU (0x0000249C) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (NVIDIA GeForce GTX 1080 Direct3D11 vs_5_0 ps_5_0)",
       "ANGLE (NVIDIA, NVIDIA GeForce GTX 1080 Ti (0x00001B06) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Laptop GPU (0x000024DC) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (NVIDIA, NVIDIA GeForce GTX 1650 (0x00002188) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (NVIDIA, NVIDIA GeForce RTX 3050 (0x00002507) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (NVIDIA, NVIDIA GeForce RTX 4070 (0x00002786) Direct3D11 vs_5_0 ps_5_0, D3D11)"
    ],
    "ANDROID": [
        "ANGLE (ARM, Mali-G68, OpenGL ES 3.2)",
        "ANGLE (Qualcomm, Adreno (TM) 642L, OpenGL ES 3.2)",
        "ANGLE (Qualcomm, Adreno (TM) 610, OpenGL ES 3.2)",
        "ANGLE (Qualcomm, Adreno (TM) 710, OpenGL ES 3.2)",
        "ANGLE (Qualcomm, Adreno (TM) 750, OpenGL ES 3.2)",
        "ANGLE (Qualcomm, Adreno (TM) 650, OpenGL ES 3.2)",
        "ANGLE (Qualcomm, Adreno (TM) 540, OpenGL ES 3.2)"

    ],
    "LINUX": [
        "ANGLE (Intel Inc., Intel(R) Iris(TM) Plus Graphics OpenGL Engine, OpenGL 4.1)",
       "ANGLE (NVIDIA, NVIDIA GeForce RTX 3090 (0x00002204) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (Intel, Intel(R) UHD Graphics 620 (0x00003EA0) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (Intel, Intel(R) HD Graphics 400 Direct3D11 vs_5_0 ps_5_0), or similar",
       "ANGLE (Intel, Intel(R) UHD Graphics 630 (0x00003E9B) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (AMD, AMD Radeon R5 340 (0x00006611) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (NVIDIA, NVIDIA GeForce RTX 2070 with Max-Q Design (0x00001F10) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (Intel, Intel(R) HD Graphics Direct3D11 vs_5_0 ps_5_0), or similar",
       "ANGLE (AMD, AMD Radeon(TM) Graphics (0x00001681) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics (0x00009A40) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Laptop GPU (0x0000249C) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (NVIDIA GeForce GTX 1080 Direct3D11 vs_5_0 ps_5_0)",
       "ANGLE (NVIDIA, NVIDIA GeForce GTX 1080 Ti (0x00001B06) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Laptop GPU (0x000024DC) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (NVIDIA, NVIDIA GeForce GTX 1650 (0x00002188) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (NVIDIA, NVIDIA GeForce RTX 3050 (0x00002507) Direct3D11 vs_5_0 ps_5_0, D3D11)",
       "ANGLE (NVIDIA, NVIDIA GeForce RTX 4070 (0x00002786) Direct3D11 vs_5_0 ps_5_0, D3D11)"
    ],
    "IOS": [
        "Apple GPU",
    ],
}

