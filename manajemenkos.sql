-- 1. Membuat Database
CREATE DATABASE IF NOT EXISTS `db_manajemenkos`;
USE `db_manajemenkos`;

-- --------------------------------------------------------
-- 2. Tabel `user`
CREATE TABLE IF NOT EXISTS `user` (
  `id_user` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `hak_akses` enum('admin','pemilik') NOT NULL,
  `akses_terakhir` datetime DEFAULT NULL,
  PRIMARY KEY (`id_user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `user` (`username`, `password`, `hak_akses`) VALUES
('admin', '123', 'admin'),
('pemilik', '123', 'pemilik');

-- --------------------------------------------------------
-- 3. Tabel `data_kamar`
CREATE TABLE IF NOT EXISTS `data_kamar` (
  `id_kamar` int(11) NOT NULL AUTO_INCREMENT,
  `nomor_kamar` varchar(10) NOT NULL,
  `tipe_kamar` enum('AC','Non-AC') NOT NULL,
  `lantai` int(11) NOT NULL,
  `fasilitas` text,
  `harga_per_bulan` decimal(15,2) NOT NULL,
  `status_huni` enum('Kosong','Terisi') DEFAULT 'Kosong',
  PRIMARY KEY (`id_kamar`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `data_kamar` (`nomor_kamar`, `tipe_kamar`, `lantai`, `fasilitas`, `harga_per_bulan`, `status_huni`) VALUES
('101', 'AC', 1, 'Kasur, Lemari, TV, Kamar Mandi Dalam', 1500000.00, 'Terisi'),
('102', 'Non-AC', 1, 'Kasur, Lemari', 800000.00, 'Terisi'),
('201', 'AC', 2, 'Kasur, Lemari, TV, WiFi', 1600000.00, 'Terisi');

-- --------------------------------------------------------
-- 4. Tabel `data_penghuni`
CREATE TABLE IF NOT EXISTS `data_penghuni` (
  `id_penghuni` int(11) NOT NULL AUTO_INCREMENT,
  `nama` varchar(100) NOT NULL,
  `pekerjaan` varchar(50) DEFAULT NULL,
  `no_hp` varchar(20) DEFAULT NULL,
  `alamat_asal` text,
  `kontak_darurat` varchar(20) DEFAULT NULL,
  `tanggal_masuk` date DEFAULT NULL,
  PRIMARY KEY (`id_penghuni`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `data_penghuni` (`nama`, `pekerjaan`, `no_hp`, `alamat_asal`, `kontak_darurat`, `tanggal_masuk`) VALUES
('Budi Santoso', 'Karyawan Swasta', '081234567890', 'Bandung', '081299998888', '2026-01-01'),
('Siti Aminah', 'Mahasiswa', '085566778899', 'Jakarta', '085511223344', '2026-01-05'),
('Andi Wijaya', 'Freelancer', '081122334455', 'Surabaya', '081155443322', '2026-01-10');

-- --------------------------------------------------------
-- 5. Tabel `tagihan_bulanan` (Data 2026 untuk AI)
CREATE TABLE IF NOT EXISTS `tagihan_bulanan` (
  `id_tagihan` int(11) NOT NULL AUTO_INCREMENT,
  `id_kamar` int(11) NOT NULL,
  `id_penghuni` int(11) NOT NULL,
  `bulan_tagihan` int(2) NOT NULL,
  `tahun_tagihan` int(4) NOT NULL,
  `biaya_sewa` decimal(15,2) NOT NULL,
  `biaya_listrik` decimal(15,2) NOT NULL,
  `biaya_air` decimal(15,2) NOT NULL,
  `biaya_sampah` decimal(15,2) NOT NULL,
  `total_tagihan` decimal(15,2) NOT NULL,
  `status_lunas` enum('Lunas','Belum Lunas') DEFAULT 'Belum Lunas',
  PRIMARY KEY (`id_tagihan`),
  CONSTRAINT `fk_kamar` FOREIGN KEY (`id_kamar`) REFERENCES `data_kamar` (`id_kamar`) ON DELETE CASCADE,
  CONSTRAINT `fk_penghuni` FOREIGN KEY (`id_penghuni`) REFERENCES `data_penghuni` (`id_penghuni`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Input Data Tagihan Berkelanjutan Tahun 2026
-- Pola biaya_listrik dibuat meningkat agar AI Linear Regression bisa mendeteksi tren
INSERT INTO `tagihan_bulanan` 
(`id_kamar`, `id_penghuni`, `bulan_tagihan`, `tahun_tagihan`, `biaya_sewa`, `biaya_listrik`, `biaya_air`, `biaya_sampah`, `total_tagihan`, `status_lunas`) VALUES
-- Kamar 1 (Budi)
(1, 1, 1, 2026, 1500000, 140000, 50000, 20000, 1710000, 'Lunas'),
(1, 1, 2, 2026, 1500000, 155000, 52000, 20000, 1727000, 'Lunas'),
(1, 1, 3, 2026, 1500000, 168000, 50000, 20000, 1738000, 'Lunas'),
(1, 1, 4, 2026, 1500000, 175000, 55000, 20000, 1750000, 'Lunas'),
(1, 1, 5, 2026, 1500000, 185000, 53000, 20000, 1758000, 'Belum Lunas'),

-- Kamar 2 (Siti)
(2, 2, 1, 2026, 800000, 50000, 30000, 20000, 900000, 'Lunas'),
(2, 2, 2, 2026, 800000, 55000, 32000, 20000, 907000, 'Lunas'),
(2, 2, 3, 2026, 800000, 62000, 30000, 20000, 912000, 'Lunas'),
(2, 2, 4, 2026, 800000, 68000, 35000, 20000, 923000, 'Belum Lunas'),

-- Kamar 3 (Andi)
(3, 3, 1, 2026, 1600000, 120000, 45000, 20000, 1785000, 'Lunas'),
(3, 3, 2, 2026, 1600000, 135000, 48000, 20000, 1803000, 'Lunas'),
(3, 3, 3, 2026, 1600000, 145000, 46000, 20000, 1811000, 'Lunas'),
(3, 3, 4, 2026, 1600000, 160000, 50000, 20000, 1830000, 'Lunas');

COMMIT;