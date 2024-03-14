{
    inputs = {
        nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
        flake-utils.url = "github:numtide/flake-utils";
    };

    outputs = {nixpkgs, flake-utils, ... }: 
    flake-utils.lib.eachDefaultSystem (system:
    let
        pkgs = import nixpkgs {
            inherit system;
        };
        zaber-motion = pkgs.python3Packages.buildPythonPackage rec {
            pname = "zaber_motion";
            version = "5.1.1";
            src = pkgs.fetchPypi {
                inherit pname version;
                sha256 = "sha256-0zQA+3/vv/i8tOPr/jOH+xjN2wmKWXxMQ/uLdqHiwOY";
            };
            doCheck = false;
            propagatedBuildInputs = with pkgs.python3Packages; [
                setuptools
                wheel
            ];       
        };
    in rec {
        devShell = (pkgs.buildFHSUserEnv {
          name = "py_env";
          targetPkgs = pkgs: (with pkgs; [
            (python311.withPackages(ps: with ps; [
                zaber-motion
                asyncua

            ]))
            nodePackages.pyright
          ]);
          runScript = "bash";
        }).env;
    });
}
