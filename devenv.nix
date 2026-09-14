{ pkgs, ... }:
{
  packages = with pkgs; [
    git
    gnumake
    panache
    nixfmt
    actionlint
    ruff
  ];

  languages.python = {
    enable = true;
    package = pkgs.python313;
    manylinux.enable = true;
    venv.enable = true;
    uv = {
      enable = true;
      sync.enable = true;
      # Ruff's wheel binary lacks a NixOS loader; use the Nix package instead.
      sync.arguments = [ "--no-dev" ];
    };
  };

  languages.texlive = {
    enable = true;
    packages = [
      "scheme-small"
      "latexmk"
      "lm"
      "microtype"
      "natbib"
      "booktabs"
    ];
  };

  git-hooks.hooks = {
    nixfmt.enable = true;
    actionlint.enable = true;
    panache-format = {
      enable = true;
      name = "Check Markdown formatting";
      entry = "panache format --check --force-exclude";
      files = "\\.md$";
    };
    panache-lint = {
      enable = true;
      name = "Lint Markdown";
      entry = "panache lint --force-exclude";
      files = "\\.md$";
    };
    python = {
      enable = true;
      name = "Check experiment formatting and lint";
      entry = "make check-python";
      files = "^(experiments/.*\\.py|pyproject\\.toml)$";
      pass_filenames = false;
    };
  };

  enterTest = ''
    make check
  '';
}
