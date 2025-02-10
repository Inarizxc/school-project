{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    pkgs = nixpkgs.legacyPackages."x86_64-linux";
  in {
    devShells."x86_64-linux".default = pkgs.mkShell {
      packages = with pkgs; [
        # Packages
        python313

        # Libraries
        python313Packages.matplotlib
        python313Packages.pandas
        python313Packages.tkinter
        python313Packages.openpyxl

        # python313Packages.pyinstaller
        # python311Packages.nuitka
      ];

      shellHook = ''
        echo ""
        echo "School Project Env"
        echo ""
        git --version
        python --version
      '';
    };
  };
}
