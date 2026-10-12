{ config, pkgs, ... }:
{
  imports = [ ./nix/release.nix ];

  packages = with pkgs; [
    git
    go-task
    panache
    nixfmt
    ruff
    lean4
  ];

  languages.python = {
    enable = true;
    package = pkgs.python313;
    manylinux.enable = true;
    venv.enable = !config.container.isBuilding;
    uv = {
      enable = true;
      sync.enable = !config.container.isBuilding;
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
      "cm-super"
      "type1cm"
      "dvipng"
      "microtype"
      "natbib"
      "booktabs"
      "cleveref"
      "algorithm2e"
      "ifoddpage"
      "relsize"
      "placeins"
      "courier"
      "helvetic"
      "times"
      "xurl"
    ];
  };

  # Extracted releases and containers do not have a Git checkout.
  git-hooks.enable = !config.container.isBuilding && builtins.pathExists ./.git;
  git-hooks.hooks = {
    check-added-large-files = {
      enable = true;
      args = [
        "--maxkb=102400"
        "--enforce-all"
      ];
      stages = [ "pre-commit" ];
    };
    nixfmt.enable = true;
  };

  enterTest = ''
    task check
  '';
}
