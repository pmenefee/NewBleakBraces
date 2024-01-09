{pkgs}: {
  deps = [
    pkgs.bash
    pkgs.go-migrate
    pkgs.openssl
    pkgs.postgresql
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.bash
      pkgs.postgresql
    ];
  };
}