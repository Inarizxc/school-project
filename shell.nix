{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
	nativeBuildInputs = with pkgs; [
		# Packages
		git
		python313
		git
		gitui

		# Libraries
		python313Packages.matplotlib
		python313Packages.pandas
		python313Packages.tkinter
	];
	shellHook = ''
		echo ""
		echo "School Project Env"
		echo ""
		git --version
		python --version
	'';
}
