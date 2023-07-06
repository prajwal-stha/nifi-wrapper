nifi_version="${1:?'[error] Must provide parameter for NiFi version'}"
# check nifi_version is correct format
#if [[ ! "${nifi_version}" =~ ^[[:digit:]] \.[[:digit:]] \.[[:digit:]] $ ]]; then
#    echo "NiFi Version must be in format 'x.y.z' (where x, y and z are digits)"
#    exit 1
#fi

image_tag="apache/nifi:${nifi_version}-arm64"

# check this is an arm64 machine (e.g. Mac M1/2)
arch_name="$(uname -m)"
if [ "${arch_name}" = "arm64" ]; then
    echo "Running on ARM, buildingarm64 image: ${image_tag}"
else
    echo "Not running on arm64, skipping image build"
    exit 1
fi
echo

# build from nifi source nifi-docker/dockerhub/
nifi_repo="https://github.com/apache/nifi.git"
release_tag="rel/nifi-${nifi_version}"
echo "Cloning NiFi release tag ${release_tag} from ${nifi_repo}"
if [ -d nifi ]; then
    echo "Removing existing nifi directory"
    rm -rf nifi/
fi
git clone -b "${release_tag}" --single-branch "${nifi_repo}" --depth 1

# enable buildkit
export DOCKER_BUILDKIT=1
builder_name=qemu
echo "Creating buildx builder: ${builder_name}"
docker buildx create --use --bootstrap --name="${builder_name}"

echo; echo; echo "Building image with buildx builder: ${builder_name}"
pushd nifi/nifi-docker/dockerhub
docker buildx build --platform linux/arm64 --tag "${image_tag}" --output type=docker .
popd

echo; echo; echo "Removing buildx builder: ${builder_name}"
docker buildx rm -f --builder "${builder_name}"