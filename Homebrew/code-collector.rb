class CodeCollector < Formula
  desc "Tool for recursively collecting code to txt file for context to any LLM"
  homepage "https://github.com/MikhailOnyanov/code-collector"
  url "https://github.com/MikhailOnyanov/code-collector/archive/refs/tags/v1.0.5.tar.gz"
  sha256 "cb7d845c06ce9f1b52c9f0100bab32e958e7ce955dfc73d4beaf63dffce532fe"
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
