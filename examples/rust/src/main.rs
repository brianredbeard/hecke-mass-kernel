use hecke_mass_kernel::{class_mass, hecke, BigRational};

fn main() {
    let mass = class_mass(&[4u32.into(), 6u32.into()]);
    assert_eq!(mass.to_string(), "5/12");

    let u = BigRational::from_integer((-1).into());
    let samples = [
        BigRational::from_integer(2.into()),
        BigRational::from_integer(4.into()),
    ];
    let coefficient = hecke(&u, &3u32.into(), &1u32.into(), &3u32.into(), &samples);
    assert_eq!(coefficient.to_string(), "-2");
}
