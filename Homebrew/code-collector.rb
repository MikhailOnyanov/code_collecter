class CodeCollector < Formula
  desc "Tool for recursively collecting code to txt file for context to any LLM"
  homepage "https://github.com/MikhailOnyanov/code-collector"
  url "https://github.com/MikhailOnyanov/code-collector/archive/refs/tags/v1.0.5.tar.gz"
  sha256 "537911a99b40606226b2658cb7d42b7fbdb5f946c4e9f3445edb1cb70c971e0d"
  license "MIT"

  depends_on "python@3.12"

  def install
    bin.install "collect_code.py" => "collect-code"
    chmod "+x", bin/"collect-code"
  end

  test do
    # Check the installation by running the help command
    assert_match "Usage", shell_output("#{bin}/collect-code --help")
  end
end
