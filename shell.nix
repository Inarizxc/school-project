{pkgs ? import <nixpkgs> {}}:
pkgs.mkShell {
  nativeBuildInputs = with pkgs; [
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
}
