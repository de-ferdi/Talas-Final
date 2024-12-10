# News Crawler API

API ini menyediakan beberapa endpoint untuk menjalankan crawler berita, mendapatkan berita, dan menambahkan berita ke database. Dibangun menggunakan Flask dan SQLAlchemy.

## Persyaratan

- Python 3.6 atau lebih baru
- Flask
- Flask-SQLAlchemy
- pymysql

## Instalasi

1. Clone repository ini
2. Install dependencies menggunakan pip

    ```bash
    pip install Flask Flask-SQLAlchemy pymysql
    ```

3. Pastikan MySQL server berjalan dan Anda memiliki database `pukulenam`.

## Konfigurasi

Update konfigurasi database di file `app.py` sesuai dengan kredensial MySQL Anda:

```bash
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:yourpassword@localhost/pukulenam?charset=utf8mb4'
```

## Menjalankan Aplikasi

Jalankan aplikasi dengan perintah berikut:

```bash
    python app.py
```

## Endpoint

### 1. Menjalankan Crawler General

**Endpoint:** `/api/crawler/general`  
**Method:** `GET`

**Deskripsi:** Menjalankan crawler general dan memperbarui data berita di database.

**Contoh Respons:**

 ```bash
    {
        "message": "News updated successfully from general crawler"
    }
```

### 2. Menjalankan Crawler Berdasarkan Topik

**Endpoint:** `/api/crawler/topik`  
**Method:** `POST`

**Deskripsi:** Menjalankan crawler berdasarkan topik yang diberikan dan memperbarui data berita di database.

**Body Request:**

```bash
    {
        "topik": "politics"
    }
```

**Contoh Respons:**

```bash
    {
        "message": "News updated successfully from topic crawler"
    }
```

### 3. Mendapatkan Semua Berita

**Endpoint:** `/api/news`  
**Method:** `GET`

**Deskripsi:** Mengambil semua berita yang ada di database.

**Contoh Respons:**

```bash
    [
        {
            "id": 1,
            "title": "Judul Berita",
            "link": "https://linkberita.com",
            "image": "https://linkgambar.com",
            "content": "Isi berita...",
            "date": "2024-07-22T10:00:00",
            "is_fake": 0,
            "media_bias": "neutral"
        }
    ]
```

### 4. Menambahkan Berita

**Endpoint:** `/api/news`  
**Method:** `POST`

**Deskripsi:** Menghapus semua berita yang ada di database dan menambahkan berita baru.

**Body Request:**

```bash
    [
        {
            "title": "Judul Berita",
            "link": "https://linkberita.com",
            "image": "https://linkgambar.com",
            "content": "Isi berita...",
            "is_fake": 0,
            "media_bias": "neutral"
        }
    ]
```

**Contoh Respons:**

```bash
    {
        "message": "News added successfully"
    }
```

## Model Database

Tabel `News` memiliki kolom-kolom berikut:

- `id`: Integer, primary key
- `title`: String, nullable=False
- `link`: String, nullable=False
- `image`: String, nullable=False
- `content`: Text, nullable=False
- `date`: DateTime, default=db.func.current_timestamp()
- `is_fake`: Integer, default=0
- `media_bias`: String, nullable=False
- `topik`: String, nullable=False

## Error Handling

Jika terjadi error, respons akan berisi pesan error:

```bash
    {
        "error": "Deskripsi error"
    }
```

## Catatan

- Pastikan MySQL server berjalan dan Anda memiliki database `pukulenam`.
- Update kredensial database di file `app.py` sebelum menjalankan aplikasi.