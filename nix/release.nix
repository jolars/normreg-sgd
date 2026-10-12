{
  config,
  inputs,
  lib,
  pkgs,
  ...
}:
let
  project = (builtins.fromTOML (builtins.readFile ../pyproject.toml)).project;
  releaseName = "${project.name}-${project.version}";
  source = lib.cleanSourceWith {
    name = releaseName;
    src = ../.;
    filter =
      path: type:
      let
        relative = lib.removePrefix "${toString ../.}/" (toString path);
        parts = lib.splitString "/" relative;
        root = builtins.head parts;
      in
      builtins.elem root [
        ".github"
        ".gitignore"
        "README.md"
        "LICENSE-CODE"
        "LICENSE-PAPER"
        "REPRODUCING.md"
        "Taskfile.yml"
        "checks"
        "devenv.lock"
        "devenv.nix"
        "devenv.yaml"
        "experiments"
        "lean"
        "nix"
        "normreg"
        "panache.toml"
        "paper"
        "pyproject.toml"
        "results"
        "scripts"
        "uv.lock"
      ]
      && !(builtins.any (
        part:
        builtins.elem part [
          "__pycache__"
          ".lake"
          ".git"
          "notes"
          "reviews"
        ]
      ) parts)
      && !(builtins.elem (lib.toLower (baseNameOf path)) [
        "agents.md"
        "agents.override.md"
        "skill.md"
        "todo.md"
      ])
      && !(lib.hasSuffix ".pyc" relative)
      && !(lib.hasSuffix ".pyo" relative)
      && (
        root != "paper"
        || type == "directory"
        || relative == "paper/.latexmkrc"
        || builtins.any (suffix: lib.hasSuffix suffix relative) [
          ".tex"
          ".bib"
          ".sty"
          ".cls"
          ".md"
        ]
      );
  };

  # Code and result changes should not rebuild the locked Python dependencies.
  dependencySource = lib.fileset.toSource {
    root = ../.;
    fileset = lib.fileset.unions [
      ../pyproject.toml
      ../uv.lock
    ];
  };
  workspace = inputs.uv2nix.lib.workspace.loadWorkspace {
    workspaceRoot = dependencySource;
  };
  pythonSet =
    (pkgs.callPackage inputs.pyproject-nix.build.packages {
      python = pkgs.python313;
    }).overrideScope
      (
        lib.composeManyExtensions [
          inputs.pyproject-build-systems.overlays.default
          (workspace.mkPyprojectOverlay { sourcePreference = "wheel"; })
        ]
      );
  pythonEnvironment = pythonSet.mkVirtualEnv "${project.name}-python" workspace.deps.default;
in
{
  outputs.release = pkgs.runCommand "${releaseName}-archive" { } ''
    mkdir -p "$out"
    # Store optimization can hard-link identical files; expand them for portable extraction.
    tar --hard-dereference --sort=name --mtime=@1 --owner=0 --group=0 --numeric-owner \
      --mode=u+rwX,go+rX --transform='s,^\.,${releaseName},' \
      -czf "$out/${releaseName}.tar.gz" -C ${source} .
  '';

  packages = lib.optionals config.container.isBuilding [ (lib.hiPrio pythonEnvironment) ];

  # uv's system-only discovery skips the packaged virtual environment.
  env = lib.optionalAttrs config.container.isBuilding {
    UV_PYTHON = pkgs.python313.interpreter;
  };

  containers.experiments = {
    name = project.name;
    version = project.version;
    copyToRoot = source;
    startupCommand = [
      "task"
      "--list"
    ];
    # Preserve argument boundaries and use the built environment without shell hooks.
    entrypoint = [
      (pkgs.writeShellScript "experiment-entrypoint" ''
        export PATH="${config.devenv.profile}/bin:/bin"
        exec "$@"
      '')
    ];
  };
}
