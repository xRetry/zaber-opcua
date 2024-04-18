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
            overlays = [
                (self: super: {
                    python39 = super.python39.override {
                        packageOverrides = pyself: pysuper: {
                            lxml = pysuper.uvloop.overrideAttrs (_: {
                                doCheck = false;
                                src =  pysuper.fetchPypi {
                                    pname = "lxml";
                                    version = "4.9.3";
                                    sha256 = "sha256-SGKL1TpCbJ65vAZqkjrKoIeNHoYSn9U1mu6ZKF9O7Zw=";
                                };
                            });
                        };
                    };
                })
            ];
        };
        dontCheckPython = drv: drv.overridePythonAttrs (old: { doCheck = false; });
        zaber-motion-bindings = pkgs.python39Packages.buildPythonPackage rec {
            pname = "zaber_motion_bindings_linux";
            version = "5.1.1";
            src = pkgs.fetchPypi {
                inherit pname version;
                sha256 = "sha256-Wub2OQDGmFfqeqQtxeaoeE+/mTVdDHSjbVc7bQkCuC8=";
            };
            doCheck = false;
            propagatedBuildInputs = with pkgs.python39Packages; [
                setuptools
                wheel
            ];       
        };
        zaber-motion = pkgs.python39Packages.buildPythonPackage rec {
            pname = "zaber_motion";
            version = "5.1.1";
            src = pkgs.fetchPypi {
                inherit pname version;
                sha256 = "sha256-0zQA+3/vv/i8tOPr/jOH+xjN2wmKWXxMQ/uLdqHiwOY";
            };
            doCheck = false;
            propagatedBuildInputs = with pkgs.python39Packages; [
                setuptools
                wheel
                (dontCheckPython protobuf)
                rx
            ];       
        };
        python-env = pkgs.python39.withPackages(ps: with ps; [
                zaber-motion
                lxml
                asyncua
                zaber-motion-bindings
                pynput
                pip

        ]);
        zaber-opcua = pkgs.stdenv.mkDerivation rec {
            name = "zaber-opcua";
            src = ./.;
            buildInputs = [ 
                python-env 
                pkgs.libxml2
                pkgs.libxslt
            ];
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
            #libxml2
            #libxslt
            #python-env
            nodePackages.pyright
            opcua-client-gui
            (python39.withPackages(ps: with ps; [
                virtualenv
            ]))
          ]);
          runScript = "bash";
        }).env;
    });
}
