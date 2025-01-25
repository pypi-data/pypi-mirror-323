{
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-24.11";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = {...} @ inputs:
    inputs.utils.lib.eachDefaultSystem (system: let
      pkgs = import inputs.nixpkgs {inherit system;};

      vermin = pkgs.python3Packages.buildPythonPackage rec {
        pname = "vermin";
        version = "1.6.0";
        src = pkgs.fetchPypi {
          inherit pname version;
          hash = "sha256-YmbKAvVdHCqhiaYQAXwTLrLRk08J5yqVWx6zgg7m1O8=";
        };
      };
    in {
      devShell = pkgs.mkShell {
        packages = with pkgs; [(python3.withPackages (ps: with ps; [ruff pytest pytest-cov flit vermin]))];
      };

      formatter = pkgs.alejandra;
    });
}
