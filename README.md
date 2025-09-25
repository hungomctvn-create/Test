echo "deb [arch=amd64] http://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee -a /etc/apt/sources.list.d/bazel.list
curl -fsSL https://bazel.build/bazel-release.pub.gpg | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/bazel.gpg
sudo apt update
