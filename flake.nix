{
    inputs = {
        nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
        flake-utils.url = "github:numtide/flake-utils";
    };

    outputs = {nixpkgs, flake-utils, ... }: 
    flake-utils.lib.eachSystem flake-utils.lib.allSystems (system:
    let
        pkgs = import nixpkgs {
            inherit system;
        };
        zaber-motion-bindings = pkgs.python3Packages.buildPythonPackage rec {
            pname = "zaber_motion_bindings_linux";
            version = "5.1.1";
            src = pkgs.fetchPypi {
                inherit pname version;
                sha256 = "sha256-Wub2OQDGmFfqeqQtxeaoeE+/mTVdDHSjbVc7bQkCuC8=";
            };
            doCheck = false;
            propagatedBuildInputs = with pkgs.python3Packages; [
                setuptools
                wheel
            ];       
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
                protobuf
                rx
            ];       
        };
        python-env = pkgs.python311.withPackages(ps: with ps; [
                zaber-motion
                asyncua
                zaber-motion-bindings

        ]);
        zaber-opcua = pkgs.stdenv.mkDerivation rec {
            name = "zaber-opcua";
            src = ./.;
            buildInputs = [ python-env ];
            env = pkgs.buildEnv { name = name; paths = buildInputs; };
            binScript = ''
                #!${pkgs.runtimeShell}
                ${python-env}/bin/python ${placeholder "out"}/src/main.py
            '';
            passAsFile = [ "binScript" ];
            installPhase = ''
                mkdir -p $out/bin
                cp -r ./. $out/
                cp $binScriptPath $out/bin/zaber-opcua
                chmod +x $out/bin/zaber-opcua
            '';
        };

    in rec {
        packages.default = zaber-opcua;
        devShell = (pkgs.buildFHSUserEnv {
          name = "py_env";
          targetPkgs = pkgs: (with pkgs; [
            python-env
            nodePackages.pyright
            opcua-client-gui
          ]);
          runScript = "bash";
        }).env;
    });
}
