if [ -z ${TARGETPLATFORM} ]
then
    arch=$(uname -m)
    echo "Arch: "${arch}
    if [ "${arch}" == 'x86_64' ];
    then
    echo "X64 Architecture"
    curl -o /tmp/s6overlay.tar.gz -L https://github.com/just-containers/s6-overlay/releases/latest/download/s6-overlay-amd64.tar.gz
    fi
    if [ "${arch}" == 'armv7l' ];
    then
    echo "Arm architecture"
    curl -o /tmp/s6overlay.tar.gz -L https://github.com/just-containers/s6-overlay/releases/latest/download/s6-overlay-armhf.tar.gz
    fi
else
    echo "Platform: "${TARGETPLATFORM}
    if [ "${TARGETPLATFORM}" == 'linux/amd64' ];
    then
    echo "X64 Architecture"
    curl -o /tmp/s6overlay.tar.gz -L https://github.com/just-containers/s6-overlay/releases/latest/download/s6-overlay-amd64.tar.gz
    fi
    if [ "${TARGETPLATFORM}" == 'linux/arm/v6' ];
    then
    echo "Arm architecture"
    curl -o /tmp/s6overlay.tar.gz -L https://github.com/just-containers/s6-overlay/releases/latest/download/s6-overlay-armhf.tar.gz
    fi
fi