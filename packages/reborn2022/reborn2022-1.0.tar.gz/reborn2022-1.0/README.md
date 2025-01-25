# Solver reCAPTCHA v2

Modul Python untuk menyelesaikan reCAPTCHA v2 secara otomatis menggunakan Selenium dan pengenalan suara. Modul ini dirancang untuk bekerja dengan tantangan audio reCAPTCHA.

## Fitur
- Mengotomatisasi interaksi dengan reCAPTCHA.
- Mendukung tantangan audio reCAPTCHA.
- Menggunakan Selenium, pydub, dan SpeechRecognition untuk menyelesaikan CAPTCHA.

## Instalasi
1. Pastikan Anda memiliki Python 3.7+ terinstal di sistem Anda.
2. Clone repositori ini:
   ```bash
   git clone https://github.com/username/repo-name.git
   ```
3. Masuk ke direktori repositori:
   ```bash
   cd repo-name
   ```
4. Instal dependensi yang diperlukan:
   ```bash
   pip install -r requirements.txt
   ```

## Penggunaan
1. Pastikan Anda memiliki driver Selenium yang sesuai dengan browser yang Anda gunakan (misalnya, ChromeDriver untuk Google Chrome).
2. Impor modul dan gunakan fungsionalitas berikut dalam kode Python Anda:
   ```python
   from solver_recaptcha import solve_recaptcha

   solve_recaptcha(url="https://example.com")
   ```
3. Fungsi `solve_recaptcha` akan membuka halaman reCAPTCHA v2 dan berinteraksi dengan tantangan audio secara otomatis untuk menyelesaikan CAPTCHA.

## Dependensi
- Selenium
- pydub
- SpeechRecognition
- webdriver-manager (untuk mengelola driver browser secara otomatis)

## Masalah yang Diketahui
- Modul ini hanya mendukung tantangan audio reCAPTCHA v2, bukan tantangan gambar.
- Penggunaan modul ini mungkin tidak sepenuhnya kompatibel dengan semua situs web atau tantangan reCAPTCHA yang lebih baru.

## Kontribusi
Jika Anda ingin berkontribusi pada pengembangan modul ini, silakan buat pull request atau buka issue untuk melaporkan masalah atau saran perbaikan.

## Lisensi
Proyek ini dilisensikan di bawah [MIT License](LICENSE).

