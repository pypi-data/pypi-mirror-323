use pyo3::prelude::*;
use pyo3::types::PyBytes;
use grammers_crypto::aes::{ige_decrypt, ige_encrypt};
use aes::cipher::generic_array::GenericArray;
use aes::cipher::KeyInit;
use aes::Aes256;
use aes::cipher::BlockEncrypt;


#[pyfunction]
fn ige256_encrypt<'a>(py: Python<'a>, data: &[u8], key: &[u8], iv: &[u8]) -> &'a PyBytes {
    PyBytes::new(
        py, 
        ige_encrypt(
            data, 
            key.try_into().expect("Key with incorrect length"), 
            iv.try_into().expect("Iv with incorrect length")
        ).as_slice()
    )
}


#[pyfunction]
fn ige256_decrypt<'a>(py: Python<'a>, data: &[u8], key: &[u8], iv: &[u8]) -> &'a PyBytes {
    PyBytes::new(
        py, 
        ige_decrypt(
            data, 
            key.try_into().expect("Key with incorrect length"), 
            iv.try_into().expect("Iv with incorrect length")
        ).as_slice()
    )
}


#[pyfunction]
fn ctr256_encrypt<'a>(py: Python<'a>, data: &PyBytes, key: &[u8], iv: &[u8], mut state: usize) -> (&'a PyBytes, usize, &'a PyBytes) {
    let data: &[u8] = data.as_bytes();
    let mut data: Vec<u8> = data.to_vec();
    let key: &[u8; 32] = key.try_into().expect("Key with incorrect length");
    let mut iv: [u8; 16] = iv.try_into().expect("Iv with incorrect length");
    let mut chunk = GenericArray::clone_from_slice(&iv);

    let cipher = Aes256::new(GenericArray::from_slice(key));
    
    cipher.encrypt_block(&mut chunk);

    for i in 0..data.len() {

        data[i] ^= chunk[state];

        state += 1;

        if state >= 16 {
            state = 0;
        }

        if state == 0 {
            for k in (0..16).rev() {
                iv[k] = iv[k] + 1;
                if iv[k] != 0 {
                    break;
                }
            }
            chunk = GenericArray::clone_from_slice(&iv);
            cipher.encrypt_block(&mut chunk);
        }
    }
    (
        PyBytes::new(py, data.as_slice()), 
        state,
        PyBytes::new(py, &iv)
    )
}


#[pymodule]
fn tgcrypto_optimized(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(ige256_encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(ige256_decrypt, m)?)?;
    m.add_function(wrap_pyfunction!(ctr256_encrypt, m)?)?;
    Ok(())
}
