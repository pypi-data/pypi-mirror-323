// build.rs

fn main() {
    // Specify the exact path to your Intel MKL installation
    let mkl_lib_dir = r"C:\Program Files (x86)\Intel\oneAPI\mkl\2025.0\lib";

    // Instruct Cargo to add the MKL library directory to the library search path
    println!("cargo:rustc-link-search=native={}", mkl_lib_dir);

    // Link against the MKL runtime library
    println!("cargo:rustc-link-lib=mkl_rt");

    // Optional: If your application uses threading or other specific MKL features,
    // you might need to link against additional libraries. Uncomment if necessary.
    // println!("cargo:rustc-link-lib=omp"); // OpenMP
    // println!("cargo:rustc-link-lib=svml"); // Short Vector Math Library
    // println!("cargo:rustc-link-lib=compiler_rt"); // Compiler runtime
}
